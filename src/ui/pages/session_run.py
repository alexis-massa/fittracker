# src/ui/pages/session_run.py
from collections.abc import Callable
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from nicegui import ui
from nicegui.events import GenericEventArguments

from src.auth import current_user_id
from src.models import session as session_model
from src.models.exercise import SessionExercise
from src.models.session import Session
from src.ui.components import btn_danger
from src.ui.components import btn_ghost
from src.ui.components import btn_primary
from src.ui.components import exercise_pictogram
from src.ui.components import form_card
from src.ui.components import page_title
from src.ui.components.session_info_fields import apply_session_info
from src.ui.components.session_info_fields import session_info_fields

_RUNNER_JS = Path(__file__).resolve().parents[3] / "static" / "runner.js"
# The mtime busts the browser cache whenever runner.js changes.
_RUNNER_URL = f"/static/runner.js?v={int(_RUNNER_JS.stat().st_mtime)}"
_ICON_URL = "/static/icons/icon-512.png"


@dataclass
class _Phase:
    kind: str  # "rest" or "work"
    group: str
    exercise: SessionExercise
    series: int
    exercise_index: int
    total_exercises: int
    seconds: int  # countdown length; 0 for reps-based work (advanced manually)


@dataclass
class _RunState:
    """Mirror of the browser-side timer, which owns the clock; this only drives what's shown."""

    index: int = 0
    paused: bool = False
    started: bool = False
    saved: bool = False


def render(session_id: str | None) -> None:
    s = session_model.get_by_id(current_user_id(), session_id) if session_id else None
    if not s:
        ui.label("Session not found.").classes("text-caption opacity-70")
        return

    phases = _build_phases(s)

    with ui.column().classes("page-content items-center"):
        btn_ghost("← Back", on_click=lambda: ui.navigate.to(f"/sessions/{s.id}"))
        ui.element("div").classes("q-mb-sm")
        page_title(f"Session — {s.date}")

        if not phases:
            ui.label("This session has no exercises to run.").classes("text-caption opacity-70")
            return

        ui.add_head_html(
            f'<script src="{_RUNNER_URL}"></script>'
            f"<script>FitRunner.init({_script_json(_runner_config(s, phases))});</script>"
        )

        state = _RunState()
        progress = ui.linear_progress(value=0, show_value=False).classes("w-full q-mb-md")
        content = ui.column().classes("w-full items-center")

        def refresh() -> None:
            progress.set_value(min(state.index / len(phases), 1.0))
            content.clear()
            with content:
                if not state.started:
                    _render_ready()
                elif state.index >= len(phases):
                    if state.saved:
                        _render_saved(s)
                    else:
                        _render_reflect(s, state, refresh)
                else:
                    _render_phase(phases[state.index], state)

        def on_run_state(e: GenericEventArguments) -> None:
            update = (e.args["index"], e.args["paused"], e.args["started"])
            if update == (state.index, state.paused, state.started):
                return
            state.index, state.paused, state.started = update
            refresh()

        ui.on("run_state", on_run_state)
        refresh()


def _build_phases(s: Session) -> list[_Phase]:
    groups = [("Warmup", s.warmup), ("Workout", s.workout), ("Stretches", s.stretches)]
    all_exercises = [ex for _, exercises in groups for ex in exercises]

    phases: list[_Phase] = []
    exercise_index = 0
    for group_label, exercises in groups:
        for ex in exercises:
            for series in range(1, ex.sets + 1):
                rest = ex.rest_before if series == 1 else ex.rest_seconds
                if rest > 0:
                    phases.append(
                        _Phase(
                            "rest",
                            group_label,
                            ex,
                            series,
                            exercise_index,
                            len(all_exercises),
                            rest,
                        )
                    )
                phases.append(
                    _Phase(
                        "work",
                        group_label,
                        ex,
                        series,
                        exercise_index,
                        len(all_exercises),
                        ex.duration,
                    )
                )
            exercise_index += 1
    return phases


def _runner_config(s: Session, phases: list[_Phase]) -> dict[str, Any]:
    return {
        "name": f"Session {s.date}",
        "backUrl": f"/sessions/{s.id}",
        "icon": _ICON_URL,
        "phases": [_phase_payload(p) for p in phases],
    }


def _phase_payload(phase: _Phase) -> dict[str, Any]:
    ex = phase.exercise
    name = " ".join(filter(None, [ex.short_name, ex.label]))
    subtitle = (
        f"Series {phase.series}/{ex.sets} · "
        f"{phase.group} {phase.exercise_index + 1}/{phase.total_exercises}"
    )
    if phase.kind == "work" and phase.seconds <= 0:
        subtitle += f" · {ex.reps} reps"
    return {
        "seconds": phase.seconds,
        "title": f"{'Rest' if phase.kind == 'rest' else 'Work'} · {name}",
        "subtitle": subtitle,
    }


