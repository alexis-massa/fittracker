#!/usr/bin/env python3
"""Load data/lafay_exercises.json into one user's exercise library.

Usage: uv run python scripts/seed_exercises.py USERNAME
Skips any exercise whose name already exists in that user's library.
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import db_manager
from src.models import exercise as exercise_model
from src.models import user as user_model
from src.models.exercise import ExerciseDefinition

DATA_FILE = Path(__file__).parent.parent / "data" / "lafay_exercises.json"


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)

    db_manager.connect()
    try:
        user = user_model.get_by_username(sys.argv[1])
        if user is None:
            sys.exit(f"No such user: {sys.argv[1]}")

        existing_names = {defn.name for defn in exercise_model.get_all(user.id)}
        entries = json.loads(DATA_FILE.read_text())

        created, skipped = 0, 0
        for entry in entries:
            if entry["name"] in existing_names:
                skipped += 1
                continue
            exercise_model.create(user.id, ExerciseDefinition.from_doc(entry))
            created += 1

        print(f"{user.username}: created {created}, skipped {skipped} (already present)")
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    main()
