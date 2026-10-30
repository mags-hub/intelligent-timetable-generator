# Deployment and architecture (Ticket 12)

## Hosting decision

**Decision for the assessed prototype/demo:** run the Flask application locally on the demo machine. The repository uses SQLite, including database triggers, and the project does not yet have an approved university-hosting account or a verified persistent hosted database. Local deployment avoids an unapproved public endpoint and prevents a free host's ephemeral filesystem from losing timetable data.

**Date recorded:** 27 October 2026. **Revisit if:** the supervisor requires remote access or the university provides an approved host. Before moving to a hosted deployment, the team must confirm persistent storage/backups, HTTPS, environment secrets, and whether the database will remain SQLite or be migrated (including rewriting and retesting SQLite-specific triggers).

For any later hosted deployment, keep the frontend and API on the **same origin**: Flask serves the static files from `frontend/`, while `/api/...` serves JSON. This is the simplest deployment for the current app and avoids introducing CORS configuration. Do not deploy the development server as a public production server; use the host's supported WSGI server.

## Architecture overview

```text
User's browser
    |  HTML / CSS / JavaScript
    |  same-origin HTTP requests (/api/...)
    v
Flask application (backend/app)
    |-- authentication and role checks
    |-- CRUD and timetable API
    |-- serves static frontend/ files
    |
    +----> scheduling/ (backtracking solver + genetic optimiser)
    |
    +----> SQLite database (database/timetable.db)
             schema, foreign keys, constraints, views
```

The scheduling package is plain Python and does not depend on Flask. The API translates requests into solver inputs and stores the generated timetable in SQLite.

## Setup guide for a new machine

Prerequisites: Python 3.12 and a terminal. From the repository root:

### Windows (PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python database/build_db.py
python -m pytest tests -v
python backend/run.py
```

### macOS / Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python database/build_db.py
python -m pytest tests -v
python backend/run.py
```

Open `http://127.0.0.1:5000/login.html`. Check `http://127.0.0.1:5000/api/health` returns `{"status":"ok"}`. The database build command recreates the database and seeds demonstration data, so back up any local database before running it again.

## Environment configuration

- `APP_ENV=development` is the default for local work.
- `DATABASE` optionally sets the SQLite database path; otherwise `database/timetable.db` is used.
- `SECRET_KEY` must be set to a long, random, private value when `APP_ENV=production`. The application refuses to start in production without it.

Generate a key locally with `python -c "import secrets; print(secrets.token_hex(32))"` and add it to the host's secret/environment settings. Do not commit it, put it in screenshots, or include it in `.env` files in Git. The development fallback key is for local development only.

## Production readiness checklist

- [ ] Supervisor/team has approved a host and confirmed persistent storage.
- [ ] `APP_ENV=production` and a unique `SECRET_KEY` are configured in the host environment.
- [ ] Development/demo accounts are removed or their passwords changed.
- [ ] The host runs Flask through a production WSGI server, not `app.run()`.
- [ ] `DEBUG` is false; debug tracebacks are not exposed to users.
- [ ] HTTPS is enabled and session cookies are configured securely for the chosen host.
- [ ] Database backups and a restore test are documented.
- [ ] Database constraints and solver tests pass against the deployed database version.
- [ ] Logs, error monitoring, and a rollback procedure are available.
- [ ] If SQLite is replaced, migrate and retest the schema, triggers, and views before release.
