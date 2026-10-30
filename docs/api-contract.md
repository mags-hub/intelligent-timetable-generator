# API contract  (Ticket 6)

The agreement between `backend/` and `frontend/`. Change it here first, then in the code.
All bodies are JSON. Errors look like `{"error": "readable message"}`.

Status codes: 200 ok, 201 created, 400 bad input, 401 not signed in, 403 wrong role,
404 not found, 409 conflict (a clash or duplicate), 422 cannot generate, 501 not built yet.

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
| PUT | `/api/<resource>/<id>` | updated row |
| DELETE | `/api/<resource>/<id>` | `{}`; 409 if still referenced |

Fields per resource are the column names in `docs/database-schema.md`.
TODO (Ticket 6): list required and optional fields and validation rules per resource.

## Timetables

| Method | URL | Who | Notes |
|---|---|---|---|
| POST | `/api/timetables/generate` | admin | body `{semester, academic_year}` -> 201 `{timetable_id, status: "draft", score}`; 422 if infeasible |
| GET | `/api/timetables` | admin | list of drafts and published |
| GET | `/api/timetables/<id>` | admin any; others published only | `{id, name, status, entries: [...]}` |
| PUT | `/api/timetables/<id>/entries/<entry_id>` | admin | body `{room_id, time_slot_id}`; 409 on clash |
| POST | `/api/timetables/<id>/publish` | admin | archives the previously published one |
| GET | `/api/timetables/published/mine` | lecturer, student | `{published: bool, entries: [...]}` for the current user |

Entry shape (from the `v_timetable_full` view):
`{entry_id, day_of_week, start_time, end_time, course_code, course_name, lecturer, room, group_id, group_name}`

TODO (Ticket 6): add a real example response for each endpoint once it works.
