# API contract  (Ticket 6)

The agreement between `backend/` and `frontend/`. Change it here first, then in the code.
All bodies are JSON. Errors look like `{"error": "readable message"}`.

Status codes: 200 ok, 201 created, 400 bad input, 401 not signed in, 403 wrong role,
404 not found, 409 conflict (a clash or duplicate), 422 cannot generate, 501 not built yet.

Example values below show the *shape* of each response; the numbers and names are illustrative.

## Auth (Ticket 5)

| Method | URL | Who | Request | Response |
|---|---|---|---|---|
| POST | `/api/auth/login` | anyone | `{username, password}` | `{id, username, role}` |
| POST | `/api/auth/logout` | signed in | none | `{}` |
| GET | `/api/auth/me` | signed in | none | `{id, username, role, lecturer_id, group_id}` |

## Data management (admin only)

Resources: `lecturers`, `courses`, `rooms`, `student-groups`, `time-slots`.

| Method | URL | Response |
|---|---|---|
| GET | `/api/<resource>` | list of rows |
| POST | `/api/<resource>` | 201 + created row |
| GET | `/api/<resource>/<id>` | one row |
| PUT | `/api/<resource>/<id>` | updated row (send the full object, as for POST) |
| DELETE | `/api/<resource>/<id>` | `{}`; 409 if still referenced |

An unknown `<resource>` returns 404.

### Fields per resource

Field names are the column names in `docs/database-schema.md`. Do not send `id`: the database
assigns it, and sending it returns 400.

| Resource | Fields you send | Rules |
|---|---|---|
| `lecturers` | `name`, `email`, `is_active` | `name` and `email` must be unique (409 if not) |
| `courses` | `code`, `name`, `year_level`, `lecturer_id`, `weekly_hours`, `block_hours`, `preferred_room_type`, `is_elective` | `code` unique (409); `year_level`, `weekly_hours`, `block_hours` positive whole numbers, and `block_hours` cannot be more than `weekly_hours` (400); `preferred_room_type` is `lecture`, `lab` or `auditorium`; `lecturer_id` must exist |
| `rooms` | `name`, `capacity`, `room_type`, `campus` | `name` unique (409); `capacity` positive whole number; `room_type` is `lecture`, `lab` or `auditorium` |
| `student-groups` | `name`, `year_level`, `size`, `parent_group_id` | `name` unique (409); `year_level` and `size` positive whole numbers; `parent_group_id` is another group's id or null |
| `time-slots` | `day_of_week`, `start_time`, `end_time`, `is_break` | `day_of_week` is a whole number 1 (Mon) to 5 (Fri) |

General validation (all resources):

- A field is **required** when its column is `NOT NULL` with no default in
  `database/migrations/001_initial_schema.sql`. A missing one returns 400 naming the field.
- An unknown field returns 400 (`Unknown field(s): ...`).
- Text values are trimmed.
- A duplicate (unique) value, or a reference to a record that does not exist, returns 409
  with a readable reason.
- A value that breaks one of the database's CHECK rules (for example `block_hours` more than
  `weekly_hours`) returns 400 with a plain message, not 409.
- `PUT` replaces the whole record, so send **every required field**, the same ones as for
  `POST`, not just the one that changed. A missing one returns 400. The frontend should always
  send the full record.
- An empty string `""` for an optional field is stored as `null`, so two records can both
  leave an optional unique field (such as an email) blank.
- Deleting a record that other records still use (for example a lecturer who still has
  courses, or a room used in a timetable) returns 409.

Example: create a room

```
POST /api/rooms
{"name": "Lab 5", "capacity": 40, "room_type": "lab", "campus": "Bryanston"}

201
{"id": 12, "name": "Lab 5", "capacity": 40, "room_type": "lab", "campus": "Bryanston"}
```

Example: errors

```
POST /api/rooms   {"name": "Lab 5", "capacity": -5, "room_type": "lab", "campus": "Bryanston"}
400  {"error": "'capacity' must be a positive whole number"}

PUT /api/courses/1   (weekly_hours 2, block_hours 4)
400  {"error": "'block_hours' cannot be more than 'weekly_hours'"}

POST /api/rooms   (a room named "Lab 5" already exists)
409  {"error": "Cannot create rooms: a record with the same name already exists."}

DELETE /api/lecturers/3   (lecturer 3 still has courses)
409  {"error": "Cannot delete lecturers/3: other records still depend on it (for example, a lecturer who still has courses, or a room or course used in a timetable). Remove or reassign those first."}

GET /api/rooms/99999
404  {"error": "rooms/99999 not found"}
```

