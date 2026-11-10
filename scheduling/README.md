# scheduling/  (Tickets 9 and 10)

The brain of the project: turns courses, lecturers, rooms and groups into a timetable.
**Pure Python. No Flask, no SQL outside `loader.py`.** That keeps it easy to unit test.

```
scheduling/
├── models.py        plain data classes: the shared vocabulary           [done]
├── loader.py        database -> Problem, Solution -> database           [Ticket 9]
├── constraints.py   hard-constraint checks and the soft-constraint score [Tickets 9 + 10]
├── backtracking.py  finds ANY clash-free timetable                      [Ticket 9]
├── genetic.py       improves it using the soft-constraint score         [Ticket 10]
└── generate.py      the one function the backend calls                  [Tickets 9 + 10]
```

## Pipeline

```
database --loader--> Problem --backtracking--> Solution --genetic--> better Solution --loader--> database
```

1. `loader.load_problem(db_path)` reads courses, groups, rooms and non-break slots.
2. `backtracking.solve(problem)` returns a `Solution` that breaks no hard rule, or `None` if impossible.
3. `genetic.optimise(problem, solution)` keeps it valid while raising the soft-constraint score.
4. `loader.save_solution(...)` writes a new *draft* timetable. The backend never sees algorithm details.

## The contract with the backend (agree this first)

```python
generate_timetable(db_path: str, name: str, semester: int, academic_year: int) -> GenerateResult
# GenerateResult: timetable_id, score, feasible, message
```

The backend only calls this one function. Both sides can build in parallel against it.

## Hard rules (must never be broken; the database also enforces them)

1. A lecturer teaches one thing at a time.
2. A room hosts one class at a time.
3. A student group attends one class at a time.
4. No classes in break slots (`time_slots.is_break = 1`).
5. Total students in the entry fit the room capacity.
6. A course's weekly hours are all placed, and `block_hours` blocks stay consecutive on one day.
7. Locked entries (`is_locked = 1`) are never moved.

## Facts from the real Richfield timetables that the solver must handle

- The same lecturer teaches across several year groups, so solve **all years together**.
- Some classes are combined (several groups in one entry).
- Practicals run as 2-hour blocks; the same course can appear in a lecture room and a lab.
  `preferred_room_type` is a soft preference, not a hard rule.
- 3rd year runs several modules in the same slot (elective streams modelled as sub-groups).

## Suggested working order

1. Finish `loader.load_problem` and test it against the seeded database.
2. Write `constraints.py` hard checks, then a tiny hand-made problem to test them.
3. Build `backtracking.solve` (try most-constrained courses first).
4. Check it can rebuild a clash-free version of the BSc 1 Group 1 timetable.
5. Define the fitness function in `docs/solver-design.md`, then build `genetic.py`.
