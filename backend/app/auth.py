"""Authentication and roles.  (Ticket 5)

Roles: 'admin', 'lecturer', 'student'  (stored in users.role).
A lecturer user has users.lecturer_id set; a student user has users.group_id set.
That link is how "my timetable" works in Ticket 4.

How it works:
  * login checks the password hash, then stores ONLY the user's id in a signed session cookie.
  * on every request the user (and their role) is read fresh from the database, so a
    deactivated account or a changed role takes effect immediately.
  * role_required / login_required decorate a route and answer 401 (not signed in) or
    403 (wrong role) before the route runs.
"""
import time
from functools import wraps

from flask import Blueprint, abort, current_app, g, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

MAX_FAILED_LOGINS = 5      # wrong passwords allowed for one username ...
LOCKOUT_SECONDS = 60       # ... within this many seconds, then logins for it are refused

# Checked when the username does not exist, so a wrong username takes as long to answer
# as a wrong password (an attacker cannot tell the two cases apart).
_DUMMY_HASH = generate_password_hash("not-a-real-password")


# ----------------------------------------------------------------- failed-login limit
def _failures() -> dict:
    """username -> (number of failures, time of the first one). Lives on the app object."""
    return current_app.extensions.setdefault("login_failures", {})


def _is_locked(username: str) -> bool:
    entry = _failures().get(username)
    if entry is None:
        return False
    count, first = entry
    if time.monotonic() - first > LOCKOUT_SECONDS:
        del _failures()[username]
        return False
    return count >= MAX_FAILED_LOGINS


def _record_failure(username: str) -> None:
    now = time.monotonic()
    count, first = _failures().get(username, (0, now))
    if now - first > LOCKOUT_SECONDS:
        count, first = 0, now
    _failures()[username] = (count + 1, first)


# ---------------------------------------------------------------------- current user
def current_user() -> dict | None:
    """The signed-in user as a dict, or None. Read from the database once per request."""
    if "current_user" in g:
        return g.current_user
    user = None
    user_id = session.get("user_id")
    if user_id is not None:
        row = get_db().execute(
            "SELECT id, username, role, lecturer_id, group_id FROM users "
            "WHERE id = ? AND is_active = 1",
            (user_id,),
        ).fetchone()
        user = dict(row) if row else None
        if user is None:
            session.clear()          # the account was deleted or switched off
    g.current_user = user
    return user


# ------------------------------------------------------------------------- endpoints
@bp.post("/login")
def login():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        abort(400, "Send a JSON body with a username and a password")
    username, password = body.get("username"), body.get("password")
    if not isinstance(username, str) or not isinstance(password, str) \
            or not username.strip() or not password:
        abort(400, "Username and password are required")
    username = username.strip()[:100].lower()    # usernames are not case-sensitive

    if _is_locked(username):
        abort(429, "Too many failed attempts. Try again in a minute.")

    row = get_db().execute(          # parameterised query: input never becomes SQL
        "SELECT id, username, password_hash, role FROM users "
        "WHERE lower(username) = ? AND is_active = 1",
        (username,),
    ).fetchone()
    password_ok = check_password_hash(row["password_hash"] if row else _DUMMY_HASH, password)
    if row is None or not password_ok:
        _record_failure(username)
        abort(401, "Wrong username or password")     # the same message for both cases

    _failures().pop(username, None)
    session.clear()                  # start a fresh session on every sign-in
    session["user_id"] = row["id"]
    g.pop("current_user", None)
    return jsonify(id=row["id"], username=row["username"], role=row["role"])


@bp.post("/logout")
def logout():
    session.clear()
    return jsonify({})


@bp.get("/me")
def me():
    user = current_user()
    if user is None:
        abort(401, "Please sign in")
    return jsonify(user)


# ----------------------------------------------------------------------- decorators
def login_required(view):
    """Reject anonymous requests with 401."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            abort(401, "Please sign in")
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    """Reject users whose role is not in `roles` (401 if anonymous, 403 if wrong role)."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = current_user()
            if user is None:
                abort(401, "Please sign in")
            if user["role"] not in roles:
                abort(403, "You do not have permission to do this")
            return view(*args, **kwargs)
        return wrapped
    return decorator
