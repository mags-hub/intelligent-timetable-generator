"""The single entry point the backend calls.  Tickets 9 and 10"""
from . import loader
from .backtracking import solve_with_reason
from .models import GenerateResult


def generate_timetable(db_path: str, name: str, semester: int, academic_year: int) -> GenerateResult:
    """Load the data, find a clash-free timetable and save it as a new draft."""
    problem = loader.load_problem(db_path)
    solution, message = solve_with_reason(problem)
    if solution is None:
        return GenerateResult(feasible=False, message=message)

    # TODO (Ticket 10): solution = genetic.optimise(problem, solution)
    #                   and fill in `score` below from constraints.soft_score.
    timetable_id = loader.save_solution(db_path, solution, name, semester, academic_year)
    return GenerateResult(feasible=True, message="ok", timetable_id=timetable_id, score=None)
