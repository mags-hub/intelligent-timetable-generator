"""
Database constraint tests (supports Tickets 7, 8 and 11).

Run from the repo root:
    python -m pytest tests/test_database_constraints.py -v

Each test builds a fresh in-memory-style DB (schema + reference seed, NO
sample timetable) and tries to store an illegal timetable. The database
itself must refuse it.
"""
import sqlite3
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "database" / "migrations" / "001_initial_schema.sql"
SEED = ROOT / "database" / "seeds" / "001_reference_data.sql"
SAMPLE = ROOT / "database" / "seeds" / "002_sample_timetable_bsc1_g1.sql"


@pytest.fixture()
def db():
    with tempfile.TemporaryDirectory() as d:
        con = sqlite3.connect(Path(d) / "t.db")
        con.execute("PRAGMA foreign_keys = ON")
        con.executescript(MIGRATION.read_text(encoding="utf-8"))
        con.executescript(SEED.read_text(encoding="utf-8"))
        con.execute(
            "INSERT INTO timetables (id, name, semester, academic_year) "
            "VALUES (1, 'draft A', 2, 2026), (2, 'draft B', 2, 2026)"
        )
        con.commit()
        yield con
        con.close()


# ---- helpers ---------------------------------------------------------
def slot(con, day, start):
    return con.execute(
        "SELECT id FROM time_slots WHERE day_of_week=? AND start_time=?", (day, start)
    ).fetchone()[0]


def add_entry(con, code, room, day, start, timetable=1, groups=("BSC1-G1",)):
    """Insert one entry plus its group links. Raises sqlite3.IntegrityError on a clash."""
    course_id, lecturer_id = con.execute(
        "SELECT id, lecturer_id FROM courses WHERE code=?", (code,)
    ).fetchone()
    room_id = con.execute("SELECT id FROM rooms WHERE name=?", (room,)).fetchone()[0]
    slot_id = slot(con, day, start)
    cur = con.execute(
        "INSERT INTO timetable_entries (timetable_id, course_id, lecturer_id, room_id, time_slot_id) "
        "VALUES (?,?,?,?,?)",
        (timetable, course_id, lecturer_id, room_id, slot_id),
    )
    entry_id = cur.lastrowid
    for g in groups:
        gid = con.execute("SELECT id FROM student_groups WHERE name=?", (g,)).fetchone()[0]
        con.execute(
            "INSERT INTO timetable_entry_groups (entry_id, timetable_id, time_slot_id, group_id) "
            "VALUES (?,?,?,?)",
            (entry_id, timetable, slot_id, gid),
        )
    return entry_id


# ---- the happy path --------------------------------------------------
def test_valid_entry_is_accepted(db):
    add_entry(db, "PRO512A", "LAB4", 1, "08:15")


def test_real_bsc1_timetable_loads_cleanly(db):
    """The genuine Bryanston BSc1 Group 1 timetable must violate nothing."""
    db.execute("DELETE FROM timetables")  # the sample seed creates its own timetable id 1
    db.commit()
    db.executescript(SAMPLE.read_text(encoding="utf-8"))
    n = db.execute("SELECT COUNT(*) FROM timetable_entries WHERE timetable_id=1").fetchone()[0]
    assert n == 24


# ---- hard constraints ------------------------------------------------
def test_lecturer_cannot_be_double_booked(db):
    # Bukasa teaches both PRO512A and MAT512
    add_entry(db, "PRO512A", "LAB4", 1, "08:15")
    with pytest.raises(sqlite3.IntegrityError):
        add_entry(db, "MAT512", "L2", 1, "08:15")  # same lecturer, same slot


def test_room_cannot_be_double_booked(db):
    add_entry(db, "PRO512A", "LAB4", 1, "08:15", groups=("BSC1-G1",))
    with pytest.raises(sqlite3.IntegrityError):
        add_entry(db, "WBT512A", "LAB4", 1, "08:15", groups=("BSC1-G1",))  # other lecturer, same room


