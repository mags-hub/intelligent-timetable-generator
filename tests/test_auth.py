"""Ticket 5. Un-skip each test as you build the feature."""
import pytest

TODO = "TODO Ticket 5"


@pytest.mark.skip(reason=TODO)
def test_login_with_correct_password_returns_role(client):
    """POST /api/auth/login as admin / ChangeMe123! -> 200 and role == 'admin'."""


@pytest.mark.skip(reason=TODO)
def test_login_with_wrong_password_is_401(client):
    """Wrong password -> 401, and the message does not reveal whether the username exists."""


@pytest.mark.skip(reason=TODO)
def test_student_cannot_open_admin_endpoints(client):
    """Log in as student_bsc1, GET /api/lecturers -> 403."""


@pytest.mark.skip(reason=TODO)
def test_lecturer_cannot_publish_a_timetable(client):
    """Log in as bukasa, POST /api/timetables/1/publish -> 403."""


@pytest.mark.skip(reason=TODO)
def test_anonymous_gets_401(client):
    """No login: GET /api/auth/me -> 401."""


@pytest.mark.skip(reason=TODO)
def test_logout_ends_the_session(client):
    """Login, logout, then /api/auth/me -> 401."""
