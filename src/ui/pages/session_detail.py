# src/ui/pages/session_detail.py
from collections.abc import Callable

from nicegui import ui

from src.models import exercise as exercise_model
from src.models import session as session_model
from src.models.exercise import Exercise
from src.ui.components import btn_danger
from src.ui.components import btn_ghost
from src.ui.components import page_title
from src.ui.components import section_title
from src.ui.components import tag
from src.utils.formatting import pluralize


def render(session_id: str | None, navigate: Callable[..., None]) -> None:
    if not session_id:
        ui.label("No session selected.").style("color:#555")
        return

    s = session_model.get_by_id(session_id)
    if not s:
        ui.label("Session not found.").style("color:#555")
        return

    with ui.column().classes("page-content"):
        btn_ghost("← Back", on_click=lambda: navigate("sessions"))
        ui.element("div").style("height:0.75rem")

        page_title(f"Session — {s.date}")

        # ── Meta strip ────────────────────────────────────────────────────
        energy_str = s.energy_level.name.replace("_", " ").title() if s.energy_level else "—"
        with ui.row().style("gap:1.2rem;align-items:center;margin-bottom:1.5rem;flex-wrap:wrap"):
            ui.label(f"Energy: {energy_str}").style("color:#888;font-size:0.78rem")
            ui.label(f"Progress: {s.progress.value.title()}").style("color:#888;font-size:0.78rem")
            if s.weight:
                ui.label(f"{s.weight} kg").style("color:#666;font-size:0.78rem")
            if s.notes:
                ui.label(s.notes).style("color:#555;font-size:0.78rem;font-style:italic")

        ui.html('<hr class="divider">')

        # ── Exercise groups ───────────────────────────────────────────────
        if s.warmup:
            _exercise_group(f"Warmup — {pluralize(len(s.warmup), 'exercise')}", s.warmup, dim=True)
            ui.html('<hr class="divider">')

        _exercise_group(
            f"Workout — {pluralize(len(s.workout), 'exercise')}",
            s.workout,
        )

        if s.stretches:
            ui.html('<hr class="divider">')
            _exercise_group(
                f"Stretches — {pluralize(len(s.stretches), 'exercise')}", s.stretches, dim=True
            )

        # ── Actions ───────────────────────────────────────────────────────
        ui.html('<hr class="divider">')
        sid = s.id
        with ui.row().style("gap:0.75rem"):
            btn_ghost("Edit", on_click=lambda: navigate("session_form", sid))
            btn_danger("Delete", on_click=lambda: _delete(sid, navigate))


def _exercise_group(title: str, exercises: list[Exercise], dim: bool = False) -> None:
    section_title(title)
    for ex in exercises:
        _exercise_row(ex, dim=dim)


def _exercise_row(exercise: Exercise, dim: bool = False) -> None:
    color = "#666" if dim else "#e8e4dc"
    opacity = "opacity:0.6;" if dim else ""
    card = ui.row().classes("card").style(f"align-items:center;{opacity}")
    column = ui.column().style("gap:3px")
    row = ui.row().style("align-items:center;gap:8px")
    with card and column and row:
        ui.label(exercise.name).style(
            f"font-family:'Syne',sans-serif;font-weight:600;font-size:0.9rem;color:{color}"
        )
        if exercise.variant:
            tag(exercise.variant, accent=True)
        ui.label(
            f"{exercise.sets} sets · {exercise.reps} reps · {exercise.rest_seconds}s rest"
        ).classes("meta-row")


def _delete(session_id: str, navigate: Callable[..., None]) -> None:
    session_model.delete(session_id)
    ui.notify("Session deleted")
    navigate("sessions")
