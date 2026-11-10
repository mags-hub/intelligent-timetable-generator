# backend/  (Tickets 5 and 6)

The Flask application. It sits between the frontend and the database, and calls the
scheduling engine when an admin generates a timetable.

```
backend/
├── run.py                 starts the dev server (python backend/run.py)
└── app/
    ├── __init__.py        create_app(): builds the Flask app and registers blueprints
    ├── config.py          settings (secret key, database path)
    ├── db.py              one SQLite connection per request, foreign keys ON  [done]
    ├── auth.py            login/logout, role checks                           [Ticket 5]
    └── routes/
        ├── crud.py        create/read/update/delete for the 5 data types      [Ticket 6]
        └── timetable.py   generate, publish, fetch the timetable              [Ticket 6]
```

## Who builds what

- **Ticket 5 (auth):** finish `auth.py`. Login with a session or JWT, three roles
  (`admin`, `lecturer`, `student`), and the `login_required` / `role_required` decorators.
  Dev accounts already exist in the seeded database (see `database/build_db.py`).
- **Ticket 6 (API):** finish `routes/crud.py` and `routes/timetable.py`, then document every
  endpoint in `docs/api-contract.md`. Test with Postman or the pytest client.

## Rules of the road

- All SQL goes through `get_db()` from `db.py`. Never open your own connection.
- The database already rejects clashes (see `docs/database-schema.md`). When it raises
  `sqlite3.IntegrityError`, turn that into a clear 409 response; don't swallow it.
- Always protect routes with `@role_required(...)` once Ticket 5 lands. Until then every
  protected endpoint answers 501 on purpose, so nothing looks secured when it isn't.
- Read published timetables through the `v_timetable_full` view.
- Keep Flask out of `scheduling/`: the engine takes plain Python data in and returns plain
  Python data out. The route only calls `scheduling.generate.generate_timetable(...)`.
