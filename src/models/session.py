# src/models/session.py
from dataclasses import dataclass
from dataclasses import field
import enum
from typing import Any

from src.db import db_manager
from src.models.exercise import SessionExercise
from src.utils import mongo as mongo_utils
from src.utils.formatting import today_iso


class EnergyLevel(enum.IntEnum):
    LOW = 1
    MEDIUM_LOW = 2
    MEDIUM = 3
    MEDIUM_HIGH = 4
    HIGH = 5


class ProgressEnum(enum.StrEnum):
    PROGRESS = "PROGRESS"
    MAINTAIN = "MAINTAIN"
    REGRESS = "REGRESS"


@dataclass
class Session:
    date: str = field(default_factory=today_iso)
    weight: float | None = None
    notes: str | None = None
    energy_level: EnergyLevel | None = None
    progress: ProgressEnum = ProgressEnum.MAINTAIN
    warmup: list[SessionExercise] = field(default_factory=list[SessionExercise])
    workout: list[SessionExercise] = field(default_factory=list[SessionExercise])
    stretches: list[SessionExercise] = field(default_factory=list[SessionExercise])
    _id: str = field(default="", repr=False)

    @property
    def id(self) -> str:
        return self._id

    @classmethod
    def from_doc(cls, doc: dict[str, Any]) -> "Session":
        def build(items: list[Any]) -> list[SessionExercise]:
            return [SessionExercise.from_doc(i) if isinstance(i, dict) else i for i in items]

        return cls(
            _id=str(doc.get("_id", "")),
            date=doc.get("date", today_iso()),
            weight=doc.get("weight"),
            notes=doc.get("notes"),
            energy_level=EnergyLevel(doc["energy_level"]) if doc.get("energy_level") else None,
            progress=ProgressEnum(doc.get("progress", ProgressEnum.MAINTAIN)),
            warmup=build(doc.get("warmup", [])),
            workout=build(doc.get("workout", [])),
            stretches=build(doc.get("stretches", [])),
        )

    def to_doc(self) -> dict[str, Any]:
        return {
            "date": self.date,
            "weight": self.weight,
            "notes": self.notes,
            "energy_level": self.energy_level.value if self.energy_level else None,
            "progress": self.progress.value,
            "warmup": [e.to_doc() for e in self.warmup],
            "workout": [e.to_doc() for e in self.workout],
            "stretches": [e.to_doc() for e in self.stretches],
        }


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


def get_all() -> list[Session]:
    return [
        Session.from_doc(doc)
        for doc in mongo_utils.find_all(db_manager.sessions(), sort_field="date", ascending=False)
    ]


def get_by_id(session_id: str) -> Session | None:
    doc = mongo_utils.find_one(db_manager.sessions(), session_id)
    return Session.from_doc(doc) if doc else None


def create(session: Session) -> str:
    return mongo_utils.insert_one(db_manager.sessions(), session.to_doc())


def update(session_id: str, session: Session) -> bool:
    return mongo_utils.update_one(db_manager.sessions(), session_id, session.to_doc())


def delete(session_id: str) -> bool:
    return mongo_utils.delete_one(db_manager.sessions(), session_id)
