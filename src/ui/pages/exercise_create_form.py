# src/ui/pages/exercise_create_form.py
"""
Canonical exercise creation form.
Renders inline into `parent`, calls `on_done(new_defn)` on success.
Imported by both session_form and exercise_form.
"""

from collections.abc import Callable

from nicegui import ui

from src.models.exercise import ExerciseDefinition
from src.models.exercise import ExerciseVariant
from src.models.exercise import create as create_definition
from src.ui.components import btn_ghost
from src.ui.components import btn_primary
from src.ui.components import form_card
from src.ui.components import input_field
from src.ui.components import section_title


def exercise_create_form(
    parent: ui.element,
    on_done: Callable[[ExerciseDefinition], None],
    on_cancel: Callable[[], None] | None = None,
) -> None:
    """
    Render an inline exercise creation form into `parent`.

    Args:
        parent:    The NiceGUI element to render into.
        on_done:   Called with the new ExerciseDefinition after successful creation.
        on_cancel: Optional callback when the user cancels. Defaults to deleting the card.
    """
    with parent, form_card() as create_card:
        ui.label("New Exercise").classes("inline-form-title")

        with ui.row().classes("w-full items-center gap-2 flex-wrap"):
            dn_in = input_field("Name (e.g. A)").classes("flex-1")
            dl_in = input_field("Label (e.g. Pushup)").classes("flex-1")

        ui.element("div").classes("spacer-sm")
        section_title("Variants")

        new_variants: list[ExerciseVariant] = []
        variants_container = ui.column().classes("w-full")

        def refresh_variants() -> None:
            variants_container.clear()
            with variants_container:
                for i, v in enumerate(new_variants):
                    with ui.row().classes("w-full items-center gap-2"):
                        vn = input_field("Name (e.g. 1)", value=v.name).classes("flex-1")
                        vl = input_field("Label (e.g. Wide)", value=v.label).classes("flex-1")

                        def update_name(idx: int, field: ui.input) -> None:
                            new_variants[idx].name = field.value.strip()

                        def update_label(idx: int, field: ui.input) -> None:
                            new_variants[idx].label = field.value.strip()

                        vn.on("blur", lambda _, idx=i, field=vn: update_name(idx, field))
                        vl.on("blur", lambda _, idx=i, field=vl: update_label(idx, field))

                        def remove(idx: int = i) -> None:
                            new_variants.pop(idx)
                            refresh_variants()

                        btn_ghost("×", on_click=remove)

        refresh_variants()

        def add_variant() -> None:
            new_variants.append(ExerciseVariant(name="", label=""))
            refresh_variants()

        btn_ghost("+ Add variant", on_click=add_variant)

        ui.element("div").classes("spacer-sm")

        def create() -> None:
            name = dn_in.value.strip()
            if not name:
                ui.notify("Name is required", color="negative")
                return
            new_defn = ExerciseDefinition(
                name=name,
                label=dl_in.value.strip(),
                variants=[v for v in new_variants if v.name.strip()],
            )
            create_definition(new_defn)
            ui.notify(f"'{new_defn.display_name}' added to library", color="positive")
            create_card.delete()
            on_done(new_defn)

        def cancel() -> None:
            if on_cancel:
                on_cancel()
            else:
                create_card.delete()

        with ui.row().classes("items-center gap-2"):
            btn_primary("Create", on_click=create)
            btn_ghost("Cancel", on_click=cancel)
