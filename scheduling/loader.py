"""The ONLY file in scheduling/ that touches the database."""
import sqlite3

from .models import (
    Assignment, Course, Group, Problem, Room, Slot, Solution,
)


def _connect(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def load_problem(db_path: str) -> Problem:
    """Read everything the solver needs from the database into a Problem."""
    con = _connect(db_path)
    try:
        # Break slots (lunch) are left out, so the solver can never use them.
        slots = [
            Slot(id=r["id"], day=r["day_of_week"], start=r["start_time"], end=r["end_time"])
            for r in con.execute(
                "SELECT id, day_of_week, start_time, end_time FROM time_slots "
                "WHERE is_break = 0 ORDER BY day_of_week, start_time"
            )
        ]

        rooms = [
            Room(id=r["id"], name=r["name"], capacity=r["capacity"], room_type=r["room_type"])
            for r in con.execute(
                "SELECT id, name, capacity, room_type FROM rooms ORDER BY id"
            )
        ]

        groups = [
            Group(id=r["id"], name=r["name"], size=r["size"], parent_id=r["parent_group_id"])
            for r in con.execute(
                "SELECT id, name, size, parent_group_id FROM student_groups ORDER BY id"
            )
        ]

        # Which groups take each course (a course with several groups is a combined class).
        groups_by_course: dict[int, list[int]] = {}
        for r in con.execute(
            "SELECT course_id, group_id FROM course_groups ORDER BY course_id, group_id"
        ):
            groups_by_course.setdefault(r["course_id"], []).append(r["group_id"])

        courses = [
            Course(
                id=r["id"],
                code=r["code"],
                lecturer_id=r["lecturer_id"],
                weekly_hours=r["weekly_hours"],
                block_hours=r["block_hours"],
                group_ids=tuple(groups_by_course.get(r["id"], [])),
                preferred_room_type=r["preferred_room_type"],
            )
            for r in con.execute(
                "SELECT id, code, lecturer_id, weekly_hours, block_hours, preferred_room_type "
                "FROM courses ORDER BY id"
            )
        ]

        # Locked entries (is_locked = 1) are not loaded yet; the list stays empty.
        return Problem(courses=courses, rooms=rooms, groups=groups, slots=slots, locked=[])
    finally:
        con.close()


def save_solution(db_path: str, solution: Solution, name: str, semester: int, academic_year: int) -> int:
    """Save a Solution as a new DRAFT timetable and return its id.

    Everything is written in one transaction: if anything fails, nothing is saved.
    """
    con = _connect(db_path)
    try:
        with con:  # commits on success, rolls back if an exception is raised
            cur = con.execute(
                "INSERT INTO timetables (name, semester, academic_year, status) "
                "VALUES (?, ?, ?, 'draft')",
                (name, semester, academic_year),
            )
            timetable_id = cur.lastrowid

            for a in solution.assignments:
                course = con.execute(
                    "SELECT lecturer_id FROM courses WHERE id = ?", (a.course_id,)
                ).fetchone()
                entry = con.execute(
                    "INSERT INTO timetable_entries "
                    "(timetable_id, course_id, lecturer_id, room_id, time_slot_id) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (timetable_id, a.course_id, course["lecturer_id"], a.room_id, a.slot_id),
                )
                for g in con.execute(
                    "SELECT group_id FROM course_groups WHERE course_id = ?", (a.course_id,)
                ):
                    con.execute(
                        "INSERT INTO timetable_entry_groups "
                        "(entry_id, timetable_id, time_slot_id, group_id) VALUES (?, ?, ?, ?)",
                        (entry.lastrowid, timetable_id, a.slot_id, g["group_id"]),
                    )
        return timetable_id
    finally:
        con.close()
