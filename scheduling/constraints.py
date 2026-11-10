"""Rules and scoring.  Hard rules: Ticket 9.  soft_score: TODO (Ticket 10)."""
from collections import Counter, defaultdict

from .models import Problem, Solution

DAY_NAMES = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri"}


def _group_chain(group_id: int, groups: dict) -> set[int]:
    """The group itself plus its parent, grandparent, and so on."""
    chain = set()
    while group_id is not None and group_id not in chain:
        chain.add(group_id)
        group = groups.get(group_id)
        group_id = group.parent_id if group else None
    return chain


def _groups_overlap(g1: int, g2: int, groups: dict) -> bool:
    """True if the same students are in both groups.

    A parent group contains its sub-groups, so a class for BSC3 clashes with a
    class for one of its elective streams. Two sibling streams do NOT clash.
    """
    return g2 in _group_chain(g1, groups) or g1 in _group_chain(g2, groups)


def hard_violations(problem: Problem, solution: Solution) -> list[str]:
    """Return a readable message for every broken hard rule. Empty list = valid."""
    courses = {c.id: c for c in problem.courses}
    rooms = {r.id: r for r in problem.rooms}
    groups = {g.id: g for g in problem.groups}
    slots = {s.id: s for s in problem.slots}

    def slot_label(slot_id: int) -> str:
        s = slots[slot_id]
        return f"{DAY_NAMES.get(s.day, s.day)} {s.start}-{s.end}"

    violations: list[str] = []
    usable = []  # assignments whose course, room and slot all exist

    # Rule 4 (and sanity): every assignment must use a real course, room and teaching slot.
    for a in solution.assignments:
        ok = True
        if a.course_id not in courses:
            violations.append(f"Unknown course id {a.course_id} in the timetable")
            ok = False
        if a.room_id not in rooms:
            violations.append(f"Unknown room id {a.room_id} in the timetable")
            ok = False
        if a.slot_id not in slots:
            code = courses[a.course_id].code if a.course_id in courses else a.course_id
            violations.append(
                f"{code} is placed in slot {a.slot_id}, which is a break or does not exist"
            )
            ok = False
        if ok:
            usable.append(a)

    # Rules 1, 2 and 3: nobody (lecturer, room, group) is in two places at once.
    by_slot = defaultdict(list)
    for a in usable:
        by_slot[a.slot_id].append(a)

    for slot_id, here in by_slot.items():
        when = slot_label(slot_id)
        for i in range(len(here)):
            for j in range(i + 1, len(here)):
                a, b = here[i], here[j]
                ca, cb = courses[a.course_id], courses[b.course_id]
                if ca.lecturer_id == cb.lecturer_id:
                    violations.append(
                        f"Lecturer {ca.lecturer_id} teaches {ca.code} and {cb.code} "
                        f"at the same time ({when})"
                    )
                if a.room_id == b.room_id:
                    violations.append(
                        f"Room {rooms[a.room_id].name} hosts {ca.code} and {cb.code} "
                        f"at the same time ({when})"
                    )
                clashing = sorted(
                    groups[g1].name
                    for g1 in ca.group_ids
                    for g2 in cb.group_ids
                    if g1 in groups and g2 in groups and _groups_overlap(g1, g2, groups)
                )
                for name in dict.fromkeys(clashing):
                    violations.append(
                        f"Group {name} has {ca.code} and {cb.code} at the same time ({when})"
                    )

    # Rule 5: the students in a class must fit the room.
    for a in usable:
        course = courses[a.course_id]
        students = sum(groups[g].size for g in course.group_ids if g in groups)
        room = rooms[a.room_id]
        if students > room.capacity:
            violations.append(
                f"{course.code} has {students} students but room {room.name} "
                f"holds {room.capacity} ({slot_label(a.slot_id)})"
            )

    # Rule 6: all weekly hours placed, and multi-hour blocks stay back to back on one day.
    placed = Counter(a.course_id for a in solution.assignments if a.course_id in courses)
    for course in problem.courses:
        if placed[course.id] != course.weekly_hours:
            violations.append(
                f"{course.code}: {placed[course.id]} of {course.weekly_hours} weekly hours placed"
            )

    for course in problem.courses:
        if course.block_hours <= 1:
            continue
        per_day = defaultdict(list)
        for a in usable:
            if a.course_id == course.id:
                s = slots[a.slot_id]
                per_day[s.day].append(s)
        for day, day_slots in per_day.items():
            day_slots.sort(key=lambda s: s.start)
            run = 1
            runs = []
            for prev, nxt in zip(day_slots, day_slots[1:]):
                if prev.end == nxt.start:
                    run += 1
                else:
                    runs.append(run)
                    run = 1
            runs.append(run)
            if any(r % course.block_hours for r in runs):
                violations.append(
                    f"{course.code}: hours on {DAY_NAMES.get(day, day)} are not in "
                    f"back-to-back blocks of {course.block_hours}"
                )

    # Rule 7: locked entries never move.
    present = set(solution.assignments)
    for locked in problem.locked:
        if locked not in present:
            code = courses[locked.course_id].code if locked.course_id in courses else locked.course_id
            violations.append(f"Locked entry for {code} was moved or removed")

    return violations


