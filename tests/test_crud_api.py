"""Ticket 6. Log in as admin first (use a helper fixture once Ticket 5 is done)."""
import pytest

TODO = "TODO Ticket 6"


@pytest.mark.skip(reason=TODO)
def test_list_lecturers_returns_seeded_rows(client):
    """GET /api/lecturers -> 200 and 8 lecturers."""


@pytest.mark.skip(reason=TODO)
def test_create_room_then_read_it_back(client):
    """POST /api/rooms -> 201; GET /api/rooms/<id> returns the same data."""


@pytest.mark.skip(reason=TODO)
def test_create_room_with_negative_capacity_is_rejected(client):
    """POST capacity=-5 -> 400 with a clear message."""


@pytest.mark.skip(reason=TODO)
def test_duplicate_course_code_is_409(client):
    """POST a course whose code already exists -> 409."""


@pytest.mark.skip(reason=TODO)
def test_cannot_delete_lecturer_with_courses(client):
    """DELETE /api/lecturers/<Bukasa> -> 409 (database blocks it)."""


@pytest.mark.skip(reason=TODO)
def test_unknown_resource_is_404(client):
    """GET /api/banana -> 404."""


@pytest.mark.skip(reason=TODO)
def test_manual_edit_that_causes_a_clash_is_409(client):
    """PUT .../entries/<id> moving a class onto an occupied room+slot -> 409 with the reason."""


@pytest.mark.skip(reason=TODO)
def test_published_timetable_is_visible_to_students_only_when_published(client):
    """Draft -> student sees published == false; after publish -> student sees entries."""
