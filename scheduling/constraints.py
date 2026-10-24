"""Rules and scoring.  TODO (Tickets 9 and 10)"""
from .models import Problem, Solution


def hard_violations(problem: Problem, solution: Solution) -> list[str]:
    """Return a readable message for every broken hard rule. Empty list = valid.

    TODO (Ticket 9): check lecturer / room / group overlaps, capacity, break slots,
    weekly hours placed, and consecutive blocks. Used by unit tests and by the GA to
    reject invalid children.
    """
    raise NotImplementedError("TODO Ticket 9: hard_violations")


def is_valid(problem: Problem, solution: Solution) -> bool:
    return not hard_violations(problem, solution)


def soft_score(problem: Problem, solution: Solution) -> float:
    """Higher is better.

    TODO (Ticket 10): combine weighted soft goals, for example
      - fewer gaps in a group's day
      - lecturer workload spread across the week
      - preferred room type used (labs for programming)
      - no very early or very late classes where avoidable
    Write the final formula and weights in docs/solver-design.md.
    """
    raise NotImplementedError("TODO Ticket 10: soft_score")
