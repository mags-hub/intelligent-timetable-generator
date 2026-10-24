"""CRUD endpoints for the five data types.  TODO (Ticket 6)

URL pattern (same for every resource):
    GET    /api/<resource>          list all
    POST   /api/<resource>          create one
    GET    /api/<resource>/<id>     read one
    PUT    /api/<resource>/<id>     update one
    DELETE /api/<resource>/<id>     delete one

Resources: lecturers, courses, rooms, student-groups, time-slots
All of them are admin-only (use @role_required("admin") once Ticket 5 exists).
"""
from flask import Blueprint, abort

from ..auth import role_required  # noqa: F401  (use it on every route below)

bp = Blueprint("crud", __name__, url_prefix="/api")

# resource URL name -> table name
RESOURCES = {
    "lecturers": "lecturers",
    "courses": "courses",
    "rooms": "rooms",
    "student-groups": "student_groups",
    "time-slots": "time_slots",
}


def _todo(action: str):
    abort(501, f"TODO Ticket 6: {action}")


@bp.get("/<resource>")
def list_items(resource):
    # TODO (Ticket 6): 404 if `resource` is not in RESOURCES; SELECT * from the table; return a list.
    _todo(f"list {resource}")


@bp.post("/<resource>")
def create_item(resource):
    # TODO (Ticket 6): validate the JSON body, INSERT, return 201 + the new row.
    #   Validation ideas: required fields, positive capacity/size, valid room_type.
    #   Catch sqlite3.IntegrityError -> 409 (e.g. duplicate course code).
    _todo(f"create {resource}")


@bp.get("/<resource>/<int:item_id>")
def get_item(resource, item_id):
    # TODO (Ticket 6): SELECT one row; 404 if missing.
    _todo(f"get {resource}/{item_id}")


@bp.put("/<resource>/<int:item_id>")
def update_item(resource, item_id):
    # TODO (Ticket 6): validate, UPDATE, return the row; 404 if missing.
    _todo(f"update {resource}/{item_id}")


@bp.delete("/<resource>/<int:item_id>")
def delete_item(resource, item_id):
    # TODO (Ticket 6): DELETE. Deleting a lecturer who still has courses is blocked by the
    #                  database (ON DELETE RESTRICT); return 409 with a readable message.
    _todo(f"delete {resource}/{item_id}")


# TODO (Ticket 6): courses also need their groups: GET/PUT /api/courses/<id>/groups
#                  (reads and writes the course_groups table).
