# Test plan  (Ticket 11)

## Levels

| Level | What | Where | Run by |
|---|---|---|---|
| Unit | one function or module in isolation (solver rules, validators) | `tests/` | CI on every PR |
| Integration | modules together (API + database, API + solver) | `tests/test_integration.py` | CI on every PR |
| User acceptance | real users try real tasks | manual, see below | before the demo |

## Coverage by module

| Module | Owner | Test file | Minimum |
|---|---|---|---|
| Database | TODO | `test_database_constraints.py` | every hard constraint has a rejecting test (done) |
| Auth | TODO | `test_auth.py` | each role allowed and blocked correctly |
| API | TODO | `test_crud_api.py` | every endpoint: success, bad input, wrong role |
| Solver | TODO | `test_solver.py` | each hard rule, infeasible input, real data |
| GA | TODO | `test_genetic.py` | improves score, stays valid |
| Frontend | TODO | manual checklist below | every screen |

## Manual frontend checklist
- [ ] Login works for admin, lecturer, student; wrong password shows a clear message
- [ ] Each admin section lists, adds, edits and deletes
- [ ] Generate -> preview -> edit -> publish works end to end
- [ ] Lecturer and student each see only their own classes
- [ ] "No timetable published yet" screen appears when nothing is published
- [ ] Usable at phone width (about 380px)

## User acceptance test (UAT)
TODO: pick 3 to 5 real users (a lecturer, a student, an administrator). Give each a task
("find your Tuesday classes"), watch without helping, record problems and time taken.

## Evaluation against the real timetable
TODO: generate a timetable from the seeded Richfield data and compare with the manual one
(clash count, gaps, lecturer workload, run time).

## CI
`.github/workflows/ci.yml` builds the database and runs `pytest` on every PR to `dev`/`main`.
Merging is blocked on failure once the branch rule from `team-workflow.md` is enabled.
