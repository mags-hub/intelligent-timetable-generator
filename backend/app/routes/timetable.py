"""Generate, preview, publish and fetch timetables.  (Ticket 6)

Flow:  admin POSTs /generate  ->  a *draft* timetable is created by scheduling/
       admin reviews or edits it  ->  admin POSTs /<id>/publish  ->  users can fetch it.
"""
import sqlite3

from flask import Blueprint, abort, current_app, jsonify, request, session

from ..auth import login_required, role_required
from ..db import get_db


bp = Blueprint("timetable", __name__, url_prefix="/api/timetables")


# ---------------------------------------------------------------- helpers --
def _current_user():
    """The signed-in user's row (id, username, role, lecturer_id, group_id), or None.

    NOTE for Ticket 5: this assumes the login stores the user's id in the Flask session
    under "user_id". If Ticket 5 stores it differently (JWT, g.user, a different key),
    change this ONE function and nothing else in this file needs to move.
   """
    
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return get_db().execute(
        "SELECT id, username, role, lecturer_id, group_id "
        "FROM users WHERE id = ? AND is_active = 1",
        (user_id,),
    ).fetchone()


def _json_body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        abort(400, "Request body must be a JSON object")
    return data


def _positive_int(data, field):
    value = data.get(field)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        abort(400, f"'{field}' must be a positive whole number")
    return value


def _entries(timetable_id, extra_sql="", extra_params=()):
    """All rows of one timetable from the v_timetable_full view.

    extra_sql is built by this file only (never from user input) to filter further."""
    rows = get_db().execute(
        "SELECT * FROM v_timetable_full WHERE entry_id IN "
        "(SELECT id FROM timetable_entries WHERE timetable_id = ?)"
        + extra_sql
        + " ORDER BY day_of_week, start_time",
        (timetable_id, *extra_params),
    ).fetchall()
    return [dict(r) for r in rows]


def _clash_reason(exc):
    """Turn a database IntegrityError into a sentence an admin can act on."""
    text = str(exc)
    if "UNIQUE constraint failed" in text:
        if "room_id" in text:
            return "Clash: that room is already used by another class in that time slot."
        if "lecturer_id" in text:
            return "Clash: that lecturer already has a class in that time slot."
        if "group_id" in text:
            return "Clash: a student group in this class already has a class in that time slot."
    if "FOREIGN KEY constraint failed" in text:
        return "The room or time slot does not exist."
    # database triggers (lunch break, room too small, ...) already carry a readable message
    return f"Clash: {text}"


# ----------------------------------------------------------------- routes --
@bp.post("/generate")
@role_required("admin")
def generate():
    data = _json_body()
    semester = _positive_int(data, "semester")
    year = _positive_int(data, "academic_year")
    name = str(data.get("name") or f"Semester {semester} {year} draft").strip()

    # imported here, as the team agreed, so the app starts even if scheduling/ has a problem
    from scheduling.generate import generate_timetable

    result = generate_timetable(
        current_app.config["DATABASE"], name=name, semester=semester, academic_year=year
    )
    if not result.feasible:
        abort(422, result.message)

    return jsonify({
        "timetable_id": result.timetable_id,
        "status": "draft",
        "score": result.score,
    }), 201

