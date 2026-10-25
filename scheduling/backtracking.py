"""Backtracking constraint solver (Ticket 9).

Idea: break every course into blocks (a 4-hour course with 2-hour blocks is two blocks),
then place the blocks one at a time. Each time, pick the block that has the FEWEST legal
places left (the most constrained one), try its options in a sensible order, and recurse.
If a block ever has no legal place, undo the last placement and try its next option.
"""
import time
from collections import defaultdict

from .constraints import _group_chain
from .models import Assignment, Problem, Solution


class _TimeUp(Exception):
    """Raised inside the search when the time limit is reached."""


def solve(problem: Problem, time_limit_s: float = 30.0) -> Solution | None:
    """Return a hard-constraint-valid Solution, or None if none exists or time runs out."""
    return solve_with_reason(problem, time_limit_s)[0]


def solve_with_reason(problem: Problem, time_limit_s: float = 30.0) -> tuple[Solution | None, str]:
    """Like solve(), but also returns a message the admin can read.

    Returns (solution, "ok") on success, or (None, "<why it failed>").
    """
    deadline = time.monotonic() + time_limit_s

    courses = {c.id: c for c in problem.courses}
    rooms = {r.id: r for r in problem.rooms}
    groups = {g.id: g for g in problem.groups}
    slots = {s.id: s for s in problem.slots}
    slot_order = {s.id: i for i, s in enumerate(problem.slots)}

    # ---- group conflicts: a group clashes with itself, its parents and its sub-groups ----
    conflicts: dict[int, set[int]] = {}
    for g in groups:
        conflicts[g] = set(_group_chain(g, groups))
    for g in groups:
        for ancestor in _group_chain(g, groups):
            conflicts[ancestor].add(g)

    # ---- windows: runs of L back-to-back slots on one day ----
    by_day = defaultdict(list)
    for s in problem.slots:
        by_day[s.day].append(s)
    for day_slots in by_day.values():
        day_slots.sort(key=lambda s: s.start)

    windows_cache: dict[int, list[tuple[int, ...]]] = {}

    def windows(length: int) -> list[tuple[int, ...]]:
        if length not in windows_cache:
            found = []
            for day_slots in by_day.values():
                for i in range(len(day_slots) - length + 1):
                    run = day_slots[i:i + length]
                    if all(a.end == b.start for a, b in zip(run, run[1:])):
                        found.append(tuple(s.id for s in run))
            found.sort(key=lambda w: slot_order[w[0]])
            windows_cache[length] = found
        return windows_cache[length]

    # ---- which rooms can hold each course, best choice first ----
    students = {c.id: sum(groups[g].size for g in c.group_ids if g in groups) for c in problem.courses}

    def room_rank(course, room):
        wanted = course.preferred_room_type
        return 0 if wanted is None or room.room_type == wanted else 1

    eligible: dict[int, list] = {}
    for c in problem.courses:
        fits = [r for r in problem.rooms if r.capacity >= students[c.id]]
        fits.sort(key=lambda r: (room_rank(c, r), r.capacity, r.id))
        eligible[c.id] = fits

    # ---- state: who is busy when ----
    lecturer_busy: set[tuple[int, int]] = set()
    room_busy: set[tuple[int, int]] = set()
    group_busy: dict[int, set[int]] = defaultdict(set)
    course_day: dict[tuple[int, int], int] = defaultdict(int)
    group_day: dict[tuple[int, int], int] = defaultdict(int)
    placed: list[Assignment] = []

    def occupy(course, room_id, slot_id):
        lecturer_busy.add((course.lecturer_id, slot_id))
        room_busy.add((room_id, slot_id))
        group_busy[slot_id].update(course.group_ids)
        day = slots[slot_id].day
        course_day[(course.id, day)] += 1
        for g in course.group_ids:
            group_day[(g, day)] += 1

    def release(course, room_id, slot_id):
        lecturer_busy.discard((course.lecturer_id, slot_id))
        room_busy.discard((room_id, slot_id))
        group_busy[slot_id].difference_update(course.group_ids)
        day = slots[slot_id].day
        course_day[(course.id, day)] -= 1
        for g in course.group_ids:
            group_day[(g, day)] -= 1

    # ---- quick checks that give a clear message straight away ----
    for c in problem.courses:
        if c.weekly_hours > 0 and not eligible[c.id]:
            return None, (f"No room is large enough for {c.code} "
                          f"({students[c.id]} students)")

    hours_by_lecturer: dict[int, int] = defaultdict(int)
    for c in problem.courses:
        hours_by_lecturer[c.lecturer_id] += c.weekly_hours
    for lecturer_id, hours in hours_by_lecturer.items():
        if hours > len(problem.slots):
            return None, (f"Lecturer {lecturer_id} has {hours} weekly hours "
                          f"but there are only {len(problem.slots)} teaching slots")

    total_hours = sum(c.weekly_hours for c in problem.courses)
    room_slots = len(problem.rooms) * len(problem.slots)
    if total_hours > room_slots:
        return None, (f"{total_hours} class hours need a room, but there are only "
                      f"{room_slots} room-and-slot places ({len(problem.rooms)} rooms x "
                      f"{len(problem.slots)} slots). Add rooms or slots.")

    # ---- locked entries are placed first and never move ----
    locked_hours: dict[int, int] = defaultdict(int)
    for a in problem.locked:
        c = courses.get(a.course_id)
        if c is None or a.slot_id not in slots or a.room_id not in rooms:
            return None, "A locked entry refers to a course, room or slot that does not exist"
        if ((c.lecturer_id, a.slot_id) in lecturer_busy or (a.room_id, a.slot_id) in room_busy
                or any(conflicts[g] & group_busy[a.slot_id] for g in c.group_ids if g in conflicts)):
            return None, f"Locked entries clash with each other ({c.code})"
        occupy(c, a.room_id, a.slot_id)
        placed.append(a)
        locked_hours[c.id] += 1

    # ---- turn every course into blocks ----
    blocks: list[tuple] = []  # (course, length)
    for c in problem.courses:
        remaining = c.weekly_hours - locked_hours[c.id]
        size = max(c.block_hours, 1)
        for _ in range(remaining // size):
            blocks.append((c, size))
        if remaining % size:
            blocks.append((c, remaining % size))
    for c, length in blocks:
        if not windows(length):
            return None, f"{c.code} needs a {length}-hour block but no {length} back-to-back slots exist"

    # ---- finding legal places for a block ----
    def legal_options(c, length, limit=None):
        """Every (window, room) where the block fits, best first. Stops early at `limit`."""
        found = []
        for window in windows(length):
            if any((c.lecturer_id, s) in lecturer_busy for s in window):
                continue
            if any(conflicts[g] & group_busy[s] for s in window for g in c.group_ids if g in conflicts):
                continue
            for room in eligible[c.id]:
                if any((room.id, s) in room_busy for s in window):
                    continue
                found.append((window, room))
                if limit is not None and len(found) >= limit:
                    return found
        return found

    def preference(c, option):
        window, room = option
        day = slots[window[0]].day
        return (
            room_rank(c, room),                                   # preferred room type first
            course_day[(c.id, day)],                              # avoid the same course twice a day
            sum(group_day[(g, day)] for g in c.group_ids),        # spread each group over the week
            slot_order[window[0]],                                # earlier in the week
            room.capacity,                                        # smallest room that fits
        )

    dead_ends: dict[int, int] = defaultdict(int)

    def search(remaining: list[int]) -> bool:
        if time.monotonic() > deadline:
            raise _TimeUp
        if not remaining:
            return True

        # Pick the block with the fewest legal options (most constrained first).
        best_index, best_count = None, None
        for index in remaining:
            c, length = blocks[index]
            cap = None if best_count is None else best_count
            count = len(legal_options(c, length, limit=cap))
            if count == 0:
                dead_ends[c.id] += 1
                return False
            if best_count is None or count < best_count:
                best_index, best_count = index, count
                if count == 1:
                    break

        c, length = blocks[best_index]
        options = legal_options(c, length)
        options.sort(key=lambda o: preference(c, o))
        rest = [i for i in remaining if i != best_index]

        for window, room in options:
            for s in window:
                occupy(c, room.id, s)
                placed.append(Assignment(c.id, room.id, s))
            if search(rest):
                return True
            for s in reversed(window):
                placed.pop()
                release(c, room.id, s)
        dead_ends[c.id] += 1
        return False

    try:
        found = search(list(range(len(blocks))))
    except _TimeUp:
        return None, (f"No timetable was found within {time_limit_s:g} seconds. "
                      "The data may be too tight (too few rooms or slots).")

    if not found:
        hardest = max(dead_ends, key=dead_ends.get) if dead_ends else None
        name = courses[hardest].code if hardest is not None else "a course"
        return None, (f"No clash-free timetable exists for this data. "
                      f"{name} is the hardest to fit: check its lecturer, groups and room sizes.")

    placed.sort(key=lambda a: (a.course_id, slot_order[a.slot_id]))
    return Solution(list(placed)), "ok"
