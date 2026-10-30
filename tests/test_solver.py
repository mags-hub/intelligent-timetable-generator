"""Ticket 9. Test the solver on tiny hand-made problems first, then on real data."""
import sqlite3

import pytest

from scheduling.backtracking import solve, solve_with_reason
from scheduling.constraints import hard_violations
from scheduling.generate import generate_timetable
from scheduling.models import (
    Assignment, Course, Group, Problem, Room, Slot, Solution,
)

def tiny_problem(locked=()):
    """5 one-hour courses, 2 rooms, 4 teaching slots, and a parent group with two sub-groups."""
    slots = [
        Slot(1, 1, "08:15", "09:15"),
        Slot(2, 1, "09:15", "10:15"),
        Slot(3, 1, "11:15", "12:15"),
        Slot(4, 2, "08:15", "09:15"),
    ]
    rooms = [Room(1, "R1", 30, "lecture"), Room(2, "R2", 100, "lecture")]
    groups = [
        Group(1, "G1", 35),
        Group(2, "G2", 20),
        Group(3, "G1-A", 10, parent_id=1),
        Group(4, "G1-B", 10, parent_id=1),
    ]
    courses = [
        Course(1, "AAA", 1, 1, 1, (1,)),   # lecturer 1, group G1
        Course(2, "BBB", 1, 1, 1, (2,)),   # lecturer 1, group G2
        Course(3, "CCC", 2, 1, 1, (1,)),   # lecturer 2, group G1
        Course(4, "DDD", 3, 1, 1, (3,)),   # lecturer 3, stream G1-A
        Course(5, "EEE", 4, 1, 1, (4,)),   # lecturer 4, stream G1-B
    ]
    return Problem(courses, rooms, groups, slots, locked=list(locked))


def solution(*triples):
    """solution((course_id, room_id, slot_id), ...)"""
    return Solution([Assignment(*t) for t in triples])


# A valid timetable for tiny_problem().
VALID = [(1, 2, 1), (2, 1, 2), (3, 2, 4), (4, 1, 3), (5, 2, 3)]


def test_hard_violations_accepts_a_valid_timetable():
    assert hard_violations(tiny_problem(), solution(*VALID)) == []


def test_hard_violations_detects_lecturer_overlap():
    """Two courses with one lecturer in the same slot -> a violation message."""
    bad = [(1, 2, 1), (2, 1, 1), (3, 2, 4), (4, 1, 3), (5, 2, 3)]
    msgs = hard_violations(tiny_problem(), solution(*bad))
    assert any("Lecturer 1" in m and "AAA" in m and "BBB" in m for m in msgs)


def test_hard_violations_detects_room_overlap():
    """Two courses in one room and slot -> a violation message."""
    bad = [(1, 2, 1), (2, 2, 1), (3, 2, 4), (4, 1, 3), (5, 2, 3)]
    msgs = hard_violations(tiny_problem(), solution(*bad))
    assert any("Room R2" in m for m in msgs)


def test_hard_violations_detects_group_overlap():
    """One group in two classes at once -> a violation message."""
    # AAA and CCC both belong to group G1 and are placed in the same slot.
    bad = [(1, 2, 1), (2, 1, 2), (3, 1, 1), (4, 1, 3), (5, 2, 3)]
    msgs = hard_violations(tiny_problem(), solution(*bad))
    assert any("Group G1 " in m for m in msgs)


def test_hard_violations_parent_group_clashes_with_its_stream():
    # DDD is for stream G1-A, AAA is for its parent group G1: same students.
    bad = [(1, 2, 1), (2, 1, 2), (3, 2, 4), (4, 1, 1), (5, 2, 3)]
    msgs = hard_violations(tiny_problem(), solution(*bad))
    assert any("Group G1 " in m for m in msgs)


def test_hard_violations_sibling_streams_may_share_a_slot():
    # DDD (G1-A) and EEE (G1-B) in the same slot is allowed: they are different students.
    assert hard_violations(tiny_problem(), solution(*VALID)) == []


def test_hard_violations_detects_room_too_small():
    bad = [(1, 1, 1), (2, 1, 2), (3, 2, 4), (4, 1, 3), (5, 2, 3)]  # 35 students in a 30-seat room
    msgs = hard_violations(tiny_problem(), solution(*bad))
    assert any("AAA has 35 students" in m for m in msgs)


