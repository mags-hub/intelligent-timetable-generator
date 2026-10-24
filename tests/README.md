# tests/  (Ticket 11)

Everything here runs automatically on every pull request (`.github/workflows/ci.yml`).
Run locally from the repo root:

```bash
python -m pytest tests -v
```

| File | Covers | Status |
|---|---|---|
| `test_database_constraints.py` | schema rejects clashes, break slots, bad roles | done (Ticket 7/8) |
| `test_smoke.py` | app starts, health check, frontend served, protected routes closed | done |
| `test_auth.py` | login, logout, roles | skipped until Ticket 5 |
| `test_crud_api.py` | five CRUD resources | skipped until Ticket 6 |
| `test_solver.py` | backtracking solver | skipped until Ticket 9 |
| `test_genetic.py` | genetic algorithm | skipped until Ticket 10 |
| `test_integration.py` | generate -> publish -> view, end to end | skipped until Tickets 5, 6, 9 |

## How to use the skipped tests

Each skipped test is a sentence describing one behaviour. When you build your ticket:
1. delete the `@pytest.mark.skip(...)` line,
2. write the body so it fails without your code and passes with it,
3. keep it in the same pull request as the feature.

A module is not "done" until its tests are un-skipped and passing. See `docs/test-plan.md`.

## Shared fixtures (`conftest.py`)

- `app`: a Flask app wired to a **fresh, seeded database** built for that one test.
- `client`: a test client for `app`. Use `client.get("/api/...")`.
- `db_path`: the path of that test database, for solver tests that read it directly.
