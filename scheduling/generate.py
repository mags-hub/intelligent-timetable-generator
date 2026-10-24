"""The single entry point the backend calls.  TODO (Tickets 9 and 10)"""
from .models import GenerateResult


def generate_timetable(db_path: str, name: str, semester: int, academic_year: int) -> GenerateResult:
    # TODO:
    #   problem  = loader.load_problem(db_path)
    #   solution = backtracking.solve(problem)
    #   if solution is None: return GenerateResult(feasible=False, message="<reason>")
    #   solution = genetic.optimise(problem, solution)          # once Ticket 10 is done
    #   timetable_id = loader.save_solution(db_path, solution, name, semester, academic_year)
    #   return GenerateResult(True, "ok", timetable_id, solution.score)
    raise NotImplementedError("TODO Tickets 9/10: generate_timetable")
