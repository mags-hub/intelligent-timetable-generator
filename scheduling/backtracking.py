"""Backtracking constraint solver.  TODO (Ticket 9)"""
from .models import Problem, Solution


def solve(problem: Problem, time_limit_s: float = 30.0) -> Solution | None:
    """Return a hard-constraint-valid Solution, or None if none exists / time runs out.

    TODO (Ticket 9). Suggested approach:
      1. Expand each course into sessions (weekly_hours / block_hours blocks).
      2. Order sessions most-constrained first (more groups, labs only, shared lecturers).
      3. For each session try (slot, room) options; skip any that break a hard rule.
      4. Recurse; on a dead end, undo the last placement and try the next option.
      5. Stop at `time_limit_s` and report infeasible rather than hanging.
    Keep a `reason` for infeasibility (e.g. "no room fits BAS622 at any slot") so the admin
    gets a useful message from the API.
    """
    raise NotImplementedError("TODO Ticket 9: solve")
