# src/ui/pages/sessions.py
from nicegui import ui

from src.models import session as session_model
from src.ui.components import btn_ghost
from src.ui.components import btn_primary
from src.ui.components import card_row
from src.ui.components import page_header_row
from src.ui.components import page_title
from src.utils.formatting import pluralize


def render() -> None:
    sessions = session_model.get_all()

    with ui.column().classes("page-content"):
        with page_header_row():
            page_title("Sessions")
            btn_primary("+ New Session", on_click=lambda: ui.navigate.to("/sessions/new"))

        if not sessions:
            ui.label("No sessions yet. Log your first workout.").classes("text-caption")
        else:
            ui.label(pluralize(len(sessions), "session") + " logged").classes("text-caption")

        for s in sessions:
            sid = s.id
            energy_str = s.energy_level.name.replace("_", " ").title() if s.energy_level else "—"

            with card_row(), ui.row().classes("w-full items-center justify-between"):
                with ui.column().style("gap:3px"):
                    ui.label(s.date).classes("text-subtitle1 text-weight-bold")
                    ui.label(
                        f"{pluralize(len(s.workout), 'exercise')} · "
                        f"{pluralize(len(s.warmup), 'warmup')} · "
                        f"{pluralize(len(s.stretches), 'stretch', 'stretches')} · "
                        f"{energy_str} energy · "
                        f"{s.progress.value.title()}"
                    ).classes("text-caption opacity-70")
                with ui.row().classes("items-center gap-2"):
                    btn_ghost(
                        "Duplicate",
                        on_click=lambda sid_=sid: ui.navigate.to(f"/sessions/{sid_}/duplicate"),
                    )
                    btn_ghost(
                        "View →", on_click=lambda sid_=sid: ui.navigate.to(f"/sessions/{sid_}")
                    )