def test_hard_violations_detects_a_break_or_unknown_slot():
    bad = [(1, 2, 99), (2, 1, 2), (3, 2, 4), (4, 1, 3), (5, 2, 3)]
    msgs = hard_violations(tiny_problem(), solution(*bad))
    assert any("break or does not exist" in m for m in msgs)


def test_hard_violations_detects_missing_weekly_hours():
    msgs = hard_violations(tiny_problem(), solution(*VALID[:4]))   # EEE not placed
    assert any("EEE: 0 of 1 weekly hours placed" in m for m in msgs)


def test_hard_violations_detects_split_two_hour_block():
    lab = Problem([Course(1, "LAB", 1, 2, 2, (2,))], tiny_problem().rooms,
                  tiny_problem().groups, tiny_problem().slots)
    # Slots 2 and 3 are on the same day but separated by the lunch break.
    msgs = hard_violations(lab, solution((1, 1, 2), (1, 1, 3)))
    assert any("back-to-back" in m for m in msgs)
    # Slots 1 and 2 are back to back, so this one is fine.
    assert hard_violations(lab, solution((1, 1, 1), (1, 1, 2))) == []


def test_hard_violations_detects_a_moved_locked_entry():
    problem = tiny_problem(locked=[Assignment(1, 2, 1)])
    moved = [(1, 2, 2), (2, 1, 3), (3, 2, 4), (4, 1, 1), (5, 2, 1)]
    msgs = hard_violations(problem, solution(*moved))
    assert any("Locked entry for AAA" in m for m in msgs)


def test_hard_violations_accepts_the_real_bsc1_sample_timetable(db_path):
    from scheduling.loader import load_problem

    problem = load_problem(db_path)
    year1 = [c for c in problem.courses if c.group_ids == (1,)]
    problem = Problem(year1, problem.rooms, problem.groups, problem.slots)
    con = sqlite3.connect(str(db_path))
    rows = con.execute(
        "SELECT course_id, room_id, time_slot_id FROM timetable_entries WHERE timetable_id = 1"
    ).fetchall()
    con.close()
    assert hard_violations(problem, solution(*rows)) == []


def test_load_problem_reads_seeded_data(db_path):
    """loader.load_problem(db_path) -> 21 courses, 10 rooms, 35 non-break slots."""
    from scheduling.loader import load_problem

    problem = load_problem(db_path)
    assert len(problem.courses) == 21
    assert len(problem.rooms) == 10
    assert len(problem.slots) == 35


def day_problem(courses, rooms=None, groups=None, slots=None, locked=()):
    """One teaching day of four back-to-back one-hour slots, unless you pass your own."""
    slots = slots or [
        Slot(1, 1, "08:15", "09:15"),
        Slot(2, 1, "09:15", "10:15"),
        Slot(3, 1, "10:15", "11:15"),
        Slot(4, 1, "11:15", "12:15"),
    ]
    rooms = rooms or [Room(1, "R1", 40, "lecture"), Room(2, "R2", 40, "lecture")]
    groups = groups or [Group(1, "G1", 30), Group(2, "G2", 30)]
    return Problem(courses, rooms, groups, slots, locked=list(locked))


def test_solver_returns_clash_free_timetable_on_small_problem():
    """3 courses, 2 rooms, 4 slots -> solution with no hard violations."""
    problem = day_problem([
        Course(1, "AAA", 1, 2, 1, (1,)),
        Course(2, "BBB", 1, 1, 1, (2,)),
        Course(3, "CCC", 2, 2, 1, (1,)),
    ])
    result = solve(problem)
    assert result is not None
    assert hard_violations(problem, result) == []


def test_solver_places_all_weekly_hours():
    """Every course gets exactly weekly_hours assignments."""
    problem = day_problem([
        Course(1, "AAA", 1, 2, 1, (1,)),
        Course(2, "BBB", 1, 1, 1, (2,)),
        Course(3, "CCC", 2, 2, 1, (1,)),
    ])
    result = solve(problem)
    for course in problem.courses:
        placed = [a for a in result.assignments if a.course_id == course.id]
        assert len(placed) == course.weekly_hours


def test_solver_keeps_two_hour_blocks_consecutive():
    """A course with block_hours = 2 gets back-to-back slots on one day."""
    problem = day_problem([Course(1, "LAB", 1, 2, 2, (1,))])
    result = solve(problem)
    ids = sorted(a.slot_id for a in result.assignments)
    assert ids[1] == ids[0] + 1                      # the two hours touch
    assert hard_violations(problem, result) == []


