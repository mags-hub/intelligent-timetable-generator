# Test plan (Ticket 11)

## Levels and execution

| Level | What | Where | Run by |
|---|---|---|---|
| Unit | Solver rules, score calculation, validators | `tests/` | Developer locally and CI |
| Integration | API + database and generate/publish/view flow | `tests/test_integration.py` | Developer locally and CI |
| Database integrity | Foreign keys, uniqueness, clash and slot constraints | `tests/test_database_constraints.py` | Developer locally and CI |
| User acceptance | Representative lecturer, student and administrator tasks | Manual checklist below | Team before demo |

Run from the repository root after installing `requirements.txt`:

```bash
python database/build_db.py
python -m pytest tests -v
```

GitHub Actions runs the database build, Python syntax check and pytest suite on pull requests targeting `dev` or `main`, and on pushes to `dev`. In repository Settings, protect `dev` and `main`, enable **Require status checks to pass before merging**, and select the `test` check after its first successful workflow run. This GitHub setting cannot be activated by the workflow file itself.

## Coverage by module

| Module | Test file | Minimum acceptance criteria | Current scope/status |
|---|---|---|---|
| Database | `test_database_constraints.py` | Invalid references, duplicate assignments and hard clashes are rejected | Implemented tests; keep these mandatory |
| Application startup | `test_smoke.py` | Health endpoint, frontend files, and no anonymous access to protected routes | Implemented tests |
| Authentication | `test_auth.py` | Valid/invalid login, logout, current-user response, and role restrictions | Pending Ticket 5; unskip when authentication is implemented |
| CRUD API | `test_crud_api.py` | CRUD success, invalid input, missing records, and role restrictions for each resource | Pending Ticket 6; unskip when endpoints are implemented |
| Solver | `test_solver.py` | Hard constraints always hold; infeasible inputs fail cleanly; seeded data can be scheduled | Pending Ticket 9; unskip when solver is implemented |
| Genetic algorithm | `test_genetic.py` | Validity is preserved and optimisation does not worsen the best score | Pending Ticket 10; unskip when optimiser is implemented |
| End-to-end | `test_integration.py` | Generate, preview, publish, then show the published timetable to the correct user | Pending Tickets 5, 6 and 9; unskip when dependencies are implemented |

Tests skipped because a feature ticket is unfinished must be made active in the same pull request that implements that feature. Do not remove a skip until the test asserts the behaviour and passes. A green CI run does not mean skipped features are complete; review the skip count as well as failures.

## Manual frontend checklist

- [ ] Login works for admin, lecturer and student; an incorrect password shows a clear error.
- [ ] Each admin section lists, adds, edits and deletes records with useful validation errors.
- [ ] Generate → preview → edit → publish works end to end.
- [ ] Lecturer and student accounts see only their own classes.
- [ ] The “No timetable published yet” state appears when no timetable is published.
- [ ] The interface remains usable at a phone width of approximately 380 px.
- [ ] Keyboard focus, labels and error messages are visible and understandable.

## User acceptance test (UAT) procedure

Recruit 3–5 willing participants covering the administrator, lecturer and student roles. Do not record passwords or unnecessary personal data. Give each participant a realistic task, such as “find your Tuesday classes” or “generate and publish a timetable.” Observe without coaching; record task completion, time taken, errors, and comments. Summarise findings and the fixes made before the demo. If real participants are unavailable, record the limitation and perform a clearly labelled team walkthrough rather than claiming a UAT was completed.

## Evaluation against the manual timetable

Using the same seeded Richfield data and the same timetable period, compare the generated timetable with the manual reference. Record: hard-constraint violations (target: zero), number of scheduled activities, lecturer workload distribution, student/group gaps, soft score before and after optimisation, and total generation time. State the machine, input size and algorithm settings so results are reproducible. Do not report performance values until the experiment has actually been run.
