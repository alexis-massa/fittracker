# src/preferences.py
from dataclasses import asdict
from dataclasses import dataclass
import json
from pathlib import Path
import typing

PREFERENCES_FILE = Path("preferences.json")


@dataclass
class Preferences:
    dark_mode: bool = True
    # future: language, units, default_weight, etc.


def load() -> Preferences:
    if not PREFERENCES_FILE.exists():
        return Preferences()

    try:
        data = json.loads(PREFERENCES_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return Preferences()

    # Keep only known fields (avoids crashes if file has extra keys)
    defaults = Preferences()
    filtered = {key: data.get(key, getattr(defaults, key)) for key in asdict(defaults)}

    return Preferences(**filtered)


def save(prefs: Preferences) -> None:
    try:
        PREFERENCES_FILE.write_text(json.dumps(asdict(prefs), indent=2))
    except OSError:
        # optional: log instead of silently ignoring
        print("Error saving preferences.")


def update(changes: dict[str, typing.Any]) -> Preferences:
    """Apply a partial update to persisted preferences, like $set."""
    current = asdict(load())
    current.update(changes)
    updated = Preferences(**current)
    save(updated)
    return updated


current = load()
