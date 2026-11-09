# src/preferences.py
from dataclasses import asdict
from dataclasses import dataclass
from typing import Any


@dataclass
class Preferences:
    dark_mode: bool = False

    @classmethod
    def from_doc(cls, doc: dict[str, Any]) -> "Preferences":
        # Keep only known fields (avoids crashes if the stored doc has extra keys)
        defaults = cls()
        return cls(**{key: doc.get(key, getattr(defaults, key)) for key in asdict(defaults)})