def test_solver_reports_infeasible_problem():
    """Two courses, one lecturer, one slot -> solve() returns None (not a crash or a hang)."""
    problem = day_problem(
        [Course(1, "AAA", 1, 1, 1, (1,)), Course(2, "BBB", 1, 1, 1, (2,))],
        slots=[Slot(1, 1, "08:15", "09:15")],
    )
    assert solve(problem) is None
    solution, message = solve_with_reason(problem)
    assert solution is None
    assert "Lecturer 1" in message


def test_solver_explains_when_no_room_is_big_enough():
    problem = day_problem(
        [Course(1, "AAA", 1, 1, 1, (1,))],
        rooms=[Room(1, "Tiny", 10, "lecture")],
    )
    solution, message = solve_with_reason(problem)
    assert solution is None
    assert "No room is large enough for AAA" in message


def test_solver_gives_up_quickly_when_there_are_not_enough_room_slots(db_path):
    """One room cannot hold 76 hours in 35 slots, so we get a clear message at once."""
    import time
    from scheduling.loader import load_problem

    full = load_problem(db_path)
    problem = Problem(full.courses, [Room(1, "AUD", 200, "auditorium")], full.groups, full.slots)
    started = time.monotonic()
    solution, message = solve_with_reason(problem, time_limit_s=30)
    assert time.monotonic() - started < 5
    assert solution is None
    assert "need a room" in message


def test_solver_never_uses_break_slots(db_path):
    """No assignment lands in 12:15-13:15."""
    from scheduling.loader import load_problem

    problem = load_problem(db_path)
    result = solve(problem)
    con = sqlite3.connect(str(db_path))
    break_ids = {r[0] for r in con.execute("SELECT id FROM time_slots WHERE is_break = 1")}
    con.close()
    assert break_ids                                   # the seed data does contain breaks
    assert not break_ids & {a.slot_id for a in result.assignments}


def test_solver_keeps_locked_entries_where_they_are():
    problem = day_problem(
        [Course(1, "AAA", 1, 2, 1, (1,)), Course(2, "BBB", 2, 1, 1, (1,))],
        locked=[Assignment(1, 2, 3)],
    )
    result = solve(problem)
    assert Assignment(1, 2, 3) in result.assignments
    assert len([a for a in result.assignments if a.course_id == 1]) == 2


def test_solver_gives_the_same_answer_every_time():
    problem = day_problem([
        Course(1, "AAA", 1, 2, 1, (1,)),
        Course(2, "BBB", 2, 2, 1, (2,)),
    ])
    assert solve(problem).assignments == solve(problem).assignments


def test_solver_handles_the_real_bsc1_group1_course_set(db_path):
    """Solve only the year-1 courses from the seeded database -> valid timetable."""
    from scheduling.loader import load_problem

    full = load_problem(db_path)
    problem = Problem([c for c in full.courses if c.group_ids == (1,)],
                      full.rooms, full.groups, full.slots)
    result = solve(problem)
    assert result is not None
    assert hard_violations(problem, result) == []


def test_solver_finishes_within_time_limit_on_all_years(db_path):
    """All 21 courses together finish within time_limit_s."""
    import time
    from scheduling.loader import load_problem

    problem = load_problem(db_path)
    started = time.monotonic()
    result = solve(problem, time_limit_s=30)
    assert time.monotonic() - started < 30
    assert result is not None
    assert hard_violations(problem, result) == []


def test_generate_timetable_saves_a_valid_draft(db_path):
    """The one function the backend calls: load, solve, save."""
    result = generate_timetable(str(db_path), "Test draft", 2, 2026)
    assert result.feasible and result.message == "ok"
    assert result.timetable_id is not None
    con = sqlite3.connect(str(db_path))
    status = con.execute("SELECT status FROM timetables WHERE id = ?", (result.timetable_id,)).fetchone()[0]
    entries = con.execute("SELECT COUNT(*) FROM timetable_entries WHERE timetable_id = ?",
                          (result.timetable_id,)).fetchone()[0]
    con.close()
    assert status == "draft"
    assert entries > 0


def test_generate_timetable_reports_impossible_data(db_path):
    """Make the data impossible (one tiny room) -> feasible is False with a reason."""
    con = sqlite3.connect(str(db_path))
    con.execute("UPDATE rooms SET capacity = 1")  # no room can hold any group
    con.commit()
    con.close()
    result = generate_timetable(str(db_path), "Impossible", 2, 2026)
    assert result.feasible is False
    assert "No room is large enough" in result.message
