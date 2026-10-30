"""Genetic algorithm optimiser.  TODO (Ticket 10)"""
from dataclasses import dataclass

from .models import Problem, Solution


@dataclass
class GAParams:
    population_size: int = 50
    generations: int = 200
    mutation_rate: float = 0.05
    crossover_rate: float = 0.8
    elite_size: int = 2
    seed: int | None = 42         # fixed seed = repeatable results for tests and the report


def optimise(problem: Problem, start: Solution, params: GAParams | None = None) -> Solution:
    """Improve `start` without ever breaking a hard rule.

    TODO (Ticket 10):
      - build the initial population from `start` plus mutated copies
      - fitness = constraints.soft_score
      - selection (tournament), crossover, mutation (move one session to another slot/room)
      - reject or repair any child that fails constraints.is_valid
      - never move locked entries
      - keep the best solution found; return it (never worse than `start`)
    Record parameters and results in docs/solver-design.md for the final report.
    """
    raise NotImplementedError("TODO Ticket 10: optimise")
