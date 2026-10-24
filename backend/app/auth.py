"""Authentication and roles.  TODO (Ticket 5)

Roles: 'admin', 'lecturer', 'student'  (stored in users.role).
A lecturer user has users.lecturer_id set; a student user has users.group_id set.
That link is how "my timetable" works in Ticket 4.
"""
from functools import wraps

from flask import Blueprint, abort

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/login")
def login():
    # TODO (Ticket 5):
    #   1. read username + password from the JSON body
    #   2. look the user up in `users` (is_active = 1)
    #   3. check with werkzeug.security.check_password_hash(row["password_hash"], password)
    #   4. start a session (or return a JWT) containing user id and role
    #   5. return {"id", "username", "role"}; wrong credentials -> 401 with a generic message
    abort(501, "TODO Ticket 5: login")


@bp.post("/logout")
def logout():
    # TODO (Ticket 5): clear the session / invalidate the token.
    abort(501, "TODO Ticket 5: logout")


@bp.get("/me")
def me():
    # TODO (Ticket 5): return the current user (id, username, role, lecturer_id, group_id),
    #                  or 401 if nobody is logged in. The frontend calls this on every page load.
    abort(501, "TODO Ticket 5: me")


def login_required(view):
    """Reject anonymous requests with 401."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        # TODO (Ticket 5): return 401 if there is no logged-in user, else call the view.
        abort(501, "TODO Ticket 5: login_required")
    return wrapped


def role_required(*roles):
    """Reject users whose role is not in `roles` (401 if anonymous, 403 if wrong role)."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            # TODO (Ticket 5): check the current user's role against `roles`, then call the view.
            abort(501, "TODO Ticket 5: role_required")
        return wrapped
    return decorator
