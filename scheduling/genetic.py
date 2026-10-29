"""Genetic algorithm optimiser (Ticket 10).

Starts from a valid timetable (the solver's answer) and improves it against the soft goals in
constraints.SoftScorer. Every change is checked for clashes as it is made, so every timetable in
the population is always valid and a hard rule can never be broken.

Individual = a list with one (window of slots, room) per block of classes.
"""
import random
import time
from collections import defaultdict
from dataclasses import dataclass

from .constraints import SoftScorer, _group_chain, hard_violations
from .models import Assignment, Problem, Solution


@dataclass
class GAParams:
    population_size: int = 50
    generations: int = 200
    mutation_rate: float = 0.05   # chance that each movable block of a child is changed
    crossover_rate: float = 0.8
    elite_size: int = 2
    seed: int | None = 42         # fixed seed = repeatable results for tests and the report
    time_limit_s: float = 20.0    # safety stop so a request can never run for long


class _Block:
    """A run of back-to-back hours of one course. A frozen block is never moved."""
    __slots__ = ("course", "length", "frozen")

    def __init__(self, course, length, frozen):
        self.course, self.length, self.frozen = course, length, frozen


class _Context:
    """Everything about the Problem that does not change while the algorithm runs."""

    def __init__(self, problem: Problem, start: Solution):
        self.problem = problem
        self.courses = {c.id: c for c in problem.courses}
        self.slots = {s.id: s for s in problem.slots}
        self.order = {s.id: i for i, s in enumerate(problem.slots)}
        groups = {g.id: g for g in problem.groups}
        self.scorer = SoftScorer(problem)

        self.conflicts = {g: set(_group_chain(g, groups)) for g in groups}
        for g in groups:
            for ancestor in _group_chain(g, groups):
                self.conflicts[ancestor].add(g)

        students = {c.id: sum(groups[g].size for g in c.group_ids if g in groups) for c in problem.courses}
        self.rooms_for = {c.id: [r.id for r in problem.rooms if r.capacity >= students[c.id]] for c in problem.courses}
        self.room_ids_for = {cid: set(ids) for cid, ids in self.rooms_for.items()}

        by_day = defaultdict(list)
        for s in problem.slots:
            by_day[s.day].append(s)
        for day_slots in by_day.values():
            day_slots.sort(key=lambda s: s.start)
        self._by_day = by_day
        self._windows = {}

        self.blocks, self.start_placements = self._recover_blocks(start)
        self.course_blocks = defaultdict(list)
        self.movable_by_length = defaultdict(list)
        for i, b in enumerate(self.blocks):
            self.course_blocks[b.course.id].append(i)
            if not b.frozen:
                self.movable_by_length[b.length].append(i)

    def windows(self, length):
        """Every run of `length` back-to-back slots on one day."""
        if length not in self._windows:
            found = []
            for day_slots in self._by_day.values():
                for i in range(len(day_slots) - length + 1):
                    run = day_slots[i:i + length]
                    if all(a.end == b.start for a, b in zip(run, run[1:])):
                        found.append(tuple(s.id for s in run))
            found.sort(key=lambda w: self.order[w[0]])
            self._windows[length] = found
        return self._windows[length]

    def _recover_blocks(self, start: Solution):
        """Turn the solution's one-hour assignments back into blocks. Anything that does not
        form a clean block (and every locked entry) becomes frozen one-hour blocks."""
        locked = set(self.problem.locked)
        by_course = defaultdict(list)
        for a in start.assignments:
            if a.course_id in self.courses and a.slot_id in self.slots:
                by_course[a.course_id].append(a)
        blocks, placements = [], []
        for cid in sorted(by_course):
            course = self.courses[cid]
            size = max(course.block_hours, 1)
            by_day = defaultdict(list)
            for a in by_course[cid]:
                by_day[self.slots[a.slot_id].day].append(a)
            for day in sorted(by_day):
                day_as = sorted(by_day[day], key=lambda a: self.order[a.slot_id])
                runs, run = [], [day_as[0]]
                for prev, nxt in zip(day_as, day_as[1:]):
                    if self.slots[prev.slot_id].end == self.slots[nxt.slot_id].start:
                        run.append(nxt)
                    else:
                        runs.append(run)
                        run = [nxt]
                runs.append(run)
                for run in runs:
                    chunks = [run[i:i + size] for i in range(0, len(run), size)] if len(run) % size == 0 else None
                    clean = (chunks is not None and not any(a in locked for a in run)
                             and all(len({a.room_id for a in ch}) == 1 for ch in chunks))
                    if clean:
                        for ch in chunks:
                            blocks.append(_Block(course, size, False))
                            placements.append((tuple(a.slot_id for a in ch), ch[0].room_id))
                    else:
                        for a in run:
                            blocks.append(_Block(course, 1, True))
                            placements.append(((a.slot_id,), a.room_id))
        return blocks, placements

    def assignments(self, placements):
        out = []
        for block, (window, room) in zip(self.blocks, placements):
            for s in window:
                out.append(Assignment(block.course.id, room, s))
        out.sort(key=lambda a: (a.course_id, self.order[a.slot_id]))
        return out

    def score(self, placements):
        return self.scorer.score(self.assignments(placements))


