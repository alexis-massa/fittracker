# src/models/user_preferences.py
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from src.db import db_manager

_COL = db_manager.get_collection  # called lazily
_COLLECTION_NAME = "user_preferences"
_DEFAULT_USER_ID = "default"


@dataclass
class UserPreferences:
    dark_mode: bool = True
    _id: str = field(default=_DEFAULT_USER_ID, repr=False)

    @classmethod
    def from_doc(cls, doc: dict[str, Any]) -> "UserPreferences":
        return cls(
            _id=str(doc.get("_id", _DEFAULT_USER_ID)),
            dark_mode=doc.get("dark_mode", True),
        )

    def to_doc(self) -> dict[str, Any]:
        doc = asdict(self)
        doc.pop("_id", None)
        return doc


def load() -> UserPreferences:
    """Load the single user preferences document, creating it if absent."""
    col = db_manager.get_collection(_COLLECTION_NAME)
    doc = col.find_one({"_id": _DEFAULT_USER_ID})
    if doc:
        return UserPreferences.from_doc(doc)
    prefs = UserPreferences()
    col.insert_one({"_id": _DEFAULT_USER_ID, **prefs.to_doc()})
    return prefs


def save(prefs: UserPreferences) -> None:
    col = db_manager.get_collection(_COLLECTION_NAME)
    col.update_one(
        {"_id": _DEFAULT_USER_ID},
        {"$set": prefs.to_doc()},
        upsert=True,
    )
