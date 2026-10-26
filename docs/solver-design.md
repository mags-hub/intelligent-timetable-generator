# Solver design  (Tickets 9 and 10)

Fill this in as you build. It becomes a chapter of the final report.

## 1. Problem definition

**Input.** A `Problem` object built by `loader.load_problem` from the database:

- courses: code, lecturer, weekly hours, block size (1 or 2 hours), the student groups that attend it, and a preferred room type
- rooms: name, capacity and type (lecture room, lab or auditorium)
- student groups: name, size and an optional parent group (used for elective streams)
- teaching slots: one-hour slots from Monday to Friday. Break slots (lunch) are removed before the solver sees them.
- locked entries: classes that must stay exactly where they are (none are loaded yet)

**Output.** A `Solution`: a list of assignments. Each assignment puts one course in one room in one one-hour slot. A 2-hour practical therefore appears as two assignments in back-to-back slots. If no valid timetable exists, the solver returns nothing and gives a readable reason.

**Size of the real problem.** The seeded Richfield data has 21 courses with 76 weekly class hours, 8 lecturers, 3 student groups, 10 rooms and 35 usable teaching slots across the three year groups. All years are solved together, because the same lecturer teaches across several year groups.

## 2. Hard constraints

A timetable is only valid if none of these rules is broken. `constraints.hard_violations` checks all of them and returns a readable message for every rule that is broken. The database also enforces most of them with unique constraints and triggers.

1. A lecturer teaches one thing at a time.
2. A room hosts one class at a time.
3. A student group attends one class at a time.
4. No classes in break slots.
5. The students in a class must fit the room. For a combined class the room must hold the sum of the group sizes.
6. All of a course's weekly hours are placed, and multi-hour blocks stay back to back on one day. A block cannot be split by the lunch break, because the slots on either side of it do not touch.
7. Locked entries are never moved.

Rules found while building:

- **A group clashes with its parent and its sub-groups.** A class for BSC3 involves the same students as a class for one of its elective streams, so they cannot share a slot. Two sibling streams are different students and may share a slot, which is how the 3rd year runs several modules at the same time.
- **A lecturer cannot have more weekly hours than there are teaching slots**, and the total class hours cannot exceed rooms x slots. These are checked first so impossible data fails immediately with a clear message.
- **The preferred room type is a soft preference, not a hard rule.** The same course can appear in a lecture room and a lab in the real timetables.

## 3. Backtracking solver (Ticket 9)

**Approach.** Backtracking search with a "most constrained first" ordering. The idea is to place the classes that are hardest to fit while there is still space, and to undo and retry whenever a class turns out to have no legal place.

**Step by step.**

1. **Split courses into blocks.** A course with 4 weekly hours and 2-hour blocks becomes two blocks of 2 hours. A course with 1-hour blocks becomes four blocks of 1 hour. Any leftover hours form one shorter block.
2. **Find the possible places for each block length.** A place is a window of back-to-back slots on one day, so a 2-hour block can never straddle lunch or jump to another day.
3. **Pre-compute which rooms can hold each course**, meaning rooms with capacity at least the total size of the groups attending. Rooms are sorted with the preferred room type first and then the smallest room.
4. **Quick checks.** If there is no room big enough for a course, a lecturer has too many hours, there are not enough room-and-slot places, or a block length has no window, the solver stops immediately with a message.
5. **Place locked entries first.** They are never moved.
6. **Search.** At each step the solver counts the legal places left for every unplaced block and picks the block with the fewest. If any block has none, that branch is a dead end and the solver goes back. Otherwise the solver tries the chosen block's options in order of preference and moves on to the next block. A legal place is one where the lecturer, the room and every attending group are free in all slots of the window.
7. **Undo on a dead end.** When a block cannot be placed, the last placement is removed and its next option is tried. This is the backtracking.

**Order in which options are tried for a block** (so the first solution found is already reasonable):

1. the preferred room type first
2. avoid putting the same course twice on one day
3. spread each group's classes across the week
4. earlier in the week
5. the smallest room that fits

**Determinism.** There is no randomness. The same data always gives the same timetable, which makes the tests repeatable.

**Infeasibility and time limits.** `solve` returns `None` when no valid timetable exists or the time limit is reached (30 seconds by default). `solve_with_reason` returns the same result together with a message for the admin, for example "No room is large enough for AAA (30 students)". When the whole search fails, the message names the course that hit the most dead ends, which is usually the best place to look first. The search checks the clock on every step, so it can never hang.

**Known limitations.**

- Locked entries are kept in place, but the solver does not yet keep a locked hour in a back-to-back block with the rest of its course.
- The solver finds any valid timetable. It does not look for the best one. Improving quality is the job of the genetic algorithm (Ticket 10).
- Room capacities and group sizes in the seed data are estimates, so the capacity rule is only as accurate as those numbers.

**Measured results on the real data.**

| Measure | Result |
|---|---|
| Courses placed | 21 (76 class hours) |
| Rooms and slots available | 10 rooms, 35 slots |
| Run time, all years together | about 1 second |
| Hard-rule violations in the result | 0 |
| Automated tests | 26 passing |

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
