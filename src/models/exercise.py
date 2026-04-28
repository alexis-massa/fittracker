# src/models/exercise.py
from dataclasses import asdict, dataclass, field
from typing import Any

from src.db import db_manager
from src.utils import mongo as mongo_utils


@dataclass
class ExerciseDefinition:
    """Reusable exercise definition stored in the library."""

    name: str
    label: str = ""  # e.g. "Pushup"
    variant: str | None = None  # e.g. "1"
    variant_label: str = ""  # e.g. "Wide"
    _id: str = field(default="", repr=False)

    @property
    def display_name(self) -> str:
        """Full human-readable name: 'A — Pushup / 1 — Wide'"""
        parts = [self.name]
        if self.label:
            parts.append(f"— {self.label}")
        if self.variant:
            parts.append(f"/ {self.variant}")
            if self.variant_label:
                parts.append(f"— {self.variant_label}")
        return " ".join(parts)

    @property
    def short_name(self) -> str:
        """Compact identifier: 'A1'"""
        return f"{self.name}{self.variant}" if self.variant else self.name

    @classmethod
    def from_doc(cls, doc: dict[str, Any]) -> "ExerciseDefinition":
        return cls(
            _id=str(doc.get("_id", "")),
            name=doc.get("name", ""),
            label=doc.get("label", ""),
            variant=doc.get("variant"),
            variant_label=doc.get("variant_label", ""),
        )

    def to_doc(self) -> dict[str, Any]:
        doc = asdict(self)
        doc.pop("_id", None)
        return doc


@dataclass
class SessionExercise:
    """Exercise as performed in a session — embedded in session document."""

    name: str
    sets: int
    reps: int
    rest_seconds: int = 90
    variant: str | None = None
    label: str = ""
    variant_label: str = ""

    @property
    def display_name(self) -> str:
        parts = [self.name]
        if self.label:
            parts.append(f"— {self.label}")
        if self.variant:
            parts.append(f"/ {self.variant}")
            if self.variant_label:
                parts.append(f"— {self.variant_label}")
        return " ".join(parts)

    @property
    def short_name(self) -> str:
        return f"{self.name}{self.variant}" if self.variant else self.name

    @classmethod
    def from_doc(cls, doc: dict[str, Any]) -> "SessionExercise":
        return cls(
            name=doc.get("name", ""),
            label=doc.get("label", ""),
            variant=doc.get("variant"),
            variant_label=doc.get("variant_label", ""),
            sets=doc.get("sets", 3),
            reps=doc.get("reps", 10),
            rest_seconds=doc.get("rest_seconds", 90),
        )

    def to_doc(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_definition(cls, defn: "ExerciseDefinition") -> "SessionExercise":
        return cls(
            name=defn.name,
            label=defn.label,
            variant=defn.variant,
            variant_label=defn.variant_label,
            sets=3,
            reps=10,
            rest_seconds=90,
        )


# ---------------------------------------------------------------------------
# Library CRUD
# ---------------------------------------------------------------------------


def get_all() -> list[ExerciseDefinition]:
    return [
        ExerciseDefinition.from_doc(doc)
        for doc in mongo_utils.find_all(db_manager.exercises(), sort_field="name")
    ]


def get_by_id(exercise_id: str) -> ExerciseDefinition | None:
    doc = mongo_utils.find_one(db_manager.exercises(), exercise_id)
    return ExerciseDefinition.from_doc(doc) if doc else None


def create(defn: ExerciseDefinition) -> str:
    return mongo_utils.insert_one(db_manager.exercises(), defn.to_doc())


def update(exercise_id: str, defn: ExerciseDefinition) -> bool:
    return mongo_utils.update_one(db_manager.exercises(), exercise_id, defn.to_doc())


def delete(exercise_id: str) -> bool:
    return mongo_utils.delete_one(db_manager.exercises(), exercise_id)
