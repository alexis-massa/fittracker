# src/ui/pages/sessions.py
from collections.abc import Callable

from nicegui import ui

from src.models import session as session_model
from src.ui.components import btn_ghost
from src.ui.components import btn_primary
from src.ui.components import page_header_row
from src.ui.components import page_title
from src.ui.components import section_title
from src.utils.formatting import pluralize


def render(navigate: Callable[..., None]) -> None:
    sessions = session_model.get_all()

    with ui.column().classes("page-content"):
        with page_header_row():
            page_title("Sessions")
            btn_primary("+ New Session", on_click=lambda: navigate("session_form"))

        if not sessions:
            ui.label("No sessions yet. Log your first workout.").classes("meta-row")
            return

        section_title(pluralize(len(sessions), "session") + " logged")

        for s in sessions:
            sid = s.id
            energy_str = s.energy_level.name.replace("_", " ").title() if s.energy_level else "—"

            with ui.row().classes("card align-center justify-between"):
                with ui.column().style("gap:3px"):
                    ui.label(s.date).classes("card-title")
                    ui.label(
                        f"{pluralize(len(s.workout), 'exercise')} · "
                        f"{pluralize(len(s.warmup), 'warmup')} · "
                        f"{pluralize(len(s.stretches), 'stretch', 'stretches')} · "
                        f"{energy_str} energy · "
                        f"{s.progress.value.title()}"
                    ).classes("meta-row")
                btn_ghost("View →", on_click=lambda sid_=sid: navigate("session_detail", sid_))
