# Intelligent Timetable Generator

An AI-based constraint satisfaction and optimization system for academic scheduling, developed as a final-year IT degree capstone project.

## Overview

Many colleges still create timetables manually — a slow, error-prone process that leads to lecturer clashes, room conflicts, and student timetable overlaps. This project automates that process: administrators input courses, lecturers, rooms, time slots and student groups, and the system generates optimized, clash-free timetables automatically. Lecturers and students then log in to view their personalized schedules.

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
| Database | MySQL |
| Version Control | Git & GitHub |

## Project Structure


/frontend    → Admin, lecturer, and student-facing pages
/backend     → Flask app, API routes, authentication
/scheduling  → Constraint solver and genetic algorithm modules
/database    → MySQL schema, migrations, seed data
/docs        → Proposal, diagrams, meeting notes
/tests       → Test suites


## Team

Six-member team, following Agile Scrum. See the [Project board](https://github.com/users/mags-hub/projects/2) for current sprint status and the [Issues](https://github.com/mags-hub/intelligent-timetable-generator/issues) tab for individual tickets.

## Development Workflow

1. Create a branch off dev named after your feature (e.g. feature/backend-auth)
2. Commit your work there
3. Open a Pull Request into dev, referencing the issue it closes (e.g. "Closes ticket 5")
4. Get it reviewed and merged
5. dev is merged into main for the final, stable submission
