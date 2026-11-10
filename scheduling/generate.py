"""The single entry point the backend calls.  Tickets 9 and 10"""
from . import loader
from .backtracking import solve_with_reason
from .constraints import soft_score
from .genetic import GAParams, optimise
from .models import GenerateResult


def generate_timetable(db_path: str, name: str, semester: int, academic_year: int,
                       ga_params: GAParams | None = None, improve: bool = True) -> GenerateResult:
    """Load the data, find a clash-free timetable, improve it and save it as a new draft.

    improve=False skips the genetic algorithm (faster; the timetable is valid but not tuned).
    """
    problem = loader.load_problem(db_path)
    solution, message = solve_with_reason(problem)
    if solution is None:
        return GenerateResult(feasible=False, message=message)

    if improve:
        solution = optimise(problem, solution, ga_params)
    else:
        solution.score = soft_score(problem, solution)

    timetable_id = loader.save_solution(db_path, solution, name, semester, academic_year)
    return GenerateResult(feasible=True, message="ok", timetable_id=timetable_id, score=solution.score)
