"""Basic checks that must always pass."""


def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_frontend_is_served(client):
    assert client.get("/login.html").status_code == 200
    assert client.get("/").status_code == 200


def test_protected_routes_are_never_open_to_anonymous_users(client):
    """Today these answer 501 (not built yet); after Ticket 5 they must answer 401.
    Either way an anonymous request must NEVER succeed."""
    for url in ["/api/lecturers", "/api/courses", "/api/rooms", "/api/timetables"]:
        assert client.get(url).status_code != 200, url
