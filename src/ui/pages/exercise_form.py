# src/ui/pages/exercise_form.py
from collections.abc import Callable

from nicegui import ui

from src.models import exercise as exercise_model
from src.models.exercise import ExerciseDefinition
from src.models.exercise import ExerciseVariant
from src.ui.components import action_row
from src.ui.components import btn_ghost
from src.ui.components import btn_primary
from src.ui.components import form_card
from src.ui.components import input_field
from src.ui.components import page_title
from src.ui.components import section_title
from src.ui.pages.exercise_create_form import exercise_create_form


def render(exercise_id: str | None, navigate: Callable[..., None]) -> None:
    existing = exercise_model.get_by_id(exercise_id) if exercise_id else None

    if not existing:
        # New exercise — use the shared creation form directly
        with ui.column().classes("page-content"):
            page_title("New Exercise")

            slot = ui.column().classes("w-full")

            def on_done(defn: ExerciseDefinition) -> None:
                navigate("exercises")

            def on_cancel() -> None:
                navigate("exercises")

            exercise_create_form(slot, on_done=on_done, on_cancel=on_cancel)
        return

    # Edit existing — show same fields pre-filled, with mutable variant list
    variants: list[ExerciseVariant] = list(existing.variants)

    with ui.column().classes("page-content"):
        page_title("Edit Exercise")
        section_title("Exercise details")

        with form_card(), ui.row().classes("w-full items-center gap-4 flex-wrap"):
            name_in = input_field("Name (e.g. A)", value=existing.name).classes("flex-1")
            label_in = input_field("Label (e.g. Pushup)", value=existing.label).classes("flex-1")

        ui.element("div").classes("q-mb-md")
        section_title("Variants")

        variants_container = ui.column().classes("w-full")

        def refresh_variants() -> None:
            variants_container.clear()
            with variants_container:
                for i, v in enumerate(variants):
                    with ui.row().classes("w-full items-center gap-2 flex-wrap"):
                        vn = input_field("Name (e.g. 1)", value=v.name).classes("flex-1")
                        vl = input_field("Label (e.g. Wide)", value=v.label).classes("flex-1")

                        def update_name(idx: int, field: ui.input) -> None:
                            variants[idx].name = field.value.strip()

                        def update_label(idx: int, field: ui.input) -> None:
                            variants[idx].label = field.value.strip()

                        vn.on("blur", lambda _, idx=i, field=vn: update_name(idx, field))
                        vl.on("blur", lambda _, idx=i, field=vl: update_label(idx, field))

                        def remove(idx: int = i) -> None:
                            variants.pop(idx)
                            refresh_variants()

                        btn_ghost("×", on_click=remove)

                def add_variant() -> None:
                    variants.append(ExerciseVariant(name="", label=""))
                    refresh_variants()

                btn_ghost("+ Add variant", on_click=add_variant)

        refresh_variants()

        ui.element("div").classes("q-mb-md")
        with action_row():
            btn_primary(
                "Save", on_click=lambda: _save(exercise_id, name_in, label_in, variants, navigate)
            )
            btn_ghost("Cancel", on_click=lambda: navigate("exercises"))


def _save(
    exercise_id: str | None,
    name_in: ui.input,
    label_in: ui.input,
    variants: list[ExerciseVariant],
    navigate: Callable[..., None],
) -> None:
    if not name_in.value.strip():
        ui.notify("Name is required", color="negative")
        return

    defn = ExerciseDefinition(
        name=name_in.value.strip(),
        label=label_in.value.strip(),
        variants=[v for v in variants if v.name.strip()],
    )

    if exercise_id:
        exercise_model.update(exercise_id, defn)
        ui.notify("Exercise updated", color="positive")

    navigate("exercises")
