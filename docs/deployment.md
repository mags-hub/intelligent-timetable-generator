# Deployment and architecture  (Ticket 12)

## Hosting decision (TEAM TO DECIDE, not yet decided)

| Option | Good for | Watch out for |
|---|---|---|
| Run locally for the demo | simplest, no cost, no risk of an outage | supervisor cannot try it afterwards |
| PythonAnywhere (free tier) | quick Flask hosting, SQLite works | limited CPU for long solver runs |
| Render / Railway | easy Git deploys | free tiers sleep; SQLite files may reset, so persistent disk or Postgres needed |
| University server | stays with the institution | needs IT permission and time |

TODO: record the decision, the date and the reason here. **Decide early**: it affects the
database engine (see `docs/database-schema.md`: moving off SQLite means rewriting the triggers).

## Architecture overview
TODO: add a diagram. Current shape:

```
Browser (frontend/)  <--HTTP/JSON-->  Flask (backend/)  --->  scheduling/ engine
                                           |
                                      SQLite (database/)
```

## Setup guide for a new machine
TODO: confirm and complete.
1. Install Python 3.12
2. `pip install -r requirements.txt`
3. `python database/build_db.py`
4. `python backend/run.py`
5. Open `http://127.0.0.1:5000/login.html`

## Production checklist
- [ ] `SECRET_KEY` set through the environment, never committed
- [ ] Dev accounts from `build_db.py` removed or their passwords changed
- [ ] `debug=False` (change `backend/run.py`)
- [ ] Database backed up, and not stored inside a folder that redeploys wipe
- [ ] HTTPS enabled by the host
