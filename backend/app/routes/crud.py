"""CRUD endpoints for the five data types.  (Ticket 6)

URL pattern (same for every resource):
    GET    /api/<resource>          list all
    POST   /api/<resource>          create one
    GET    /api/<resource>/<id>     read one
    PUT    /api/<resource>/<id>     update one
    DELETE /api/<resource>/<id>     delete one

Resources: lecturers, courses, rooms, student-groups, time-slots
All of them are admin-only (@role_required("admin")).

Extra: GET/PUT /api/courses/<id>/groups  (reads and writes course_groups)
"""
import sqlite3

from flask import Blueprint, abort, jsonify, request

from ..auth import role_required
from ..db import get_db

bp = Blueprint("crud", __name__, url_prefix="/api")

# resource URL name -> table name
RESOURCES = {
    "lecturers": "lecturers",
    "courses": "courses",
    "rooms": "rooms",
    "student-groups": "student_groups",
    "time-slots": "time_slots",
}

# ---- Values taken from docs/database-schema.md ---------------------------
# Allowed values for rooms.room_type and courses.preferred_room_type
VALID_ROOM_TYPES = {"lecture", "lab", "auditorium"}
# Numeric columns that must be a positive whole number if supplied
POSITIVE_INT_FIELDS = {
    "capacity", "size", "year_level", "weekly_hours", "block_hours",
}
# --------------------------------------------------------------------------


# ---------------------------------------------------------------- helpers --
def _table_for(resource):
    """Return the table name for a URL resource or abort with 404."""
    table = RESOURCES.get(resource)
    if table is None:
        abort(404, f"Unknown resource: {resource}")
    return table


def _writable_columns(table):
    """Columns we accept from the client (everything except the primary key).

    Read from the database itself so this works for all five tables."""
    info = get_db().execute(f"PRAGMA table_info({table})").fetchall()
    return {c["name"]: c for c in info if not c["pk"]}


def _fetch_one(table, item_id):
    return get_db().execute(
        f"SELECT * FROM {table} WHERE id = ?", (item_id,)
    ).fetchone()


def _get_or_404(table, resource, item_id):
    row = _fetch_one(table, item_id)
    if row is None:
        abort(404, f"{resource}/{item_id} not found")
    return row


