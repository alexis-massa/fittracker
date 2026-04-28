# src/ui/pages/exercise_form.py
from collections.abc import Callable

from nicegui import ui

from src.models import exercise as exercise_model
from src.models.exercise import ExerciseDefinition
from src.ui.components import action_row
from src.ui.components import btn_ghost
from src.ui.components import btn_primary
from src.ui.components import form_card
from src.ui.components import input_field
from src.ui.components import page_title
from src.ui.components import section_title


def render(exercise_id: str | None, navigate: Callable[..., None]) -> None:
    existing = exercise_model.get_by_id(exercise_id) if exercise_id else None

    with ui.column().classes("page-content"):
        page_title("Edit Exercise" if existing else "New Exercise")
        section_title("Exercise details")

        with form_card():
            with ui.row().classes("w-full items-center gap-4 flex-wrap"):
                name_in = input_field(
                    "Name (e.g. A)", value=existing.name if existing else ""
                ).classes("flex-1")
                label_in = input_field(
                    "Label (e.g. Pushup)", value=existing.label if existing else ""
                ).classes("flex-1")
            ui.element("div").classes("spacer-sm")
            with ui.row().classes("w-full items-center gap-4 flex-wrap"):
                variant_in = input_field(
                    "Variant (e.g. 1)", value=existing.variant or "" if existing else ""
                ).classes("flex-1")
                variant_label_in = input_field(
                    "Variant label (e.g. Wide)", value=existing.variant_label if existing else ""
                ).classes("flex-1")

        with action_row():
            btn_primary(
                "Save",
                on_click=lambda: _save(
                    exercise_id, name_in, label_in, variant_in, variant_label_in, navigate
                ),
            )
            btn_ghost("Cancel", on_click=lambda: navigate("exercises"))


def _save(
    exercise_id: str | None,
    name_in: ui.input,
    label_in: ui.input,
    variant_in: ui.input,
    variant_label_in: ui.input,
    navigate: Callable[..., None],
) -> None:
    if not name_in.value.strip():
        ui.notify("Name is required", color="negative")
        return

    defn = ExerciseDefinition(
        name=name_in.value.strip(),
        label=label_in.value.strip(),
        variant=variant_in.value.strip() or None,
        variant_label=variant_label_in.value.strip(),
    )

    if exercise_id:
        exercise_model.update(exercise_id, defn)
        ui.notify("Exercise updated", color="positive")
    else:
        exercise_model.create(defn)
        ui.notify("Exercise saved", color="positive")

    navigate("exercises")
