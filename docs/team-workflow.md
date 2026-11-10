# Team workflow  (Tickets 1 and 2)

## One-time GitHub setup (Ticket 1 owner)

1. **Branches:** `main` = what you submit. `dev` = where finished work meets. Create `dev` from `main`.
2. **Protect `main`:** Settings → Branches → Add rule for `main` →
   *Require a pull request before merging* → *Require approvals: 1*.
   Repeat for `dev` so nothing lands there without a review.
3. **Make CI block bad merges (Ticket 11):** in the same rule tick
   *Require status checks to pass before merging* and select the check named **test**
   (it only appears after the first CI run). Failing tests now block merging.
4. **Project board:** Projects → New project → Board view with columns
   **Backlog / In Progress / In Review / Done**.
5. **Issues:** create the 12 tickets as Issues with labels (`frontend`, `backend`, `database`,
   `team-lead`, `testing/QA`), assign each to one owner, and add them all to the board.
6. **Access:** invite all 6 members (Settings → Collaborators).

## Everyday flow

```
git checkout dev && git pull
git checkout -b feature/<ticket-number>-<short-name>     e.g. feature/6-crud-endpoints
... work, commit small and often ...
git push -u origin feature/6-crud-endpoints
open a pull request INTO dev  (the template appears; write "Closes #6")
a teammate reviews -> CI green -> merge
```

Rules:
- Never commit to `main` or `dev` directly.
- Pull `dev` into your branch at least every couple of days so conflicts stay small.
- A pull request should be reviewable in 15 minutes. Split large work.
- Move your card on the board: Backlog → In Progress → In Review → Done.
- Never commit `.db` files, passwords or secret keys.

## Weekly check-in (Ticket 2 owner)

Every week open an issue from the **Weekly check-in** template. Each member answers
"done / in progress / blocked". The team lead updates the board, resolves merge conflicts
between backend and scheduling work, and checks that `dev` still builds and CI is green.

## Suggested build order (so nobody waits)

```
Week 1   1 repo/board  ->  2 check-ins, 11 CI skeleton, 7 schema -> 8 seed
Week 2   9 solver (needs only synthetic data), 3 admin shell (mock data), 5 auth, 6 API
Week 3   10 genetic algorithm (after 9), 4 timetable views (after 5 and 6)
Week 4   12 hosting, docs, demo, polish
```