def is_valid(problem: Problem, solution: Solution) -> bool:
    return not hard_violations(problem, solution)


class SoftScorer:
    """Scores how pleasant a valid timetable is. Higher is better, 0 is perfect.

    Built once per Problem so the genetic algorithm can score thousands of
    timetables quickly. Each goal is counted, multiplied by its weight and subtracted.
    """

    WEIGHTS = {"gaps": 3, "load": 2, "rooms": 2, "type": 1, "late": 1}

    def __init__(self, problem: Problem, weights: dict | None = None):
        self.weights = dict(self.WEIGHTS, **(weights or {}))
        self.courses = {c.id: c for c in problem.courses}
        self.rooms = {r.id: r for r in problem.rooms}
        self.slots = {s.id: s for s in problem.slots}
        groups = {g.id: g for g in problem.groups}

        # position of every teaching slot inside its day (lunch is not a slot, so it is never a gap)
        by_day = defaultdict(list)
        for s in problem.slots:
            by_day[s.day].append(s)
        self.days = sorted(by_day)
        self.position = {}
        self.last_position = {}
        for day, day_slots in by_day.items():
            day_slots.sort(key=lambda s: s.start)
            for i, s in enumerate(day_slots):
                self.position[s.id] = i
            self.last_position[day] = len(day_slots) - 1

        # a class for a group is also attended by every sub-group of it
        self.audience = {g: {g} for g in groups}
        for g in groups:
            for ancestor in _group_chain(g, groups):
                self.audience[ancestor].add(g)

    def components(self, assignments) -> dict:
        group_day = defaultdict(set)      # (group, day) -> positions of its classes
        lecturer_day = defaultdict(int)   # (lecturer, day) -> hours taught
        rooms_used = defaultdict(set)     # course -> rooms used
        wrong_type = 0
        late = 0
        for a in assignments:
            course = self.courses.get(a.course_id)
            slot = self.slots.get(a.slot_id)
            room = self.rooms.get(a.room_id)
            if course is None or slot is None or room is None:
                continue
            pos = self.position[slot.id]
            for g in course.group_ids:
                for member in self.audience.get(g, ()):
                    group_day[(member, slot.day)].add(pos)
            lecturer_day[(course.lecturer_id, slot.day)] += 1
            rooms_used[course.id].add(room.id)
            if course.preferred_room_type and room.room_type != course.preferred_room_type:
                wrong_type += 1
            if pos == self.last_position[slot.day]:
                late += 1

        gaps = sum(max(p) - min(p) + 1 - len(p) for p in group_day.values())

        per_lecturer = defaultdict(lambda: {d: 0 for d in self.days})
        for (lecturer, day), hours in lecturer_day.items():
            per_lecturer[lecturer][day] = hours
        imbalance = 0.0
        for hours in per_lecturer.values():
            mean = sum(hours.values()) / len(hours)
            imbalance += sum((h - mean) ** 2 for h in hours.values()) / len(hours)

        room_changes = sum(len(r) - 1 for r in rooms_used.values())
        return {"gaps": gaps, "load": imbalance, "rooms": room_changes, "type": wrong_type, "late": late}

    def score(self, assignments) -> float:
        c = self.components(assignments)
        return -sum(self.weights[k] * c[k] for k in self.weights)


def soft_score(problem: Problem, solution: Solution) -> float:
    """Higher is better. 0 would mean no gaps, perfectly even lecturer days, one room per
    course, every class in its preferred room type and nothing in the last slot of the day.

    gaps   idle teaching slots between a group's first and last class of a day
    load   how unevenly each lecturer's hours are spread over the week (variance of daily hours)
    rooms  rooms a course uses beyond its first
    type   classes not in the course's preferred room type
    late   classes in the last teaching slot of the day

    Weights are in SoftScorer.WEIGHTS and are written up in docs/solver-design.md.
    """
    return SoftScorer(problem).score(solution.assignments)
