# Intelligent Timetable Generator

An AI-based constraint satisfaction and optimization system for academic scheduling, developed as a final-year IT degree capstone project at Richfield Graduate Institute of Technology.

## Overview

Many colleges still create timetables manually, a slow, error-prone process that leads to lecturer clashes, room conflicts, and student timetable overlaps. This project automates that process: administrators input courses, lecturers, rooms, time slots and student groups, and the system generates optimized, clash-free timetables automatically. Lecturers and students then log in to view their personalized schedules.

It uses a backtracking solver (hard constraints) and a genetic algorithm (soft constraints), behind a Flask API and a web interface.

## Features

- Admin dashboard to manage lecturers, courses, classrooms, student groups and time slots
- Automated, clash-free timetable generation using constraint-based scheduling
- Optimization for soft constraints (preferred times, workload balancing)
- Lecturer and student login with personalized timetable views

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python (Flask) |
| Scheduling Engine | Python (backtracking + genetic algorithm) |
| Database | SQLite |
| Version Control | Git & GitHub |

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

Every folder has its own `README.md` explaining what lives there.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate            # Windows (Git Bash): source .venv/Scripts/activate
pip install -r requirements.txt
python database/build_db.py          # builds database/timetable.db with seed data and dev logins
python -m pytest tests -v            # should pass before you change anything
python backend/run.py                # starts the app on http://127.0.0.1:5000
```

Then open `http://127.0.0.1:5000/login.html`. Development logins (password `ChangeMe123!`, local use only): `admin`, lecturers such as `bukasa`, and students `student_bsc1`, `student_bsc2`, `student_bsc3`.

## Team

Six-member team, following Agile Scrum. See the [Project board](https://github.com/users/mags-hub/projects/2) for current sprint status and the [Issues](https://github.com/mags-hub/intelligent-timetable-generator/issues) tab for individual tickets.

## Development workflow (short version; full version in docs/team-workflow.md)

1. Never push to `main`. Create a branch off `dev` named after your feature (e.g. `feature/backend-auth`).
2. Commit your work there.
3. Open a Pull Request into `dev`, referencing the issue it closes (e.g. "Closes ticket 5"). One teammate reviews, and CI must be green.
4. Get it reviewed and merged.
5. `dev` is merged into `main` for the final, stable submission.