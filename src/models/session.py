# src/models/session.py
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
import enum
import typing

from src.db import db_manager
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
    weight: float | None = None
    notes: str | None = None
    energy_level: EnergyLevel | None = None
    date: str = field(default_factory=today_iso)
    warmup: list[str] = field(default_factory=list)
    workout: list[str] = field(default_factory=list)
    stretches: list[str] = field(default_factory=list)
    progress: ProgressEnum = ProgressEnum.MAINTAIN
    _id: str = field(default="", repr=False)

    @property
    def id(self) -> str:
        return self._id

    @classmethod
    def from_doc(cls, doc: dict[str, typing.Any]) -> "Session":
        return cls(
            _id=str(doc.get("_id", "")),
            date=doc.get("date", today_iso()),
            weight=doc.get("weight"),
            notes=doc.get("notes"),
            energy_level=EnergyLevel(doc["energy_level"]) if doc.get("energy_level") else None,
            progress=ProgressEnum(doc.get("progress", ProgressEnum.MAINTAIN)),
            warmup=doc.get("warmup", []),
            workout=doc.get("exercises", []),
            stretches=doc.get("stretches", []),
        )

    def to_doc(self) -> dict[str, typing.Any]:
        doc = asdict(self)
        doc.pop("_id", None)
        return doc


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
