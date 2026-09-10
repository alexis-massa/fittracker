# src/ui/pages/session_run.py
from collections.abc import Callable
from dataclasses import dataclass

from nicegui import ui

from src.models import session as session_model
from src.models.exercise import SessionExercise
from src.models.session import Session
from src.ui.components import btn_ghost
from src.ui.components import btn_primary
from src.ui.components import page_title
from src.ui.components import tag


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
    index: int = 0
    remaining: int = 0
    paused: bool = False


def render(session_id: str | None) -> None:
    s = session_model.get_by_id(session_id) if session_id else None
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

        state = _RunState(remaining=phases[0].seconds)
        progress = ui.linear_progress(value=0, show_value=False).classes("w-full q-mb-md")
        content = ui.column().classes("w-full items-center")

        def advance() -> None:
            state.index += 1
            if state.index < len(phases):
                state.remaining = phases[state.index].seconds
                _beep()
            refresh()

        def tick() -> None:
            if state.paused or state.index >= len(phases):
                return
            phase = phases[state.index]
            if phase.seconds <= 0:
                return  # reps-based work: waits on manual "Series done"
            state.remaining -= 1
            if state.remaining <= 0:
                advance()
            else:
                refresh()

        def toggle_pause() -> None:
            state.paused = not state.paused
            refresh()

        def refresh() -> None:
            progress.set_value(min(state.index / len(phases), 1.0))
            content.clear()
            with content:
                if state.index >= len(phases):
                    _render_complete(s)
                else:
                    _render_phase(phases[state.index], state, advance, toggle_pause)

        ui.timer(1.0, tick)
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


def _render_phase(
    phase: _Phase,
    state: _RunState,
    advance: Callable[[], None],
    toggle_pause: Callable[[], None],
) -> None:
    ex = phase.exercise
    ui.label(
        f"{phase.group.upper()} · exercise {phase.exercise_index + 1}/{phase.total_exercises}"
    ).classes("text-caption opacity-70")
    with ui.row().classes("items-center gap-2 q-mb-sm"):
        ui.label(ex.short_name).classes("text-h5 text-weight-bold")
        if ex.variant_name:
            tag(ex.variant_name, accent=True)
    if ex.label or ex.variant_label:
        desc = " / ".join(filter(None, [ex.label, ex.variant_label]))
        ui.label(desc).classes("text-caption opacity-70 q-mb-md")

    if phase.kind == "rest":
        ui.label("REST").classes("text-caption opacity-70")
        ui.label(_mmss(state.remaining)).classes("text-h2 text-weight-bold q-my-md")
        ui.label(f"series {phase.series}/{ex.sets} next").classes("text-caption opacity-70 q-mb-md")
    elif phase.seconds > 0:
        ui.label(f"series {phase.series}/{ex.sets}").classes("text-caption opacity-70")
        ui.label(_mmss(state.remaining)).classes("text-h2 text-weight-bold q-my-md")
    else:
        ui.label(f"series {phase.series}/{ex.sets}").classes("text-caption opacity-70")
        ui.label(f"{ex.reps} reps").classes("text-h2 text-weight-bold q-my-md")
        btn_primary("Series done", on_click=advance)

    with ui.row().classes("items-center gap-2 q-mt-md"):
        if phase.kind == "rest" or phase.seconds > 0:
            btn_ghost("Pause" if not state.paused else "Resume", on_click=toggle_pause)
            btn_ghost("Skip", on_click=advance)


def _render_complete(s: Session) -> None:
    ui.label("Session complete").classes("text-h5 text-weight-bold q-mb-md")
    with ui.row().classes("items-center gap-2"):
        btn_primary("Back to session", on_click=lambda: ui.navigate.to(f"/sessions/{s.id}"))
        btn_ghost("All sessions", on_click=lambda: ui.navigate.to("/"))


def _mmss(seconds: int) -> str:
    minutes, secs = divmod(max(seconds, 0), 60)
    return f"{minutes:01d}:{secs:02d}"


def _beep() -> None:
    ui.run_javascript(
        "try {"
        "const c = new (window.AudioContext || window.webkitAudioContext)();"
        "const o = c.createOscillator();"
        "o.frequency.value = 880;"
        "o.connect(c.destination);"
        "o.start();"
        "setTimeout(() => o.stop(), 150);"
        "} catch (e) {}"
    )
