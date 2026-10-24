"""Ticket 9. Test the solver on tiny hand-made problems first, then on real data."""
import pytest

TODO = "TODO Ticket 9"


@pytest.mark.skip(reason=TODO)
def test_load_problem_reads_seeded_data(db_path):
    """loader.load_problem(db_path) -> 21 courses, 10 rooms, 35 non-break slots."""


@pytest.mark.skip(reason=TODO)
def test_hard_violations_detects_lecturer_overlap():
    """Two courses with one lecturer in the same slot -> a violation message."""


@pytest.mark.skip(reason=TODO)
def test_hard_violations_detects_room_overlap():
    """Two courses in one room and slot -> a violation message."""


@pytest.mark.skip(reason=TODO)
def test_hard_violations_detects_group_overlap():
    """One group in two classes at once -> a violation message."""


@pytest.mark.skip(reason=TODO)
def test_solver_returns_clash_free_timetable_on_small_problem():
    """3 courses, 2 rooms, 4 slots -> solution with no hard violations."""


@pytest.mark.skip(reason=TODO)
def test_solver_places_all_weekly_hours():
    """Every course gets exactly weekly_hours assignments."""


@pytest.mark.skip(reason=TODO)
def test_solver_keeps_two_hour_blocks_consecutive():
    """A course with block_hours = 2 gets back-to-back slots on one day."""


@pytest.mark.skip(reason=TODO)
def test_solver_reports_infeasible_problem():
    """Two courses, one lecturer, one slot -> solve() returns None (not a crash or a hang)."""


@pytest.mark.skip(reason=TODO)
def test_solver_never_uses_break_slots():
    """No assignment lands in 12:15-13:15."""


@pytest.mark.skip(reason=TODO)
def test_solver_handles_the_real_bsc1_group1_course_set(db_path):
    """Solve only the year-1 courses from the seeded database -> valid timetable."""


@pytest.mark.skip(reason=TODO)
def test_solver_finishes_within_time_limit_on_all_years(db_path):
    """All 21 courses together finish within time_limit_s."""
