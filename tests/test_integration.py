"""End-to-end tests across modules. Needs Tickets 5, 6, 9."""
import pytest

TODO = "TODO Tickets 5, 6, 9"


@pytest.mark.skip(reason=TODO)
def test_generate_publish_and_student_view_flow(client):
    """Admin generates -> draft exists -> admin publishes -> student sees only their group's classes."""


@pytest.mark.skip(reason=TODO)
def test_generated_timetable_has_no_clashes_in_the_database(client):
    """After /generate, scan timetable_entries for any lecturer/room/group appearing twice in a slot."""


@pytest.mark.skip(reason=TODO)
def test_infeasible_data_returns_422_with_a_reason(client):
    """Make the data impossible (one room, many courses) -> POST /generate -> 422 with a message."""
