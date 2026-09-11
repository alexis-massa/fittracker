# src/ui/pages/session_detail.py
from nicegui import ui

from src.models import session as session_model
from src.models.exercise import SessionExercise
from src.ui.components import btn_danger
from src.ui.components import btn_ghost
from src.ui.components import btn_primary
from src.ui.components import card_row
from src.ui.components import confirm_dialog
from src.ui.components import page_title
from src.ui.components import section_title
from src.ui.components import tag
from src.utils.formatting import pluralize


def render(session_id: str | None) -> None:
    if not session_id:
        ui.label("No session selected.").classes("text-caption opacity-70")
        return

    s = session_model.get_by_id(session_id)
    if not s:
        ui.label("Session not found.").classes("text-caption opacity-70")
        return

    with ui.column().classes("page-content"):
        btn_ghost("← Back", on_click=lambda: ui.navigate.to("/"))
        ui.element("div").classes("q-mb-sm")
        page_title(f"Session — {s.date}")

        with ui.row().classes("items-center gap-6 flex-wrap q-mb-lg"):
            if s.completed:
                energy_str = (
                    s.energy_level.name.replace("_", " ").title() if s.energy_level else "—"
                )
                ui.label(f"Energy: {energy_str}").classes("text-caption opacity-70")
                ui.label(f"Progress: {s.progress.value.title()}").classes("text-caption opacity-70")
                if s.weight:
                    ui.label(f"{s.weight} kg").classes("text-caption opacity-70")
                if s.notes:
                    ui.label(s.notes).classes("text-caption opacity-70").style("font-style:italic")
            else:
                tag("Not completed yet")

        ui.separator().classes("q-my-md")

        if s.warmup:
            _exercise_group(f"Warmup — {pluralize(len(s.warmup), 'exercise')}", s.warmup, dim=True)
            ui.separator().classes("q-my-md")

        _exercise_group(f"Workout — {pluralize(len(s.workout), 'exercise')}", s.workout)

        if s.stretches:
            ui.separator().classes("q-my-md")
            _exercise_group(
                f"Stretches — {pluralize(len(s.stretches), 'exercise')}", s.stretches, dim=True
            )

        ui.separator().classes("q-my-md")
        sid = s.id
        with ui.row().classes("items-center gap-2"):
            btn_primary("Start", on_click=lambda: ui.navigate.to(f"/sessions/{sid}/run"))
            btn_ghost("Edit", on_click=lambda: ui.navigate.to(f"/sessions/{sid}/edit"))
            btn_ghost("Duplicate", on_click=lambda: ui.navigate.to(f"/sessions/{sid}/duplicate"))
            btn_danger("Delete", on_click=lambda: _delete(sid))


def _exercise_group(title: str, exercises: list[SessionExercise], dim: bool = False) -> None:
    section_title(title)
    for ex in exercises:
        _exercise_row(ex, dim=dim)


def _exercise_row(ex: SessionExercise, dim: bool = False) -> None:
    opacity = "opacity:0.5;" if dim else ""
    with (
        card_row().style(opacity),
        ui.row().classes("w-full items-center"),
        ui.column().classes("flex-1").style("gap:3px"),
    ):
        with ui.row().classes("items-center gap-2"):
            ui.label(ex.short_name).classes("text-subtitle1 text-weight-bold")
            if ex.variant_name:
                tag(ex.variant_name, accent=True)
            if ex.label or ex.variant_label:
                desc = " / ".join(filter(None, [ex.label, ex.variant_label]))
                ui.label(desc).classes("text-caption opacity-70")
        ui.label(f"{ex.sets} sets · {ex.reps} reps · {ex.rest_seconds}s rest").classes(
            "text-caption opacity-70"
        )


def _delete(session_id: str) -> None:
    def do_delete() -> None:
        session_model.delete(session_id)
        ui.notify("Session deleted")
        ui.navigate.to("/")

    confirm_dialog("Delete this session? This cannot be undone.", do_delete)
