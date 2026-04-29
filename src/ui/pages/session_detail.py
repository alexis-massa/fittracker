# src/ui/pages/session_detail.py
from collections.abc import Callable

from nicegui import ui

from src.models import session as session_model
from src.models.exercise import SessionExercise
from src.ui.components import btn_danger
from src.ui.components import btn_ghost
from src.ui.components import page_title
from src.ui.components import section_title
from src.ui.components import tag
from src.utils.formatting import pluralize


def render(session_id: str | None, navigate: Callable[..., None]) -> None:
    if not session_id:
        ui.label("No session selected.").classes("meta-row")
        return

    s = session_model.get_by_id(session_id)
    if not s:
        ui.label("Session not found.").classes("meta-row")
        return

    with ui.column().classes("page-content"):
        btn_ghost("← Back", on_click=lambda: navigate("sessions"))
        ui.element("div").classes("spacer-sm")
        page_title(f"Session — {s.date}")

        # ── Meta ─────────────────────────────────────────────────────────
        energy_str = s.energy_level.name.replace("_", " ").title() if s.energy_level else "—"
        with ui.row().classes("items-center gap-6 flex-wrap").style("margin-bottom:1.5rem"):
            ui.label(f"Energy: {energy_str}").classes("meta-row")
            ui.label(f"Progress: {s.progress.value.title()}").classes("meta-row")
            if s.weight:
                ui.label(f"{s.weight} kg").classes("meta-row")
            if s.notes:
                ui.label(s.notes).classes("meta-row").style("font-style:italic")

        ui.html('<hr class="divider">')

        if s.warmup:
            _exercise_group(f"Warmup — {pluralize(len(s.warmup), 'exercise')}", s.warmup, dim=True)
            ui.html('<hr class="divider">')

        _exercise_group(f"Workout — {pluralize(len(s.workout), 'exercise')}", s.workout)

        if s.stretches:
            ui.html('<hr class="divider">')
            _exercise_group(
                f"Stretches — {pluralize(len(s.stretches), 'exercise')}", s.stretches, dim=True
            )

        ui.html('<hr class="divider">')
        sid = s.id
        with ui.row().classes("items-center gap-2"):
            btn_ghost("Edit", on_click=lambda: navigate("session_form", sid))
            btn_danger("Delete", on_click=lambda: _delete(sid, navigate))


def _exercise_group(title: str, exercises: list[SessionExercise], dim: bool = False) -> None:
    section_title(title)
    for ex in exercises:
        _exercise_row(ex, dim=dim)


def _exercise_row(ex: SessionExercise, dim: bool = False) -> None:
    opacity = "opacity:0.5;" if dim else ""
    with (
        ui.row().classes("card items-center").style(opacity),
        ui.column().classes("flex-1").style("gap:3px"),
    ):
        with ui.row().classes("items-center gap-2"):
            ui.label(ex.name).classes("card-title")
            if ex.variant:
                tag(ex.variant, accent=True)
        ui.label(f"{ex.sets} sets · {ex.reps} reps · {ex.rest_seconds}s rest").classes("meta-row")


def _delete(session_id: str, navigate: Callable[..., None]) -> None:
    session_model.delete(session_id)
    ui.notify("Session deleted")
    navigate("sessions")
