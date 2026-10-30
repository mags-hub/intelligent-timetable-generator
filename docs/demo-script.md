# Demo script (Ticket 12)

Rehearse at least twice. Target duration: 10 minutes. Build a fresh demo database before rehearsal and confirm that the server and sample accounts work.

## Before the demo

- [ ] Run `python database/build_db.py` (this recreates the demo database; back up anything needed first).
- [ ] Run `python -m pytest tests -v` and note any skipped tests caused by unfinished tickets.
- [ ] Start the app with `python backend/run.py` and confirm `/api/health` returns `{"status":"ok"}`.
- [ ] Prepare separate browser sessions for administrator, lecturer and student.
- [ ] Keep a screen recording or screenshots as a fallback; never include passwords or secrets.

## Ten-minute flow

1. **Problem (1 min):** explain why manual timetable creation makes clashes and workload balancing difficult.
2. **Data (1 min):** sign in as administrator and show the seeded lecturers, courses, rooms and student groups.
3. **Generate (2 min):** generate a draft and explain the timetable and score, distinguishing implemented behaviour from planned functionality.
4. **Constraints (2 min):** demonstrate a conflicting room/slot assignment being rejected, if that endpoint is implemented; otherwise show the database constraint test and state the limitation honestly.
5. **Publish (1 min):** publish the timetable, if the workflow is implemented.
6. **Role-specific views (2 min):** show lecturer and student timetable views and explain role-based filtering.
7. **Results and limitations (1 min):** present measured clash count, score and run time only if measured; mention unfinished tickets and next steps.

## Likely supervisor questions

- **Why backtracking plus a genetic algorithm?** Backtracking searches for a timetable satisfying hard constraints; the genetic algorithm can then improve soft preferences such as reducing gaps or balancing workloads. Hard constraints must remain satisfied after optimisation.
- **How are clashes prevented?** Validate candidate assignments in the solver and enforce database constraints as a final integrity guard. The database remains the last line of defence against conflicting writes.
- **What happens with infeasible input?** The generator should return a clear no-solution result and identify the limiting constraints; it must not publish a partial or invalid timetable as successful.
- **How does it scale?** Runtime depends on activities, candidate slots, constraints and solver settings. Measure representative datasets before making performance claims; consider pruning, better heuristics and time limits.
- **Why SQLite?** It is simple for a local prototype and supports the current schema. A multi-user hosted deployment may need a managed database, but SQLite-specific triggers and views must be migrated and tested.
- **What is production-ready?** The current hosting decision is local demo. Public deployment requires a production WSGI server, HTTPS, a securely configured `SECRET_KEY`, persistent backups and changed demo credentials.

## Presenter roles

Before presenting, assign one person to explain the user problem and requirements, one to demonstrate the application, and one to explain architecture, testing and limitations. If the team is smaller, combine roles. Each presenter should be able to explain their own contribution and answer questions without exposing credentials.
