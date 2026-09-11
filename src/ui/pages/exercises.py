# src/ui/pages/exercises.py
from nicegui import ui

from src.models import exercise as exercise_model
from src.models.exercise import ExerciseDefinition
from src.ui.components import btn_danger
from src.ui.components import btn_ghost
from src.ui.components import btn_primary
from src.ui.components import card_row
from src.ui.components import confirm_dialog
from src.ui.components import exercise_pictogram
from src.ui.components import page_header_row
from src.ui.components import page_title
from src.ui.components import section_title
from src.ui.pages.exercise_create_form import exercise_create_form
from src.utils.formatting import pluralize


def render() -> None:
    with ui.column().classes("page-content"):
        # ── Header + toggleable create form ───────────────────────────────
        create_slot = ui.column().classes("w-full")
        create_visible = {"value": False}

        def toggle_create() -> None:
            if create_visible["value"]:
                create_slot.clear()
                create_visible["value"] = False
            else:
                create_visible["value"] = True

                def on_done(defn: ExerciseDefinition) -> None:
                    create_visible["value"] = False
                    ui.navigate.to("/exercises")

                def on_cancel() -> None:
                    create_slot.clear()
                    create_visible["value"] = False

                exercise_create_form(create_slot, on_done=on_done, on_cancel=on_cancel)

        with page_header_row():
            page_title("Exercise Library")
            btn_primary("+ New Exercise", on_click=toggle_create)

        # Form expands here, above the list
        # (create_slot is already in the column, declared before page_header_row)

        # ── Exercise list ─────────────────────────────────────────────────
        exercises = exercise_model.get_all()

        if not exercises:
            ui.label("No exercises yet. Add your first one.").classes("text-caption opacity-70")
            return

        section_title(pluralize(len(exercises), "exercise"))

        for ex in exercises:
            with card_row(), ui.row().classes("w-full items-center justify-between"):
                with ui.row().classes("items-center gap-3"):
                    exercise_pictogram(ex.name)
                    with ui.column().style("gap:2px"):
                        ui.label(ex.display_name).classes("text-subtitle1 text-weight-bold")
                        if ex.variants:
                            with ui.column().style("gap:0px"):
                                for v in ex.variants:
                                    ui.label(v.display_name).classes("text-caption opacity-70")
                with ui.row().classes("items-center gap-2"):
                    btn_ghost(
                        "Edit",
                        on_click=lambda eid_=ex.id: ui.navigate.to(f"/exercises/{eid_}/edit"),
                    )
                    btn_danger(
                        "Delete",
                        on_click=lambda eid_=ex.id, name_=ex.display_name: _delete(eid_, name_),
                    )


def _delete(exercise_id: str, name: str) -> None:
    def do_delete() -> None:
        exercise_model.delete(exercise_id)
        ui.notify("Exercise deleted")
        ui.navigate.to("/exercises")

    confirm_dialog(f"Delete '{name}' from the library? This cannot be undone.", do_delete)
