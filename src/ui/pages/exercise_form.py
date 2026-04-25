# src/ui/pages/exercise_form.py
"""
Exercise create / edit form.
"""

from collections.abc import Callable

from nicegui import ui

from src.models import exercise as exercise_model
from src.models.exercise import Exercise
from src.ui.components import action_row
from src.ui.components import btn_ghost
from src.ui.components import btn_primary
from src.ui.components import form_card
from src.ui.components import input_field
from src.ui.components import number_field
from src.ui.components import page_title
from src.ui.components import section_title


def render(exercise_id: str | None, navigate: Callable[[str], None]) -> None:
    existing = exercise_model.get_by_id(exercise_id) if exercise_id else None

    with ui.column().classes("page-content"):
        page_title("Edit Exercise" if existing else "New Exercise")
        section_title("Exercise details")

        with form_card():
            name_in = input_field("Name", value=existing.name if existing else "")
            ui.element("div").style("height:0.5rem")
            variant_in = input_field(
                "Variant",
                value=existing.variant if existing and existing.variant else "",
            )
            ui.element("div").style("height:0.5rem")
            sets_in = number_field("Sets", value=existing.sets if existing else 3, min=1, max=20)
            ui.element("div").style("height:0.5rem")
            reps_in = number_field("Reps", value=existing.reps if existing else 10, min=1, max=200)
            ui.element("div").style("height:0.5rem")
            rest_in = number_field(
                "Rest (s)", value=existing.rest_seconds if existing else 90, min=0, max=600
            )

        with action_row():
            btn_primary(
                "Save",
                on_click=lambda: _save(
                    exercise_id, name_in, variant_in, sets_in, reps_in, rest_in, navigate
                ),
            )
            btn_ghost("Cancel", on_click=lambda: navigate("exercises"))


def _save(
    exercise_id: str | None,
    name_in: ui.input,
    variant_in: ui.input,
    sets_in: ui.number,
    reps_in: ui.number,
    rest_in: ui.number,
    navigate: Callable[[str], None],
) -> None:
    if not name_in.value.strip():
        ui.notify("Name is required", color="negative")
        return

    ex = Exercise(
        name=name_in.value.strip(),
        variant=variant_in.value.strip(),
        sets=int(sets_in.value or 3),
        reps=int(reps_in.value or 10),
        rest_seconds=int(rest_in.value or 90),
    )

    if exercise_id:
        exercise_model.update(exercise_id, ex)
        ui.notify("Exercise updated", color="positive")
    else:
        exercise_model.create(ex)
        ui.notify("Exercise saved", color="positive")

    navigate("exercises")
