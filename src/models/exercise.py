# src/models/exercise.py
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from src.db import db_manager
from src.utils import mongo as mongo_utils


@dataclass
class Exercise:
    name: str
    sets: int
    reps: int
    variant: str | None
    rest_seconds: int = 90
    _id: str = field(default="", repr=False)

    @property
    def id(self) -> str:
        return self._id

    @property
    def display_name(self) -> str:
        return f"{self.name} [{self.variant}]" if self.variant else self.name

    @classmethod
    def from_doc(cls, doc: dict[str, Any]) -> "Exercise":
        return cls(
            _id=str(doc.get("_id", "")),
            name=doc.get("name", ""),
            sets=doc.get("sets", 0),
            reps=doc.get("reps", 0),
            variant=doc.get("variant"),
            rest_seconds=doc.get("rest_seconds", 0),
        )

    def to_doc(self) -> dict[str, Any]:
        doc = asdict(self)
        doc.pop("_id", None)
        return doc


def get_all() -> list[Exercise]:
    return [
        Exercise.from_doc(doc)
        for doc in mongo_utils.find_all(db_manager.exercises(), sort_field="name")
    ]


def get_by_id(exercise_id: str) -> Exercise | None:
    doc = mongo_utils.find_one(db_manager.exercises(), exercise_id)
    return Exercise.from_doc(doc) if doc else None


def create(exercise: Exercise) -> str:
    return mongo_utils.insert_one(db_manager.exercises(), exercise.to_doc())


def update(exercise_id: str, exercise: Exercise) -> bool:
    return mongo_utils.update_one(db_manager.exercises(), exercise_id, exercise.to_doc())


def delete(exercise_id: str) -> bool:
    return mongo_utils.delete_one(db_manager.exercises(), exercise_id)
