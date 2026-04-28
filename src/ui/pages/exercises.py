# src/ui/pages/exercises.py
from collections.abc import Callable

from nicegui import ui

from src.models import exercise as exercise_model
from src.ui.components import btn_danger
from src.ui.components import btn_ghost
from src.ui.components import btn_primary
from src.ui.components import page_header_row
from src.ui.components import page_title
from src.ui.components import section_title
from src.utils.formatting import pluralize


def render(navigate: Callable[..., None]) -> None:
    exercises = exercise_model.get_all()

    with ui.column().classes("page-content"):
        with page_header_row():
            page_title("Exercise Library")
            btn_primary("+ New Exercise", on_click=lambda: navigate("exercise_form"))

        if not exercises:
            ui.label("No exercises yet. Add your first one.").classes("meta-row")
            return

        section_title(pluralize(len(exercises), "exercise"))

        for ex in exercises:
            eid = ex._id
            with ui.row().classes("card items-center justify-between"):
                with ui.column().style("gap:2px"):
                    with ui.row().classes("items-center gap-2"):
                        ui.label(ex.short_name).classes("card-title")
                        if ex.label:
                            ui.label(ex.label).classes("meta-row").style("margin-top:0")
                    if ex.variant and ex.variant_label:
                        ui.label(f"{ex.variant} — {ex.variant_label}").classes("meta-row")
                    elif ex.variant:
                        ui.label(f"Variant {ex.variant}").classes("meta-row")
                with ui.row().classes("items-center gap-2"):
                    btn_ghost("Edit", on_click=lambda eid_=eid: navigate("exercise_form", eid_))
                    btn_danger("Delete", on_click=lambda eid_=eid: _delete(eid_, navigate))


def _delete(exercise_id: str, navigate: Callable[..., None]) -> None:
    exercise_model.delete(exercise_id)
    ui.notify("Exercise deleted")
    navigate("exercises")
