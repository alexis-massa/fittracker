#!/usr/bin/env python3
"""One-shot loader: insert data/lafay_exercises.json into the exercise library.

Usage: uv run python scripts/seed_exercises.py
Skips any exercise whose name already exists in the library.
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import db_manager
from src.models import exercise as exercise_model
from src.models.exercise import ExerciseDefinition

DATA_FILE = Path(__file__).parent.parent / "data" / "lafay_exercises.json"


def main() -> None:
    db_manager.connect()
    try:
        existing_names = {defn.name for defn in exercise_model.get_all()}
        entries = json.loads(DATA_FILE.read_text())

        created, skipped = 0, 0
        for entry in entries:
            if entry["name"] in existing_names:
                skipped += 1
                continue
            exercise_model.create(ExerciseDefinition.from_doc(entry))
            created += 1

        print(f"Created {created}, skipped {skipped} (already present)")
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    main()