def _script_json(data: Any) -> str:
    """JSON safe to embed in an inline <script> (exercise labels are user-typed)."""
    return json.dumps(data).replace("<", "\\u003c")


def _client_button(button: ui.button, js: str) -> ui.button:
    """Run `js` in the browser on click: audio and the timer must start from a real tap."""
    return button.on("click", js_handler=f"() => {js}")


def _render_ready() -> None:
    ui.label("Ready?").classes("text-h5 text-weight-bold q-mb-sm")
    ui.label("Keeps the screen on and puts pause / skip on your lock screen.").classes(
        "text-caption opacity-70 q-mb-md"
    )
    _client_button(btn_primary("Start workout"), "FitRunner.begin()")


def _render_phase(phase: _Phase, state: _RunState) -> None:
    ex = phase.exercise
    ui.label(
        f"{phase.group.upper()} · exercise {phase.exercise_index + 1}/{phase.total_exercises}"
    ).classes("text-caption opacity-70")
    ui.label(ex.short_name).classes("text-h5 text-weight-bold q-mb-sm")
    if ex.label or ex.variant_label:
        desc = " / ".join(filter(None, [ex.label, ex.variant_label]))
        ui.label(desc).classes("text-caption opacity-70 q-mb-md")
    exercise_pictogram(ex.name, size="96px")

    if phase.kind == "rest":
        ui.label("REST").classes("text-caption opacity-70")
        _clock(phase.seconds)
        ui.label(f"series {phase.series}/{ex.sets} next").classes("text-caption opacity-70 q-mb-md")
    elif phase.seconds > 0:
        ui.label(f"series {phase.series}/{ex.sets}").classes("text-caption opacity-70")
        _clock(phase.seconds)
    else:
        ui.label(f"series {phase.series}/{ex.sets}").classes("text-caption opacity-70")
        ui.label(f"{ex.reps} reps").classes("text-h2 text-weight-bold q-my-md")
        _client_button(btn_primary("Series done"), "FitRunner.next()")

    with ui.row().classes("items-center gap-2 q-mt-md"):
        _client_button(btn_ghost("Resume" if state.paused else "Pause"), "FitRunner.toggle()")
        _client_button(btn_ghost("Skip"), "FitRunner.next()")
        _client_button(btn_ghost("Restart"), "FitRunner.restartPhase()")
    with ui.row().classes("items-center gap-2 q-mt-sm"):
        _client_button(
            btn_ghost("Reset workout"),
            "confirm('Start the whole workout over?') && FitRunner.restartWorkout()",
        )
        _client_button(
            btn_danger("Stop"),
            "confirm('Stop this workout? Nothing is saved.') && FitRunner.stop()",
        )


def _clock(seconds: int) -> None:
    # The browser rewrites this text every 250ms; the server only sets its starting value.
    ui.label(_mmss(seconds)).props("id=run-clock").classes("text-h2 text-weight-bold q-my-md")


def _render_reflect(s: Session, state: _RunState, refresh: Callable[[], None]) -> None:
    ui.label("Session complete — how did it go?").classes("text-h5 text-weight-bold q-mb-md")
    last_completed = session_model.get_last_completed(current_user_id())
    default_weight = last_completed.weight if last_completed else None
    with form_card(), ui.row().classes("w-full items-center gap-4 flex-wrap"):
        info = session_info_fields(s, default_weight=default_weight)

    def save() -> None:
        if not apply_session_info(s, info):
            return
        session_model.update(current_user_id(), s.id, s)
        ui.notify("Session saved", color="positive")
        state.saved = True
        refresh()

    with ui.row().classes("items-center gap-2"):
        btn_primary("Save", on_click=save)
        btn_ghost("Skip", on_click=lambda: ui.navigate.to(f"/sessions/{s.id}"))


def _render_saved(s: Session) -> None:
    ui.label("Session saved").classes("text-h5 text-weight-bold q-mb-md")
    with ui.row().classes("items-center gap-2"):
        btn_primary("Back to session", on_click=lambda: ui.navigate.to(f"/sessions/{s.id}"))
        btn_ghost("All sessions", on_click=lambda: ui.navigate.to("/"))


def _mmss(seconds: int) -> str:
    minutes, secs = divmod(max(seconds, 0), 60)
    return f"{minutes:01d}:{secs:02d}"
