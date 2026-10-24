# Demo script  (Ticket 12)

Rehearse this at least twice. Target: 10 minutes. Have a built database ready.

## Before
- [ ] Fresh `python database/build_db.py`
- [ ] Server running, three browser tabs ready (admin, lecturer, student)
- [ ] Backup plan: screen recording of the full flow

## Flow
1. **The problem (1 min).** Show the manual Richfield timetable and why clashes are hard to avoid by hand.
2. **Data (1 min).** Admin signs in; show lecturers, courses, rooms already loaded.
3. **Generate (2 min).** Press Generate; show the draft grid and the score.
4. **Constraints (2 min).** Try to move a class into an occupied room: show the clash message.
5. **Publish (1 min).** Publish the timetable.
6. **Users (2 min).** Sign in as a lecturer, then a student: each sees only their own classes.
7. **Results (1 min).** Compare soft score before vs after the genetic algorithm, and with the manual timetable.

## Likely questions
TODO: list questions from the supervisor and agree who answers (why backtracking plus GA,
how clashes are prevented, what happens with infeasible input, scaling to more courses).