def _clean_body(table):
    """Read and validate the JSON body. Returns a dict of column -> value."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        abort(400, "Request body must be a non-empty JSON object")

    columns = _writable_columns(table)

    unknown = [key for key in data if key not in columns]
    if unknown:
        abort(400, f"Unknown field(s): {', '.join(unknown)}")

    # trim whitespace on strings
    data = {k: (v.strip() if isinstance(v, str) else v) for k, v in data.items()}

    # required = NOT NULL and no default value in the schema
    missing = [
        name
        for name, col in columns.items()
        if col["notnull"] and col["dflt_value"] is None
        and data.get(name) in (None, "")
    ]
    if missing:
        abort(400, f"Missing required field(s): {', '.join(missing)}")

    for field in POSITIVE_INT_FIELDS & data.keys():
        value = data[field]
        if value is None:  # nullable column; NOT NULL was checked above
            continue
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            abort(400, f"'{field}' must be a positive whole number")

    allowed = ", ".join(sorted(VALID_ROOM_TYPES))
    for field in ("room_type", "preferred_room_type"):
        if data.get(field) is not None and data[field] not in VALID_ROOM_TYPES:
            abort(400, f"'{field}' must be one of: {allowed}")

    if table == "time_slots" and "day_of_week" in data:
        day = data["day_of_week"]
        if isinstance(day, bool) or not isinstance(day, int) or not 1 <= day <= 5:
            abort(400, "'day_of_week' must be a whole number from 1 (Mon) to 5 (Fri)")

    return data


def _integrity_message(exc, action):
    """Turn a raw SQLite IntegrityError into a readable 409 message."""
    text = str(exc)
    if text.startswith("UNIQUE constraint failed:"):
        cols = text.split(":", 1)[1].split(",")
        names = ", ".join(c.strip().split(".")[-1] for c in cols)
        return f"Cannot {action}: a record with the same {names} already exists."
    if text.startswith("FOREIGN KEY constraint failed"):
        return f"Cannot {action}: it refers to a record that does not exist."
    return f"Cannot {action}: {text}"


# ----------------------------------------------------------------- routes --
@bp.get("/<resource>")
@role_required("admin")
def list_items(resource):
    table = _table_for(resource)
    rows = get_db().execute(f"SELECT * FROM {table}").fetchall()
    return jsonify([dict(row) for row in rows])


@bp.post("/<resource>")
@role_required("admin")
def create_item(resource):
    table = _table_for(resource)
    data = _clean_body(table)

    names = list(data)
    placeholders = ", ".join("?" for _ in names)
    db = get_db()
    try:
        cur = db.execute(
            f"INSERT INTO {table} ({', '.join(names)}) VALUES ({placeholders})",
            [data[n] for n in names],
        )
        db.commit()
    except sqlite3.IntegrityError as exc:
        db.rollback()
        abort(409, _integrity_message(exc, f"create {resource}"))

    row = _fetch_one(table, cur.lastrowid)
    return jsonify(dict(row)), 201


@bp.get("/<resource>/<int:item_id>")
@role_required("admin")
def get_item(resource, item_id):
    table = _table_for(resource)
    row = _get_or_404(table, resource, item_id)
    return jsonify(dict(row))


@bp.put("/<resource>/<int:item_id>")
@role_required("admin")
def update_item(resource, item_id):
    table = _table_for(resource)
    _get_or_404(table, resource, item_id)
    data = _clean_body(table)

    assignments = ", ".join(f"{name} = ?" for name in data)
    db = get_db()
    try:
        db.execute(
            f"UPDATE {table} SET {assignments} WHERE id = ?",
            [*data.values(), item_id],
        )
        db.commit()
    except sqlite3.IntegrityError as exc:
        db.rollback()
        abort(409, _integrity_message(exc, f"update {resource}/{item_id}"))

    return jsonify(dict(_fetch_one(table, item_id)))


@bp.delete("/<resource>/<int:item_id>")
@role_required("admin")
def delete_item(resource, item_id):
    table = _table_for(resource)
    _get_or_404(table, resource, item_id)

    db = get_db()
    try:
        db.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        abort(
            409,
            f"Cannot delete {resource}/{item_id}: other records still depend on it "
            "(for example, a lecturer who still has courses, or a room or course "
            "used in a timetable). "
            "Remove or reassign those first.",
        )

    return "", 204


# ------------------------------------------------------- course <-> groups --
@bp.get("/courses/<int:item_id>/groups")
@role_required("admin")
def get_course_groups(item_id):
    _get_or_404("courses", "courses", item_id)
    rows = get_db().execute(
        "SELECT group_id FROM course_groups WHERE course_id = ? ORDER BY group_id",
        (item_id,),
    ).fetchall()
    return jsonify({"course_id": item_id, "group_ids": [r["group_id"] for r in rows]})


@bp.put("/courses/<int:item_id>/groups")
@role_required("admin")
def set_course_groups(item_id):
    """Replace the course's groups. Body: {"group_ids": [1, 2, 3]}"""
    _get_or_404("courses", "courses", item_id)

    body = request.get_json(silent=True)
    group_ids = body.get("group_ids") if isinstance(body, dict) else body
    if not isinstance(group_ids, list) or any(
        isinstance(g, bool) or not isinstance(g, int) for g in group_ids
    ):
        abort(400, 'Body must be {"group_ids": [<int>, ...]}')
    group_ids = sorted(set(group_ids))

    db = get_db()
    try:
        db.execute("DELETE FROM course_groups WHERE course_id = ?", (item_id,))
        db.executemany(
            "INSERT INTO course_groups (course_id, group_id) VALUES (?, ?)",
            [(item_id, g) for g in group_ids],
        )
        db.commit()
    except sqlite3.IntegrityError as exc:
        db.rollback()  # restores the old groups if any new id is invalid
        abort(409, _integrity_message(exc, f"update groups for course {item_id}"))

    return jsonify({"course_id": item_id, "group_ids": group_ids})