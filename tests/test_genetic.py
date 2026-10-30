"""Ticket 10."""
import pytest

TODO = "TODO Ticket 10"


@pytest.mark.skip(reason=TODO)
def test_ga_improves_soft_score_over_backtracking_output(db_path):
    """soft_score(optimise(...)) > soft_score(start) on the seeded data (Ticket 10's acceptance criterion)."""


@pytest.mark.skip(reason=TODO)
def test_ga_result_is_still_hard_constraint_valid(db_path):
    """constraints.is_valid(problem, optimised) is True."""


@pytest.mark.skip(reason=TODO)
def test_ga_never_returns_worse_than_the_start_solution(db_path):
    """Score never goes down, even with a tiny population."""


@pytest.mark.skip(reason=TODO)
def test_ga_does_not_move_locked_entries(db_path):
    """Locked assignments are identical before and after."""


@pytest.mark.skip(reason=TODO)
def test_ga_is_repeatable_with_a_fixed_seed(db_path):
    """Two runs with seed=42 give the same score."""
