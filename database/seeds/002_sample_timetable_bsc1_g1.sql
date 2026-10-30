-- =====================================================================
-- Seed 002: sample timetable = the real BSc 1st Year Group 1 timetable
-- (Bryanston, Semester 2). Loading it proves the schema accepts a genuine,
-- clash-free timetable. 24 one-hour entries (6 courses x 4 hours).
-- Run AFTER seed 001.
-- =====================================================================

PRAGMA foreign_keys = ON;

INSERT INTO timetables (id, name, semester, academic_year, status, published_at)
VALUES (1, 'Bryanston BSc1 Group 1 - Semester 2 (imported sample)', 2, 2026, 'published', datetime('now'));

-- Helper pattern: each block inserts the entry, then links the group.
-- Slot / course / room are looked up by their natural keys so the file is readable.


-- Monday
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 1, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'WBT512A' AND r.name = 'LAB4' AND ts.day_of_week = 1 AND ts.start_time = '08:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 2, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'WBT512A' AND r.name = 'LAB4' AND ts.day_of_week = 1 AND ts.start_time = '09:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 3, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'DSC500' AND r.name = 'G10 L2' AND ts.day_of_week = 1 AND ts.start_time = '10:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 4, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'INS512A' AND r.name = 'G10 L2' AND ts.day_of_week = 1 AND ts.start_time = '11:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 5, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'NET512A' AND r.name = 'L2' AND ts.day_of_week = 1 AND ts.start_time = '13:15';

-- Tuesday
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 6, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'PRO512A' AND r.name = 'LAB4' AND ts.day_of_week = 2 AND ts.start_time = '08:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 7, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'MAT512' AND r.name = 'L2' AND ts.day_of_week = 2 AND ts.start_time = '09:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 8, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'INS512A' AND r.name = 'L2' AND ts.day_of_week = 2 AND ts.start_time = '10:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 9, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'NET512A' AND r.name = 'L2' AND ts.day_of_week = 2 AND ts.start_time = '14:15';

-- Wednesday
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 10, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'INS512A' AND r.name = 'L2' AND ts.day_of_week = 3 AND ts.start_time = '08:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 11, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'NET512A' AND r.name = 'G10 L2' AND ts.day_of_week = 3 AND ts.start_time = '09:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 12, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'DSC500' AND r.name = 'L2' AND ts.day_of_week = 3 AND ts.start_time = '10:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 13, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'MAT512' AND r.name = 'L2' AND ts.day_of_week = 3 AND ts.start_time = '11:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 14, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'WBT512A' AND r.name = 'LAB2' AND ts.day_of_week = 3 AND ts.start_time = '13:15';

-- Thursday
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 15, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'WBT512A' AND r.name = 'LAB4' AND ts.day_of_week = 4 AND ts.start_time = '08:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 16, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'INS512A' AND r.name = 'L2' AND ts.day_of_week = 4 AND ts.start_time = '09:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 17, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'PRO512A' AND r.name = 'LAB2' AND ts.day_of_week = 4 AND ts.start_time = '10:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 18, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'PRO512A' AND r.name = 'LAB2' AND ts.day_of_week = 4 AND ts.start_time = '11:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 19, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'DSC500' AND r.name = 'LAB4' AND ts.day_of_week = 4 AND ts.start_time = '13:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 20, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'DSC500' AND r.name = 'LAB4' AND ts.day_of_week = 4 AND ts.start_time = '14:15';

-- Friday
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 21, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'PRO512A' AND r.name = 'LAB2' AND ts.day_of_week = 5 AND ts.start_time = '08:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 22, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'NET512A' AND r.name = 'L2' AND ts.day_of_week = 5 AND ts.start_time = '09:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 23, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'MAT512' AND r.name = 'L2' AND ts.day_of_week = 5 AND ts.start_time = '10:15';
INSERT INTO timetable_entries (id, timetable_id, course_id, lecturer_id, room_id, time_slot_id)
SELECT 24, 1, c.id, c.lecturer_id, r.id, ts.id
FROM courses c, rooms r, time_slots ts
WHERE c.code = 'MAT512' AND r.name = 'L2' AND ts.day_of_week = 5 AND ts.start_time = '11:15';

-- Link every entry to BSC1-G1
INSERT INTO timetable_entry_groups (entry_id, timetable_id, time_slot_id, group_id)
SELECT e.id, e.timetable_id, e.time_slot_id, g.id
FROM timetable_entries e, student_groups g
WHERE e.timetable_id = 1 AND g.name = 'BSC1-G1';
