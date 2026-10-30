-- =====================================================================
-- Seed 001: reference data  (Ticket 8)
-- Source: Richfield Bryanston Semester 2 timetables (BSc 1st, 2nd, 3rd year)
--
-- PLACEHOLDERS TO VERIFY (not shown on the timetables):
--   * room capacities and group sizes are guesses
--   * 'G10 L2' and 'G10 LAB' are treated as separate rooms from 'L2' / 'LAB'
--   * ISM731's full name is not readable in the screenshot
--   * lecturer emails are left empty
-- =====================================================================

PRAGMA foreign_keys = ON;

-- ---- Lecturers (8 appear across the three timetables) ----------------
INSERT INTO lecturers (id, name) VALUES
    (1, 'Pam'),
    (2, 'Kudzai'),
    (3, 'Jonga'),
    (4, 'Bukasa'),
    (5, 'Lebaka'),
    (6, 'Muaaz'),
    (7, 'Kelvin'),
    (8, 'Itu');

-- ---- Rooms -----------------------------------------------------------
INSERT INTO rooms (id, name, capacity, room_type) VALUES
    (1,  'L1',       60,  'lecture'),
    (2,  'L2',       60,  'lecture'),
    (3,  'L6',       60,  'lecture'),
    (4,  'G10 L2',   60,  'lecture'),
    (5,  'LAB1',     40,  'lab'),
    (6,  'LAB2',     40,  'lab'),
    (7,  'LAB3',     40,  'lab'),
    (8,  'LAB4',     40,  'lab'),
    (9,  'G10 LAB',  40,  'lab'),
    (10, 'AUD',      150, 'auditorium');

-- ---- Student groups --------------------------------------------------
INSERT INTO student_groups (id, name, year_level, size) VALUES
    (1, 'BSC1-G1', 1, 35),
    (2, 'BSC2',    2, 35),
    (3, 'BSC3',    3, 35);

-- ---- Time slots: Mon-Fri x 8 one-hour slots (lunch 12:15 is a break) --
WITH RECURSIVE days(d) AS (
    SELECT 1 UNION ALL SELECT d + 1 FROM days WHERE d < 5
),
slots(start_time, end_time, is_break) AS (
    VALUES ('08:15', '09:15', 0),
           ('09:15', '10:15', 0),
           ('10:15', '11:15', 0),
           ('11:15', '12:15', 0),
           ('12:15', '13:15', 1),
           ('13:15', '14:15', 0),
           ('14:15', '15:15', 0),
           ('15:15', '16:15', 0)
)
INSERT INTO time_slots (day_of_week, start_time, end_time, is_break)
SELECT d, start_time, end_time, is_break
FROM days CROSS JOIN slots
ORDER BY d, start_time;

-- ---- Courses ---------------------------------------------------------
-- 1st year (all 4 hrs/week as read from the BSc1 Group 1 timetable)
INSERT INTO courses (id, code, name, year_level, lecturer_id, weekly_hours, block_hours, preferred_room_type) VALUES
    (1,  'WBT512A', 'Web Technology 512',      1, 1, 4, 1, 'lab'),
    (2,  'DSC500',  'Data Science 500',        1, 2, 4, 1, NULL),
    (3,  'INS512A', 'Information Systems 512', 1, 3, 4, 1, 'lecture'),
    (4,  'NET512A', 'Networks 512',            1, 5, 4, 1, 'lecture'),
    (5,  'PRO512A', 'Programming 512',         1, 4, 4, 1, 'lab'),
    (6,  'MAT512',  'Mathematics 512',         1, 4, 4, 1, 'lecture');

-- 2nd year (read from the screenshot; hours per week to confirm)
INSERT INTO courses (id, code, name, year_level, lecturer_id, weekly_hours, block_hours, preferred_room_type) VALUES
    (7,  'SDS600',  'Statistics for Data Sci 600',  2, 2, 4, 1, NULL),
    (8,  'INS622A', 'Information Systems 622',      2, 3, 4, 1, 'lecture'),
    (9,  'STN600',  'Server Technology 600',        2, 6, 4, 1, 'lecture'),
    (10, 'BDI600',  'Big Data & IoT 600',           2, 4, 4, 1, 'lecture'),
    (11, 'PRO622A', 'Programming 622',              2, 6, 4, 1, 'lab'),
    (12, 'BAS622',  'Business Analysis 622',        2, 7, 2, 1, 'lecture'),
    (13, 'MCI600',  'Machine Learning 600',         2, 2, 4, 1, 'lab'),
    (14, 'IPR622A', 'Internet Programming 622',     2, 7, 3, 1, 'lab');

-- 3rd year (screenshot is cropped on the right, so this list may be incomplete)
INSERT INTO courses (id, code, name, year_level, lecturer_id, weekly_hours, block_hours, preferred_room_type, is_elective) VALUES
    (15, 'OPS700',   'Operating Systems 700',  3, 4, 3, 1, 'auditorium', 0),
    (16, 'PRO742',   'Programming 742',        3, 8, 3, 1, 'lab',        0),
    (17, 'NET732',   'Networks 732',           3, 5, 4, 1, 'lab',        0),
    (18, 'ISM731',   'ISM731 (name to confirm)', 3, 6, 2, 1, 'lecture',  0),
    (19, 'ROBOTICS', 'Robotics',               3, 8, 3, 1, 'lecture',    0),
    (20, 'PRO732',   'Programming 732',        3, 6, 4, 1, 'lab',        0),
    (21, 'MAD700',   'Mobile App Development 700', 3, 7, 4, 1, 'lab',    0);

-- ---- Which group takes which course ----------------------------------
INSERT INTO course_groups (course_id, group_id)
SELECT id, 1 FROM courses WHERE year_level = 1;

INSERT INTO course_groups (course_id, group_id)
SELECT id, 2 FROM courses WHERE year_level = 2;

INSERT INTO course_groups (course_id, group_id)
SELECT id, 3 FROM courses WHERE year_level = 3;
