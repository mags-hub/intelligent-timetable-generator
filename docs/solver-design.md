# Solver design  (Tickets 9 and 10)

Fill this in as you build. It becomes a chapter of the final report.

## 1. Problem definition
TODO: inputs (courses, lecturers, rooms, groups, slots), outputs (assignments), size of the
real problem (21 courses, 10 rooms, 35 usable slots across three year groups).

## 2. Hard constraints
See `scheduling/README.md` for the list. TODO: add any rule discovered while building, with the
reason (for example: "combined classes need a room for the sum of group sizes").

## 3. Backtracking solver (Ticket 9)
TODO: ordering heuristic used, how blocks are placed, how infeasibility and time limits are reported,
measured run time on the real data.

## 4. Soft constraints and fitness function (Ticket 10)
TODO: write the formula. Example shape:

```
score = w1 * (-gap_hours) + w2 * (-workload_imbalance) + w3 * (preferred_room_matches) + ...
```

| Soft goal | Weight | How it is measured |
|---|---|---|
| TODO | TODO | TODO |

## 5. Genetic algorithm parameters (Ticket 10)

| Parameter | Value | Why |
|---|---|---|
| population_size | 50 | TODO tune |
| generations | 200 | TODO tune |
| mutation_rate | 0.05 | TODO tune |
| crossover_rate | 0.8 | TODO tune |
| elite_size | 2 | TODO tune |

## 6. Results
TODO: soft score before vs after the GA, run time, and a comparison with the manual Richfield
timetable (gaps per group, lecturer workload). This is your strongest evidence for the report.