### Course groups (admin only)

Which student groups take a course.

| Method | URL | Request | Response |
|---|---|---|---|
| GET | `/api/courses/<id>/groups` | none | `{course_id, group_ids: [...]}` |
| PUT | `/api/courses/<id>/groups` | `{group_ids: [...]}` | `{course_id, group_ids: [...]}` |

`PUT` replaces the whole list. An empty list returns 400 (a course needs at least one
group). A group id that does not exist returns 409 and the old list
is kept. An unknown course returns 404.

```
PUT /api/courses/1/groups
{"group_ids": [1, 2]}

200
{"course_id": 1, "group_ids": [1, 2]}
```

## Timetables

| Method | URL | Who | Notes |
|---|---|---|---|
| POST | `/api/timetables/generate` | admin | body `{semester, academic_year}` (optional `name`) -> 201 `{timetable_id, status: "draft", score}`; 422 if infeasible |
| GET | `/api/timetables` | admin | list of drafts and published |
| GET | `/api/timetables/<id>` | admin any; others published only | `{id, name, semester, academic_year, status, entries: [...]}`; a draft is 404 for non-admins |
| PUT | `/api/timetables/<id>/entries/<entry_id>` | admin | body `{room_id, time_slot_id}` (either or both); locks the entry; 409 on clash |
| POST | `/api/timetables/<id>/publish` | admin | archives the previously published one for the same semester and year |
| GET | `/api/timetables/published/mine` | any signed-in user | `{published: bool, entries: [...]}` for the current user |

Entry shape (from the `v_timetable_full` view):
`{entry_id, day_of_week, start_time, end_time, course_code, course_name, lecturer, room, group_id, group_name}`

A class shared by several groups (a combined class) appears once per group.

### Generate

```
POST /api/timetables/generate
{"semester": 2, "academic_year": 2026}

201
{"timetable_id": 4, "status": "draft", "score": null}
```

- `semester` and `academic_year` must be positive whole numbers (400 otherwise).
- 422 `{"error": "<reason>"}` when the solver cannot build a clash-free timetable, for
  example when no room is big enough for a group. The reason says why.
- `score` is `null` until the solver returns one.

### List

```
GET /api/timetables

200
[{"id": 4, "name": "Semester 2 2026 draft", "semester": 2, "academic_year": 2026,
  "status": "draft", "created_at": "2026-10-29 18:30:00"}]
```

### Get one timetable

```
GET /api/timetables/4

200
{"id": 4, "name": "Semester 2 2026 draft", "semester": 2, "academic_year": 2026,
 "status": "draft",
 "entries": [{"entry_id": 31, "day_of_week": 1, "start_time": "08:00", "end_time": "09:00",
              "course_code": "ABC101", "course_name": "Example Course",
              "lecturer": "Example Lecturer", "room": "Lab 5",
              "group_id": 1, "group_name": "BSc 1st Year G1"}]}
```

### Edit one entry (manual override)

```
PUT /api/timetables/4/entries/31
{"room_id": 7, "time_slot_id": 12}

200
{"entry_id": 31, "is_locked": 1, "rows": [ ...the entry in the shape above... ]}

409
{"error": "Clash: that room is already used by another class in that time slot."}
```

The entry is locked (`is_locked = 1`), so regenerating does not move it. The 409 reason can
also be one of the database rules, such as "no classes at lunch" or "room too small".

### Publish

```
POST /api/timetables/4/publish

200
{"id": 4, "name": "Semester 2 2026 draft", "semester": 2, "academic_year": 2026,
 "status": "published", "published_at": "2026-10-29 18:45:00", ...}
```

Publishing archives the previous published timetable for the same semester and year.
Publishing one that is already published changes nothing. Only a draft can be published (409
otherwise).

### My timetable

```
GET /api/timetables/published/mine

200  (nothing published yet)
{"published": false, "entries": []}

200  (published; lecturers get their own classes, students get their group's classes,
      admins get the whole timetable)
{"published": true, "timetable_id": 4, "name": "Semester 2 2026 draft", "entries": [ ... ]}
```

If more than one semester is published, the latest semester is returned.

## Errors from the database

Any database rule that is broken (a clash, a duplicate, a missing reference) is returned as
409 `{"error": "..."}` and never as a 500 page.
