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
from src.ui.components import tag
from src.utils.formatting import pluralize


def render(navigate: Callable[..., None]) -> None:
    exercises = exercise_model.get_all()

    with ui.column().classes("page-content"):
        with page_header_row():
            page_title("Exercise Library")
            btn_primary("+ New Exercise", on_click=lambda: navigate("exercise_form"))

        if not exercises:
            ui.label("No exercises yet. Add your first one.").style("color:#555;font-size:0.82rem")
            return

        section_title(pluralize(len(exercises), "exercise"))

        for ex in exercises:
            eid = ex._id
            with ui.row().classes("card").style("align-items:center;justify-content:space-between"):
                with ui.column().style("gap:3px"):
                    with ui.row().style("align-items:center;gap:8px"):
                        ui.label(ex.name).classes("card-title")
                        if ex.variant:
                            tag(ex.variant, accent=True)
                    ui.label(f"{ex.sets} sets · {ex.reps} reps · {ex.rest_seconds}s rest").classes(
                        "meta-row"
                    )
                with ui.row().style("gap:8px"):
                    btn_ghost("Edit", on_click=lambda eid_=eid: navigate("exercise_form", eid_))
                    btn_danger("Delete", on_click=lambda eid_=eid: _delete(eid_, navigate))


def _delete(exercise_id: str, navigate: Callable[..., None]) -> None:
    exercise_model.delete(exercise_id)
    ui.notify("Exercise deleted")
    navigate("exercises")
