"""Generate, preview, publish and fetch timetables.  TODO (Ticket 6)

Flow:  admin POSTs /generate  ->  a *draft* timetable is created by scheduling/
       admin reviews or edits it  ->  admin POSTs /<id>/publish  ->  users can fetch it.
"""
from flask import Blueprint, abort

from ..auth import login_required, role_required  # noqa: F401

bp = Blueprint("timetable", __name__, url_prefix="/api/timetables")


@bp.post("/generate")
def generate():
    # TODO (Ticket 6), admin only:
    #   from scheduling.generate import generate_timetable     (import INSIDE the function)
    #   timetable_id = generate_timetable(current_app.config["DATABASE"], name=..., semester=..., year=...)
    #   return 201 {"timetable_id": ..., "status": "draft", "score": ...}
    #   If the solver reports infeasibility, return 422 with the reason.
    abort(501, "TODO Ticket 6: generate")


@bp.get("")
def list_timetables():
    # TODO (Ticket 6), admin only: list drafts and published timetables (id, name, status, created_at).
    abort(501, "TODO Ticket 6: list timetables")


@bp.get("/<int:timetable_id>")
def get_timetable(timetable_id):
    # TODO (Ticket 6): all entries of one timetable from the v_timetable_full view.
    #   Admin can read any status; lecturer/student only 'published'.
    abort(501, "TODO Ticket 6: get timetable")


@bp.put("/<int:timetable_id>/entries/<int:entry_id>")
def edit_entry(timetable_id, entry_id):
    # TODO (Ticket 6), admin only: manual override of one entry (new room or slot).
    #   Set is_locked = 1 so regeneration does not move it. A clash makes the database raise
    #   IntegrityError -> return 409 with the reason. This powers the admin edit screen.
    abort(501, "TODO Ticket 6: edit entry")


@bp.post("/<int:timetable_id>/publish")
def publish(timetable_id):
    # TODO (Ticket 6), admin only: set status = 'published' and published_at = now.
    #   Only one published timetable per semester/year is allowed (database enforces it);
    #   archive the previous one first.
    abort(501, "TODO Ticket 6: publish")


@bp.get("/published/mine")
def my_timetable():
    # TODO (Ticket 6), login required: the published timetable filtered for the current user.
    #   lecturer -> rows where lecturer_id = user.lecturer_id
    #   student  -> rows where group_id    = user.group_id
    #   Return an empty list plus {"published": false} when nothing is published yet
    #   (Ticket 4's "no timetable yet" screen depends on this).
    abort(501, "TODO Ticket 6: my timetable")
