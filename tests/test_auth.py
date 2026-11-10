"""Ticket 5: sign in, sign out and roles."""
import sqlite3

PASSWORD = "ChangeMe123!"      # the development password set by database/build_db.py


def login(client, username, password=PASSWORD):
    return client.post("/api/auth/login", json={"username": username, "password": password})


def test_login_with_correct_password_returns_role(client):
    """POST /api/auth/login as admin / ChangeMe123! -> 200 and role == 'admin'."""
    response = login(client, "admin")
    assert response.status_code == 200
    body = response.get_json()
    assert body["role"] == "admin" and body["username"] == "admin"
    assert "password" not in response.get_data(as_text=True).lower()     # no hash leaks out


def test_login_with_wrong_password_is_401(client):
    """Wrong password -> 401, and the message does not reveal whether the username exists."""
    wrong_password = login(client, "admin", "not-the-password")
    unknown_user = login(client, "nobody-here", "not-the-password")
    assert wrong_password.status_code == 401
    assert unknown_user.status_code == 401
    assert wrong_password.get_data() == unknown_user.get_data()          # identical answers


def test_login_without_a_username_or_password_is_400(client):
    assert client.post("/api/auth/login", json={"username": "admin"}).status_code == 400
    assert client.post("/api/auth/login", data="not json").status_code == 400


def test_student_cannot_open_admin_endpoints(client):
    """Log in as student_bsc1: admin-only endpoints answer 403.

    Uses the timetable routes. When Ticket 6's data routes are merged, GET /api/lecturers
    is admin-only too and can be added here.
    """
    assert login(client, "student_bsc1").status_code == 200
    assert client.get("/api/timetables").status_code == 403
    assert client.post("/api/timetables/generate").status_code == 403


def test_lecturer_cannot_publish_a_timetable(client):
    """Log in as bukasa, POST /api/timetables/1/publish -> 403."""
    assert login(client, "bukasa").status_code == 200
    assert client.post("/api/timetables/1/publish").status_code == 403


def test_anonymous_gets_401(client):
    """No login: GET /api/auth/me -> 401."""
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/timetables").status_code == 401               # protected routes too
    assert client.post("/api/timetables/generate").status_code == 401
    assert client.get("/api/timetables/published/mine").status_code == 401


def test_me_returns_the_link_to_the_lecturer_or_group(client):
    login(client, "student_bsc1")
    body = client.get("/api/auth/me").get_json()
    assert body["role"] == "student" and body["group_id"] is not None
    client.post("/api/auth/logout")
    login(client, "bukasa")
    body = client.get("/api/auth/me").get_json()
    assert body["role"] == "lecturer" and body["lecturer_id"] is not None


def test_logout_ends_the_session(client):
    """Login, logout, then /api/auth/me -> 401."""
    login(client, "admin")
    assert client.get("/api/auth/me").status_code == 200
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/auth/me").status_code == 401


def test_an_inactive_account_cannot_sign_in(client, db_path):
    con = sqlite3.connect(str(db_path))
    con.execute("UPDATE users SET is_active = 0 WHERE username = 'bukasa'")
    con.commit()
    con.close()
    assert login(client, "bukasa").status_code == 401


def test_switching_an_account_off_ends_its_session_at_once(client, db_path):
    login(client, "bukasa")
    assert client.get("/api/auth/me").status_code == 200
    con = sqlite3.connect(str(db_path))
    con.execute("UPDATE users SET is_active = 0 WHERE username = 'bukasa'")
    con.commit()
    con.close()
    assert client.get("/api/auth/me").status_code == 401


def test_repeated_wrong_passwords_lock_that_username_for_a_minute(client):
    for _ in range(5):
        assert login(client, "bukasa", "wrong").status_code == 401
    assert login(client, "bukasa", PASSWORD).status_code == 429          # even the right password
    assert login(client, "admin").status_code == 200                      # other users unaffected
                      # other users unaffected
