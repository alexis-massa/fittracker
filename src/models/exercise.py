# src/models/exercise.py
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from src.db import db_manager
from src.utils import mongo as mongo_utils

# ---------------------------------------------------------------------------
# Variant — embedded in ExerciseDefinition, never stored separately
# ---------------------------------------------------------------------------


@dataclass
class ExerciseVariant:
    name: str  # e.g. "1"
    label: str = ""  # e.g. "Wide"

    @property
    def display_name(self) -> str:
        return f"{self.name} — {self.label}" if self.label else self.name

    @classmethod
    def from_doc(cls, doc: dict[str, Any]) -> "ExerciseVariant":
        return cls(
            name=doc.get("name", ""),
            label=doc.get("label", ""),
        )

    def to_doc(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# ExerciseDefinition — stored in exercises collection
# ---------------------------------------------------------------------------


@dataclass
class ExerciseDefinition:
    name: str  # e.g. "A"
    label: str = ""
    variants: list[ExerciseVariant] = field(default_factory=list[ExerciseVariant])
    _id: str = field(default="", repr=False)

    @property
    def id(self) -> str:
        return self._id

    @property
    def display_name(self) -> str:
        return f"{self.name} — {self.label}" if self.label else self.name

    def get_variant(self, name: str) -> ExerciseVariant | None:
        return next((v for v in self.variants if v.name == name), None)

    @classmethod
    def from_doc(cls, doc: dict[str, Any]) -> "ExerciseDefinition":
        return cls(
            _id=str(doc.get("_id", "")),
            name=doc.get("name", ""),
            label=doc.get("label", ""),
            variants=[ExerciseVariant.from_doc(v) for v in doc.get("variants", [])],
        )

    def to_doc(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "label": self.label,
            "variants": [v.to_doc() for v in self.variants],
        }


# ---------------------------------------------------------------------------
# SessionExercise — embedded in Session, never stored separately
# ---------------------------------------------------------------------------


@dataclass
class SessionExercise:
    name: str  # e.g. "A"
    label: str = ""  # e.g. "Pushup"
    variant_name: str = ""  # e.g. "1"
    variant_label: str = ""  # e.g. "Wide"
    sets: int = 3
    reps: int = 10
    duration: int = 0  # seconds — alternative to reps
    rest_before: int = 0  # seconds before this exercise
    rest_seconds: int = 90  # seconds between sets

    @property
    def short_name(self) -> str:
        return f"{self.name}{self.variant_name}" if self.variant_name else self.name

    @property
    def display_name(self) -> str:
        parts = [self.name]
        if self.label:
            parts.append(f"— {self.label}")
        if self.variant_name:
            parts.append(f"/ {self.variant_name}")
            if self.variant_label:
                parts.append(f"— {self.variant_label}")
        return " ".join(parts)

    @classmethod
    def from_doc(cls, doc: dict[str, Any]) -> "SessionExercise":
        return cls(
            name=doc.get("name", ""),
            label=doc.get("label", ""),
            variant_name=doc.get("variant_name", ""),
            variant_label=doc.get("variant_label", ""),
            sets=doc.get("sets", 3),
            reps=doc.get("reps", 10),
            duration=doc.get("duration", 0),
            rest_before=doc.get("rest_before", 0),
            rest_seconds=doc.get("rest_seconds", 90),
        )

    def to_doc(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_definition(
        cls,
        defn: ExerciseDefinition,
        variant: ExerciseVariant | None = None,
    ) -> "SessionExercise":
        return cls(
            name=defn.name,
            label=defn.label,
            variant_name=variant.name if variant else "",
            variant_label=variant.label if variant else "",
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