class _State:
    """Who is busy when, for one timetable. Lets us test a move without checking everything."""

    def __init__(self, ctx: _Context, placements):
        self.ctx = ctx
        self.lecturer, self.room, self.group = set(), set(), defaultdict(set)
        for block, (window, room) in zip(ctx.blocks, placements):
            self.add(block.course, window, room)

    def add(self, course, window, room):
        for s in window:
            self.lecturer.add((course.lecturer_id, s))
            self.room.add((room, s))
            self.group[s].update(course.group_ids)

    def remove(self, course, window, room):
        for s in window:
            self.lecturer.discard((course.lecturer_id, s))
            self.room.discard((room, s))
            self.group[s].difference_update(course.group_ids)

    def is_free(self, course, window, room):
        conflicts = self.ctx.conflicts
        for s in window:
            if (course.lecturer_id, s) in self.lecturer or (room, s) in self.room:
                return False
            busy = self.group[s]
            if busy and any(conflicts.get(g, ()) & busy for g in course.group_ids):
                return False
        return True


def _move_block(ctx, rng, state, placements, i):
    """Move one block to another window and/or room. Returns True if it moved."""
    block = ctx.blocks[i]
    old = placements[i]
    rooms = ctx.rooms_for[block.course.id]
    windows = ctx.windows(block.length)
    state.remove(block.course, *old)
    for _ in range(8):
        if rng.random() < 0.3:
            new = (old[0], rng.choice(rooms))                      # same time, another room
        else:
            window = rng.choice(windows)
            room = old[1] if (old[1] in ctx.room_ids_for[block.course.id] and rng.random() < 0.5) else rng.choice(rooms)
            new = (window, room)
        if new != old and state.is_free(block.course, *new):
            placements[i] = new
            state.add(block.course, *new)
            return True
    state.add(block.course, *old)
    return False


def _swap_blocks(ctx, rng, state, placements, i):
    """Swap the times of two blocks of the same length, each keeping its own room."""
    block = ctx.blocks[i]
    others = [j for j in ctx.movable_by_length[block.length] if j != i]
    if not others:
        return False
    j = rng.choice(others)
    bi, bj = block, ctx.blocks[j]
    (wi, ri), (wj, rj) = placements[i], placements[j]
    if wi == wj or ri not in ctx.room_ids_for[bi.course.id] or rj not in ctx.room_ids_for[bj.course.id]:
        return False
    state.remove(bi.course, wi, ri)
    state.remove(bj.course, wj, rj)
    if state.is_free(bi.course, wj, ri):
        state.add(bi.course, wj, ri)
        if state.is_free(bj.course, wi, rj):
            state.add(bj.course, wi, rj)
            placements[i], placements[j] = (wj, ri), (wi, rj)
            return True
        state.remove(bi.course, wj, ri)
    state.add(bi.course, wi, ri)
    state.add(bj.course, wj, rj)
    return False


def _mutate(ctx, rng, state, placements, rate):
    for i, block in enumerate(ctx.blocks):
        if block.frozen or rng.random() >= rate:
            continue
        if rng.random() < 0.5:
            _move_block(ctx, rng, state, placements, i)
        else:
            _swap_blocks(ctx, rng, state, placements, i)


def _crossover(ctx, rng, state, child, other):
    """Take some courses' placements from `other`, keeping a change only if it causes no clash."""
    courses = list(ctx.course_blocks)
    rng.shuffle(courses)
    for cid in courses:
        if rng.random() < 0.5:
            continue
        idx = [i for i in ctx.course_blocks[cid] if not ctx.blocks[i].frozen and child[i] != other[i]]
        if not idx:
            continue
        course = ctx.courses[cid]
        for i in idx:
            state.remove(course, *child[i])
        done = []
        for i in idx:
            if state.is_free(course, *other[i]):
                state.add(course, *other[i])
                done.append(i)
            else:
                break
        if len(done) == len(idx):
            for i in idx:
                child[i] = other[i]
        else:
            for i in done:
                state.remove(course, *other[i])
            for i in idx:
                state.add(course, *child[i])


def optimise(problem: Problem, start: Solution, params: GAParams | None = None) -> Solution:
    """Improve `start` without ever breaking a hard rule. Never returns a worse timetable."""
    params = params or GAParams()
    ctx = _Context(problem, start)
    start_score = ctx.score(ctx.start_placements)
    unchanged = Solution(list(start.assignments), start_score)
    if not any(not b.frozen for b in ctx.blocks) or params.population_size < 2:
        return unchanged

    rng = random.Random(params.seed)
    deadline = time.monotonic() + params.time_limit_s
    first = ctx.start_placements

    population = [list(first)]
    for _ in range(params.population_size - 1):
        child = list(first)
        _mutate(ctx, rng, _State(ctx, child), child, max(params.mutation_rate * 3, 0.1))
        population.append(child)
    scores = [ctx.score(p) for p in population]
    best, best_score = list(first), start_score

    def pick():
        contenders = [rng.randrange(len(population)) for _ in range(3)]
        return population[max(contenders, key=lambda k: scores[k])]

    for _ in range(params.generations):
        if time.monotonic() > deadline:
            break
        ranked = sorted(range(len(population)), key=lambda k: -scores[k])
        new_population = [population[k] for k in ranked[:params.elite_size]]
        new_scores = [scores[k] for k in ranked[:params.elite_size]]
        while len(new_population) < params.population_size:
            child = list(pick())
            state = _State(ctx, child)
            if rng.random() < params.crossover_rate:
                _crossover(ctx, rng, state, child, pick())
            _mutate(ctx, rng, state, child, params.mutation_rate)
            new_population.append(child)
            new_scores.append(ctx.score(child))
        population, scores = new_population, new_scores
        top = max(range(len(population)), key=lambda k: scores[k])
        if scores[top] > best_score:
            best, best_score = list(population[top]), scores[top]

    if best_score <= start_score:
        return unchanged
    result = Solution(ctx.assignments(best), best_score)
    if hard_violations(problem, result):          # safety net: should never happen
        return unchanged
    return result
