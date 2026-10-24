# Intelligent Timetable Generator

Final Year Project, Richfield Graduate Institute of Technology.
Generates clash-free university timetables with a backtracking solver (hard constraints)
and a genetic algorithm (soft constraints), behind a Flask API and a web interface.

## Folder map

| Folder | What lives here | Tickets |
|---|---|---|
| `backend/` | Flask app: login, roles, CRUD API, generate/publish endpoints | 5, 6 |
| `frontend/` | HTML/CSS/JS pages: login, admin screens, timetable views | 3, 4 |
| `scheduling/` | The solver and optimiser (pure Python, no Flask) | 9, 10 |
| `database/` | Schema, migrations, seed data, build script | 7, 8 |
| `tests/` | Automated tests, run by CI on every pull request | 11 |
| `docs/` | Team workflow, API contract, solver design, test plan, deployment, demo | 1, 2, 6, 10, 11, 12 |
| `.github/` | CI workflow, PR template, weekly check-in template | 1, 2, 11 |

Every folder has its own `README.md` explaining what to build there. Every file marked
`TODO (Ticket N)` is waiting for the person who owns that ticket.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python database/build_db.py          # builds database/timetable.db with seed data
python -m pytest tests -v            # should pass before you change anything
python backend/run.py                # starts the API on http://127.0.0.1:5000
```

Then open `http://127.0.0.1:5000/api/health`; it should answer `{"status": "ok"}`.

## Branch rules (short version; full version in docs/team-workflow.md)

- Never push to `main`. Branch from `dev`: `feature/<ticket-number>-<short-name>`.
- Open a pull request into `dev`. One teammate reviews. CI must be green.