def test_group_cannot_be_double_booked(db):
    add_entry(db, "PRO512A", "LAB4", 1, "08:15")
    with pytest.raises(sqlite3.IntegrityError):
        add_entry(db, "WBT512A", "LAB2", 1, "08:15")  # different lecturer + room, same group


def test_drafts_do_not_clash_with_each_other(db):
    add_entry(db, "PRO512A", "LAB4", 1, "08:15", timetable=1)
    add_entry(db, "PRO512A", "LAB4", 1, "08:15", timetable=2)  # same slot, other draft: fine


def test_no_classes_in_lunch_break(db):
    with pytest.raises(sqlite3.IntegrityError):
        add_entry(db, "PRO512A", "LAB4", 1, "12:15")


def test_lecturer_must_match_course(db):
    course_id = db.execute("SELECT id FROM courses WHERE code='PRO512A'").fetchone()[0]
    room_id = db.execute("SELECT id FROM rooms WHERE name='LAB4'").fetchone()[0]
    wrong_lecturer = db.execute("SELECT id FROM lecturers WHERE name='Pam'").fetchone()[0]
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO timetable_entries (timetable_id, course_id, lecturer_id, room_id, time_slot_id) "
            "VALUES (1,?,?,?,?)",
            (course_id, wrong_lecturer, room_id, slot(db, 1, "08:15")),
        )


def test_room_capacity_is_enforced(db):
    db.execute("UPDATE student_groups SET size = 50 WHERE name='BSC1-G1'")  # LAB4 holds 40
    with pytest.raises(sqlite3.IntegrityError):
        add_entry(db, "PRO512A", "LAB4", 1, "08:15")


def test_group_must_take_the_course(db):
    # BSC2 does not take the 1st-year course PRO512A
    with pytest.raises(sqlite3.IntegrityError):
        add_entry(db, "PRO512A", "LAB4", 1, "08:15", groups=("BSC2",))


def test_combined_class_two_groups_one_entry(db):
    # Make a course shared by two groups (a "combined" class), then schedule it once.
    db.execute(
        "INSERT INTO course_groups (course_id, group_id) "
        "SELECT c.id, g.id FROM courses c, student_groups g WHERE c.code='BAS622' AND g.name='BSC3'"
    )
    # Two groups of 35 = 70 students, so it needs the auditorium (150), not a 60-seat room.
    add_entry(db, "BAS622", "AUD", 2, "08:15", groups=("BSC2", "BSC3"))


def test_group_link_must_match_entry_slot(db):
    """The composite FK stops a group link pointing at the wrong slot."""
    entry_id = add_entry(db, "PRO512A", "LAB4", 1, "08:15")
    other_slot = slot(db, 1, "09:15")
    gid = db.execute("SELECT id FROM student_groups WHERE name='BSC1-G1'").fetchone()[0]
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO timetable_entry_groups (entry_id, timetable_id, time_slot_id, group_id) "
            "VALUES (?,?,?,?)",
            (entry_id, 1, other_slot, gid),
        )


# ---- publishing and users --------------------------------------------
def test_only_one_published_timetable_per_semester(db):
    db.execute("UPDATE timetables SET status='published', published_at=datetime('now') WHERE id=1")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("UPDATE timetables SET status='published', published_at=datetime('now') WHERE id=2")


def test_published_requires_published_at(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("UPDATE timetables SET status='published' WHERE id=1")


def test_user_role_link_consistency(db):
    with pytest.raises(sqlite3.IntegrityError):  # lecturer account without a lecturer record
        db.execute("INSERT INTO users (username, password_hash, role) VALUES ('x','h','lecturer')")
    with pytest.raises(sqlite3.IntegrityError):  # student account without a group
        db.execute("INSERT INTO users (username, password_hash, role) VALUES ('y','h','student')")
    with pytest.raises(sqlite3.IntegrityError):  # unknown role
        db.execute("INSERT INTO users (username, password_hash, role) VALUES ('z','h','hacker')")


def test_cannot_delete_lecturer_who_has_courses(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("DELETE FROM lecturers WHERE name='Bukasa'")
