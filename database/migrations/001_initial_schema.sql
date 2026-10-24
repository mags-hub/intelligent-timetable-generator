-- =====================================================================
-- Migration 001: initial schema  (Ticket 7)
-- Intelligent Timetable Generator
--
-- Engine: SQLite 3 (foreign keys ON). Everything here uses standard SQL
-- (UNIQUE, CHECK, composite FKs), so it ports to PostgreSQL/MySQL with
-- only type tweaks. The two triggers at the bottom are SQLite syntax.
--
-- Core idea: a clash is IMPOSSIBLE to store, not just unlikely.
--   * lecturer double-booking -> UNIQUE (timetable_id, lecturer_id, time_slot_id)
--   * room double-booking     -> UNIQUE (timetable_id, room_id,     time_slot_id)
--   * group double-booking    -> UNIQUE (timetable_id, group_id,    time_slot_id)
--                                on timetable_entry_groups
--   * lunch break             -> trigger blocks entries in is_break slots
--   * room capacity           -> trigger sums group sizes vs room capacity
-- =====================================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- Reference data
-- ---------------------------------------------------------------------

CREATE TABLE lecturers (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    email       TEXT UNIQUE,
    is_active   INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

CREATE TABLE rooms (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,                 -- e.g. 'L2', 'LAB4', 'AUD'
    capacity    INTEGER NOT NULL CHECK (capacity > 0),
    room_type   TEXT NOT NULL
                CHECK (room_type IN ('lecture', 'lab', 'auditorium')),
    campus      TEXT NOT NULL DEFAULT 'Bryanston'
);

-- A student group is a cohort that attends classes together.
-- Elective streams (3rd year) are modelled as sub-groups via parent_group_id,
-- so a student only "clashes" with classes of the stream they belong to.
CREATE TABLE student_groups (
    id               INTEGER PRIMARY KEY,
    name             TEXT NOT NULL UNIQUE,            -- e.g. 'BSC1-G1'
    programme        TEXT NOT NULL DEFAULT 'BSc',
    year_level       INTEGER NOT NULL CHECK (year_level BETWEEN 1 AND 4),
    campus           TEXT NOT NULL DEFAULT 'Bryanston',
    size             INTEGER NOT NULL CHECK (size > 0),
    parent_group_id  INTEGER REFERENCES student_groups(id) ON DELETE RESTRICT,
    CHECK (parent_group_id IS NULL OR parent_group_id <> id)
);

-- Each course has ONE lecturer (matches the real Richfield timetables).
-- weekly_hours / block_hours drive the solver: a 4-hour module with
-- block_hours = 2 is placed as two 2-hour blocks.
CREATE TABLE courses (
    id                  INTEGER PRIMARY KEY,
    code                TEXT NOT NULL UNIQUE,         -- e.g. 'PRO512A'
    name                TEXT NOT NULL,
    year_level          INTEGER NOT NULL CHECK (year_level BETWEEN 1 AND 4),
    lecturer_id         INTEGER NOT NULL REFERENCES lecturers(id) ON DELETE RESTRICT,
    weekly_hours        INTEGER NOT NULL DEFAULT 4 CHECK (weekly_hours > 0),
    block_hours         INTEGER NOT NULL DEFAULT 1 CHECK (block_hours BETWEEN 1 AND 4),
    preferred_room_type TEXT CHECK (preferred_room_type IN ('lecture', 'lab', 'auditorium')),
    is_elective         INTEGER NOT NULL DEFAULT 0 CHECK (is_elective IN (0, 1)),
    CHECK (weekly_hours >= block_hours)
);

-- Which groups take which course (many-to-many).
-- A course with several groups = a "combined" class.
CREATE TABLE course_groups (
    course_id   INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    group_id    INTEGER NOT NULL REFERENCES student_groups(id) ON DELETE CASCADE,
    PRIMARY KEY (course_id, group_id)
);

-- The weekly grid: Mon-Fri, one-hour slots. 12:15-13:15 is the lunch break.
CREATE TABLE time_slots (
    id            INTEGER PRIMARY KEY,
    day_of_week   INTEGER NOT NULL CHECK (day_of_week BETWEEN 1 AND 5),  -- 1 = Monday
    start_time    TEXT NOT NULL CHECK (start_time GLOB '[0-2][0-9]:[0-5][0-9]'),
    end_time      TEXT NOT NULL CHECK (end_time   GLOB '[0-2][0-9]:[0-5][0-9]'),
    is_break      INTEGER NOT NULL DEFAULT 0 CHECK (is_break IN (0, 1)),
    UNIQUE (day_of_week, start_time),
    CHECK (end_time > start_time)
);

-- ---------------------------------------------------------------------
-- Users and access control (Ticket 5 builds on this)
-- ---------------------------------------------------------------------

-- A lecturer account links to a lecturers row; a student account links to a
-- student_groups row. This is what lets "my timetable" work (Ticket 4).
CREATE TABLE users (
    id             INTEGER PRIMARY KEY,
    username       TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,
    role           TEXT NOT NULL CHECK (role IN ('admin', 'lecturer', 'student')),
    lecturer_id    INTEGER REFERENCES lecturers(id) ON DELETE SET NULL,
    group_id       INTEGER REFERENCES student_groups(id) ON DELETE SET NULL,
    is_active      INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    -- role <-> link consistency
    CHECK (role <> 'lecturer' OR lecturer_id IS NOT NULL),
    CHECK (role <> 'student'  OR group_id    IS NOT NULL),
    CHECK (role <> 'admin'    OR (lecturer_id IS NULL AND group_id IS NULL))
);

-- ---------------------------------------------------------------------
-- Timetables
-- ---------------------------------------------------------------------

-- A timetable is one generated version. Several drafts can coexist; the
-- constraints below apply WITHIN a timetable, so drafts never clash with
-- each other. Students/lecturers only ever see status = 'published'.
CREATE TABLE timetables (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    semester      INTEGER NOT NULL CHECK (semester IN (1, 2)),
    academic_year INTEGER NOT NULL,
    status        TEXT NOT NULL DEFAULT 'draft'
                  CHECK (status IN ('draft', 'published', 'archived')),
    created_by    INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    published_at  TEXT,
    CHECK (status <> 'published' OR published_at IS NOT NULL)
);

-- At most one published timetable per semester/year.
CREATE UNIQUE INDEX ux_one_published_timetable
    ON timetables (semester, academic_year)
    WHERE status = 'published';

-- One row = one course taught in one room in one one-hour slot.
-- A 2-hour practical is two consecutive rows.
CREATE TABLE timetable_entries (
    id             INTEGER PRIMARY KEY,
    timetable_id   INTEGER NOT NULL REFERENCES timetables(id) ON DELETE CASCADE,
    course_id      INTEGER NOT NULL REFERENCES courses(id)    ON DELETE RESTRICT,
    lecturer_id    INTEGER NOT NULL REFERENCES lecturers(id)  ON DELETE RESTRICT,
    room_id        INTEGER NOT NULL REFERENCES rooms(id)      ON DELETE RESTRICT,
    time_slot_id   INTEGER NOT NULL REFERENCES time_slots(id) ON DELETE RESTRICT,
    is_locked      INTEGER NOT NULL DEFAULT 0 CHECK (is_locked IN (0, 1)),  -- manual override
    -- HARD CONSTRAINTS: no lecturer or room in two places at once
    UNIQUE (timetable_id, lecturer_id, time_slot_id),
    UNIQUE (timetable_id, room_id,     time_slot_id),
    -- target for the composite FK from timetable_entry_groups
    UNIQUE (id, timetable_id, time_slot_id)
);

CREATE INDEX ix_entries_timetable_course ON timetable_entries (timetable_id, course_id);
CREATE INDEX ix_entries_slot             ON timetable_entries (time_slot_id);

-- Which groups attend an entry. One entry may have several groups (combined
-- class). timetable_id and time_slot_id are repeated here ON PURPOSE so the
-- UNIQUE below can stop a group being in two classes at the same time, and
-- the composite FK guarantees the copies always match the parent entry.
CREATE TABLE timetable_entry_groups (
    entry_id       INTEGER NOT NULL,
    timetable_id   INTEGER NOT NULL,
    time_slot_id   INTEGER NOT NULL,
    group_id       INTEGER NOT NULL REFERENCES student_groups(id) ON DELETE RESTRICT,
    PRIMARY KEY (entry_id, group_id),
    -- HARD CONSTRAINT: no group in two classes at once
    UNIQUE (timetable_id, group_id, time_slot_id),
    FOREIGN KEY (entry_id, timetable_id, time_slot_id)
        REFERENCES timetable_entries (id, timetable_id, time_slot_id)
        ON DELETE CASCADE
);

CREATE INDEX ix_entry_groups_group ON timetable_entry_groups (group_id);

-- ---------------------------------------------------------------------
-- Trigger-enforced hard constraints
-- ---------------------------------------------------------------------

-- No classes in the lunch break.
CREATE TRIGGER trg_entry_not_in_break_ins
BEFORE INSERT ON timetable_entries
WHEN (SELECT is_break FROM time_slots WHERE id = NEW.time_slot_id) = 1
BEGIN
    SELECT RAISE(ABORT, 'Cannot schedule a class in a break slot');
END;

CREATE TRIGGER trg_entry_not_in_break_upd
BEFORE UPDATE OF time_slot_id ON timetable_entries
WHEN (SELECT is_break FROM time_slots WHERE id = NEW.time_slot_id) = 1
BEGIN
    SELECT RAISE(ABORT, 'Cannot schedule a class in a break slot');
END;

-- The lecturer on an entry must be the lecturer assigned to the course.
CREATE TRIGGER trg_entry_lecturer_matches_course
BEFORE INSERT ON timetable_entries
WHEN NEW.lecturer_id <> (SELECT lecturer_id FROM courses WHERE id = NEW.course_id)
BEGIN
    SELECT RAISE(ABORT, 'Entry lecturer does not match the course lecturer');
END;

-- Total size of all groups in the entry must fit the room.
CREATE TRIGGER trg_entry_group_capacity
BEFORE INSERT ON timetable_entry_groups
WHEN (
    COALESCE((SELECT SUM(g.size)
                FROM timetable_entry_groups eg
                JOIN student_groups g ON g.id = eg.group_id
               WHERE eg.entry_id = NEW.entry_id), 0)
    + (SELECT size FROM student_groups WHERE id = NEW.group_id)
) > (SELECT r.capacity
       FROM timetable_entries e
       JOIN rooms r ON r.id = e.room_id
      WHERE e.id = NEW.entry_id)
BEGIN
    SELECT RAISE(ABORT, 'Room capacity exceeded by the groups in this entry');
END;

-- The group must actually take the course.
CREATE TRIGGER trg_entry_group_takes_course
BEFORE INSERT ON timetable_entry_groups
WHEN NOT EXISTS (
    SELECT 1
      FROM timetable_entries e
      JOIN course_groups cg ON cg.course_id = e.course_id
     WHERE e.id = NEW.entry_id AND cg.group_id = NEW.group_id
)
BEGIN
    SELECT RAISE(ABORT, 'This group is not enrolled in the entry''s course');
END;

-- ---------------------------------------------------------------------
-- Convenience views (used by the API and the timetable pages)
-- ---------------------------------------------------------------------

CREATE VIEW v_timetable_full AS
SELECT  t.id            AS timetable_id,
        t.status        AS timetable_status,
        e.id            AS entry_id,
        ts.day_of_week,
        ts.start_time,
        ts.end_time,
        c.code          AS course_code,
        c.name          AS course_name,
        l.name          AS lecturer,
        r.name          AS room,
        g.id            AS group_id,
        g.name          AS group_name
FROM timetable_entries e
JOIN timetables t               ON t.id  = e.timetable_id
JOIN time_slots ts              ON ts.id = e.time_slot_id
JOIN courses c                  ON c.id  = e.course_id
JOIN lecturers l                ON l.id  = e.lecturer_id
JOIN rooms r                    ON r.id  = e.room_id
JOIN timetable_entry_groups eg  ON eg.entry_id = e.id
JOIN student_groups g           ON g.id  = eg.group_id;