@bp.get("")
@role_required("admin")
def list_timetables():
    rows = get_db().execute(
        "SELECT id, name, semester, academic_year, status, created_at "
        "FROM timetables ORDER BY id DESC"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@bp.get("/<int:timetable_id>")
@login_required
def get_timetable(timetable_id):
    user = _current_user()
    if user is None:
        abort(401, "Not signed in")

    tt = get_db().execute(
        "SELECT * FROM timetables WHERE id = ?", (timetable_id,)
    ).fetchone()
    # lecturers and students must not even learn that a draft exists
    if tt is None or (user["role"] != "admin" and tt["status"] != "published"):
        abort(404, f"timetables/{timetable_id} not found")

    return jsonify({
        "id": tt["id"],
        "name": tt["name"],
        "semester": tt["semester"],
        "academic_year": tt["academic_year"],
        "status": tt["status"],
        "entries": _entries(timetable_id),
    })


@bp.put("/<int:timetable_id>/entries/<int:entry_id>")
@role_required("admin")
def edit_entry(timetable_id, entry_id):
    db = get_db()
    entry = db.execute(
        "SELECT * FROM timetable_entries WHERE id = ? AND timetable_id = ?",
        (entry_id, timetable_id),
    ).fetchone()
    if entry is None:
        abort(404, f"entry {entry_id} not found in timetable {timetable_id}")

    data = _json_body()
    unknown = set(data) - {"room_id", "time_slot_id"}
    if unknown:
        abort(400, f"Unknown field(s): {', '.join(sorted(unknown))}")
    if not data:
        abort(400, "Send room_id and/or time_slot_id")

    room_id = _positive_int(data, "room_id") if "room_id" in data else entry["room_id"]
    slot_id = (
        _positive_int(data, "time_slot_id") if "time_slot_id" in data else entry["time_slot_id"]
    )

    try:
        # The group links store the slot too (composite foreign key), so the entry and its
        # group rows must change together; check the keys at commit, not row by row.
        db.execute("PRAGMA defer_foreign_keys = ON")
        db.execute(
            "UPDATE timetable_entries SET room_id = ?, time_slot_id = ?, is_locked = 1 "
            "WHERE id = ?",
            (room_id, slot_id, entry_id),
        )
        db.execute(
            "UPDATE timetable_entry_groups SET time_slot_id = ? WHERE entry_id = ?",
            (slot_id, entry_id),
        )
        db.commit()
    except sqlite3.IntegrityError as exc:
        db.rollback()
        abort(409, _clash_reason(exc))

    rows = db.execute(
        "SELECT * FROM v_timetable_full WHERE entry_id = ?", (entry_id,)
    ).fetchall()
    return jsonify({"entry_id": entry_id, "is_locked": 1, "rows": [dict(r) for r in rows]})


@bp.post("/<int:timetable_id>/publish")
@role_required("admin")
def publish(timetable_id):
    db = get_db()
    tt = db.execute("SELECT * FROM timetables WHERE id = ?", (timetable_id,)).fetchone()
    if tt is None:
        abort(404, f"timetables/{timetable_id} not found")
    if tt["status"] == "published":
        return jsonify(dict(tt))  # already published: nothing to do
    if tt["status"] != "draft":
        abort(409, "Only a draft timetable can be published")

    try:
        # only one published timetable per semester/year: archive the old one first
        db.execute(
            "UPDATE timetables SET status = 'archived' "
            "WHERE semester = ? AND academic_year = ? AND status = 'published'",
            (tt["semester"], tt["academic_year"]),
        )
        db.execute(
            "UPDATE timetables SET status = 'published', published_at = datetime('now') "
            "WHERE id = ?",
            (timetable_id,),
        )
        db.commit()
    except sqlite3.IntegrityError as exc:
        db.rollback()
        abort(409, _clash_reason(exc))

    row = db.execute("SELECT * FROM timetables WHERE id = ?", (timetable_id,)).fetchone()
    return jsonify(dict(row))


@bp.get("/published/mine")
@login_required
def my_timetable():

    user = _current_user()
    if user is None:
        abort(401, "Not signed in")

    tt = get_db().execute(
        "SELECT * FROM timetables WHERE status = 'published' "
        "ORDER BY academic_year DESC, semester DESC LIMIT 1"
    ).fetchone()
    if tt is None:
        # Ticket 4's "no timetable yet" screen relies on this exact shape
        return jsonify({"published": False, "entries": []})

    if user["role"] == "lecturer":
        entries = _entries(
            tt["id"],
            " AND entry_id IN (SELECT id FROM timetable_entries WHERE lecturer_id = ?)",
            (user["lecturer_id"],),
        )
    elif user["role"] == "student":
        entries = _entries(tt["id"], " AND group_id = ?", (user["group_id"],))
    else:  # admin sees the whole published timetable
        entries = _entries(tt["id"])

    return jsonify({
        "published": True,
        "timetable_id": tt["id"],
        "name": tt["name"],
        "entries": entries,
    })

   