"""Ticket 10: the soft score and the genetic algorithm."""
from scheduling.backtracking import solve
from scheduling.constraints import SoftScorer, is_valid, soft_score
from scheduling.genetic import GAParams, optimise
from scheduling.loader import load_problem
from scheduling.models import Assignment, Course, Group, Problem, Room, Slot, Solution

SMALL = GAParams(population_size=20, generations=40)   # quick settings for the tests


def real_problem_and_start(db_path):
    problem = load_problem(db_path)
    return problem, solve(problem)


# ---------------------------------------------------------------- soft_score on tiny problems
def tiny(courses, slots=None, rooms=None):
    slots = slots or [Slot(1, 1, "08:15", "09:15"), Slot(2, 1, "09:15", "10:15"),
                      Slot(3, 1, "10:15", "11:15"), Slot(4, 1, "11:15", "12:15"),
                      Slot(5, 2, "08:15", "09:15")]
    rooms = rooms or [Room(1, "L1", 40, "lecture"), Room(2, "LAB1", 40, "lab")]
    return Problem(courses, rooms, [Group(1, "G1", 30)], slots)


def components(problem, *triples):
    return SoftScorer(problem).components([Assignment(*t) for t in triples])


def test_soft_score_counts_a_gap_in_a_groups_day():
    problem = tiny([Course(1, "AAA", 1, 1, 1, (1,)), Course(2, "BBB", 2, 1, 1, (1,))])
    assert components(problem, (1, 1, 1), (2, 1, 3))["gaps"] == 1     # a free slot between them
    assert components(problem, (1, 1, 1), (2, 1, 2))["gaps"] == 0     # back to back


def test_soft_score_does_not_count_lunch_as_a_gap():
    slots = [Slot(1, 1, "11:15", "12:15"), Slot(2, 1, "13:15", "14:15")]   # lunch sits between them
    problem = tiny([Course(1, "AAA", 1, 1, 1, (1,)), Course(2, "BBB", 2, 1, 1, (1,))], slots=slots)
    assert components(problem, (1, 1, 1), (2, 1, 2))["gaps"] == 0


def test_soft_score_counts_extra_rooms_for_one_course():
    problem = tiny([Course(1, "AAA", 1, 2, 1, (1,))])
    assert components(problem, (1, 1, 1), (1, 1, 2))["rooms"] == 0
    assert components(problem, (1, 1, 1), (1, 2, 2))["rooms"] == 1


def test_soft_score_counts_the_wrong_room_type():
    problem = tiny([Course(1, "AAA", 1, 1, 1, (1,), preferred_room_type="lab")])
    assert components(problem, (1, 1, 1))["type"] == 1
    assert components(problem, (1, 2, 1))["type"] == 0


def test_soft_score_counts_classes_in_the_last_slot_of_a_day():
    problem = tiny([Course(1, "AAA", 1, 1, 1, (1,))])
    assert components(problem, (1, 1, 4))["late"] == 1                # slot 4 is last on day 1
    assert components(problem, (1, 1, 1))["late"] == 0


def test_soft_score_prefers_a_lecturer_whose_hours_are_spread_over_days():
    problem = tiny([Course(1, "AAA", 1, 2, 1, (1,))])
    same_day = components(problem, (1, 1, 1), (1, 1, 2))["load"]
    two_days = components(problem, (1, 1, 1), (1, 1, 5))["load"]
    assert two_days < same_day


def test_soft_score_is_higher_for_a_better_timetable():
    problem = tiny([Course(1, "AAA", 1, 2, 1, (1,))])
    good = Solution([Assignment(1, 1, 1), Assignment(1, 1, 5)])
    bad = Solution([Assignment(1, 1, 1), Assignment(1, 2, 4)])
    assert soft_score(problem, good) > soft_score(problem, bad)


# ---------------------------------------------------------------- the genetic algorithm
def test_ga_improves_soft_score_over_backtracking_output(db_path):
    """soft_score(optimise(...)) > soft_score(start) on the seeded data (Ticket 10's acceptance criterion)."""
    problem, start = real_problem_and_start(db_path)
    result = optimise(problem, start, SMALL)
    assert soft_score(problem, result) > soft_score(problem, start)


def test_ga_result_is_still_hard_constraint_valid(db_path):
    """constraints.is_valid(problem, optimised) is True."""
    problem, start = real_problem_and_start(db_path)
    assert is_valid(problem, optimise(problem, start, SMALL))


def test_ga_never_returns_worse_than_the_start_solution(db_path):
    """Score never goes down, even with a tiny population."""
    problem, start = real_problem_and_start(db_path)
    tiny_run = GAParams(population_size=2, generations=3, elite_size=1)
    result = optimise(problem, start, tiny_run)
    assert soft_score(problem, result) >= soft_score(problem, start)
    assert is_valid(problem, result)


def test_ga_does_not_move_locked_entries(db_path):
    """Locked assignments are identical before and after."""
    problem, start = real_problem_and_start(db_path)
    locked = [start.assignments[0], start.assignments[10], start.assignments[40]]
    locked_problem = Problem(problem.courses, problem.rooms, problem.groups, problem.slots, locked=locked)
    result = optimise(locked_problem, start, SMALL)
    for entry in locked:
        assert entry in result.assignments
    assert is_valid(locked_problem, result)


def test_ga_is_repeatable_with_a_fixed_seed(db_path):
    """Two runs with seed=42 give the same score."""
    problem, start = real_problem_and_start(db_path)
    first = optimise(problem, start, GAParams(population_size=20, generations=40, seed=42))
    second = optimise(problem, start, GAParams(population_size=20, generations=40, seed=42))
    assert first.score == second.score
    assert first.assignments == second.assignments
