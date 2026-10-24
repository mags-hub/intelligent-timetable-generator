"""The ONLY file in scheduling/ that touches the database.  TODO (Ticket 9)"""
from .models import Problem, Solution


def load_problem(db_path: str) -> Problem:
    # TODO (Ticket 9):
    #   - open sqlite3 with PRAGMA foreign_keys = ON
    #   - courses + their groups (course_groups)
    #   - rooms, student_groups, and time_slots WHERE is_break = 0
    #   - locked entries from an existing draft, if regenerating
    #   Build and return a Problem.
    raise NotImplementedError("TODO Ticket 9: load_problem")


def save_solution(db_path: str, solution: Solution, name: str, semester: int, academic_year: int) -> int:
    # TODO (Ticket 9):
    #   - INSERT a timetables row with status 'draft'
    #   - for each assignment INSERT timetable_entries (lecturer comes from the course),
    #     then timetable_entry_groups for the course's groups
    #   - do it all in ONE transaction so a failure leaves nothing half-saved
    #   - return the new timetable id
    raise NotImplementedError("TODO Ticket 9: save_solution")
