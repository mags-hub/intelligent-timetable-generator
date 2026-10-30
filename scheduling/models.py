"""Plain data classes shared by every part of the scheduling engine."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Slot:
    id: int
    day: int            # 1 = Monday ... 5 = Friday
    start: str          # "08:15"
    end: str            # "09:15"


@dataclass(frozen=True)
class Room:
    id: int
    name: str
    capacity: int
    room_type: str      # "lecture" | "lab" | "auditorium"


@dataclass(frozen=True)
class Group:
    id: int
    name: str
    size: int
    parent_id: int | None = None


@dataclass(frozen=True)
class Course:
    id: int
    code: str
    lecturer_id: int
    weekly_hours: int
    block_hours: int
    group_ids: tuple[int, ...]
    preferred_room_type: str | None = None


@dataclass
class Problem:
    """Everything the solver needs. Break slots are already removed."""
    courses: list[Course]
    rooms: list[Room]
    groups: list[Group]
    slots: list[Slot]
    locked: list["Assignment"] = field(default_factory=list)   # entries that must not move


@dataclass(frozen=True)
class Assignment:
    """One course placed in one room in one one-hour slot."""
    course_id: int
    room_id: int
    slot_id: int


@dataclass
class Solution:
    assignments: list[Assignment]
    score: float = 0.0              # higher is better; set by constraints.soft_score


@dataclass
class GenerateResult:
    feasible: bool
    message: str
    timetable_id: int | None = None
    score: float | None = None
