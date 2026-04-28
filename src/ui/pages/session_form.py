# src/ui/pages/session_form.py
from collections.abc import Callable
import copy

from nicegui import ui

from src.models import exercise as exercise_model
from src.models import session as session_model
from src.models.exercise import Exercise
from src.models.session import EnergyLevel
from src.models.session import ProgressEnum
from src.models.session import Session
from src.ui.components import action_row
from src.ui.components import btn_danger
from src.ui.components import btn_ghost
from src.ui.components import btn_primary
from src.ui.components import date_field
from src.ui.components import form_card
from src.ui.components import input_field
from src.ui.components import number_field
from src.ui.components import page_title
from src.ui.components import section_title
from src.ui.components import select_field
from src.ui.components import tag
from src.ui.components import textarea_field

_ENERGY_OPTIONS: dict[int, str] = {e.value: e.name.replace("_", " ").title() for e in EnergyLevel}
_PROGRESS_OPTIONS: dict[str, str] = {p.value: p.value.title() for p in ProgressEnum}


def render(session_id: str | None, navigate: Callable[..., None]) -> None:
    existing = session_model.get_by_id(session_id) if session_id else None

    warmup_exs: list[Exercise] = list(existing.warmup if existing else [])
    workout_exs: list[Exercise] = list(existing.workout if existing else [])
    stretch_exs: list[Exercise] = list(existing.stretches if existing else [])

    with ui.column().classes("page-content"):
        page_title("Edit Session" if existing else "New Session")

        section_title("Session info")
        with form_card(), ui.row().classes("w-full justify-stretch"):
            date_in = date_field(
                "Date",
                value=existing.date if existing else None,
            )

            weight_in = number_field(
                "Weight",
                value=existing.weight if existing and existing.weight is not None else 0.0,
                min=0,
                max=999,
                step=0.1
            )

            energy_in = select_field(
                "Energy",
                options=_ENERGY_OPTIONS,
                value=existing.energy_level.value
                if existing and existing.energy_level
                else EnergyLevel.MEDIUM.value,
            )

            progress_in = select_field(
                "Progress",
                options=_PROGRESS_OPTIONS,
                value=existing.progress.value if existing else ProgressEnum.MAINTAIN.value,
            )

            notes_in = textarea_field(
                "Notes",
                value=existing.notes if existing and existing.notes is not None else "",
            ).classes("grow-1")


        _exercise_group("Warmup", warmup_exs)
        _exercise_group("Workout", workout_exs)
        _exercise_group("Stretches", stretch_exs)

        with action_row():
            btn_primary(
                "Save Session",
                on_click=lambda: _save(
                    session_id,
                    date_in,
                    weight_in,
                    energy_in,
                    progress_in,
                    notes_in,
                    warmup_exs,
                    workout_exs,
                    stretch_exs,
                    navigate,
                ),
            )
            btn_ghost("Cancel", on_click=lambda: navigate("sessions"))


def _exercise_group(title: str, ex_list: list[Exercise]) -> None:
    section_title(title)
    container = ui.column().classes("w-full").style("gap:0")

    def refresh() -> None:
        container.clear()
        with container:
            for i, ex in enumerate(ex_list):
                label = ex.display_name if ex else ex.id
                with ui.row().classes("c-full align-center").style("gap:8px;margin-bottom:4px"):
                    ui.label(label).style("flex:1;font-size:0.82rem;color:#e8e4dc")
                    if ex.variant:
                        tag(ex.variant, accent=True)
                    btn_danger("×", on_click=lambda idx=i: _remove(ex_list, idx, refresh))

    refresh()

    ex_map = {e.display_name: e for e in exercise_model.get_all()}
    ex_labels = list(ex_map.keys())

    with ui.row().classes("align-center").style("gap:8px;margin-top:0.5rem"):
        if ex_labels:
            sel = select_field("Add existing", options=ex_labels).style(
                "flex:1;width:auto;min-width:180px"
            )
            btn_ghost("Add", on_click=lambda: _add_existing(ex_list, ex_map, sel, refresh))
        btn_ghost("+ Create new", on_click=lambda: _show_inline_form(ex_list, container, refresh))


def _remove(ex_list: list[Exercise], index: int, refresh: Callable[[], None]) -> None:
    ex_list.pop(index)
    refresh()


def _add_existing(
    ex_list: list[Exercise],
    ex_map: dict[str, Exercise],
    selector: ui.select,
    refresh: Callable[[], None],
) -> None:
    if selector.value and selector.value in ex_map:
        ex_list.append(copy.deepcopy(ex_map[selector.value]))
    refresh()


def _show_inline_form(
    exercises: list[Exercise],
    container: ui.column,
    refresh: Callable[[], None],
) -> None:
    with (
        container,
        ui.card().classes("w-full") as inline_card,
        ui.row().classes("w-full items-center gap-2 no-wrap"),
    ):
        name_in = input_field("Name").classes("flex-1")
        variant_in = input_field("Variant").classes("flex-1")
        sets_in = number_field("Sets", value=3, min=1, max=20).classes("flex-1")
        reps_in = number_field("Reps", value=10, min=1, max=200).classes("flex-1")
        rest_in = number_field("Rest (s)", value=90, min=0, max=3600).classes("flex-1")

        def save_inline() -> None:
            if not name_in.value.strip():
                ui.notify("Name is required", color="negative")
                return

            new_exercise = Exercise(
                name=name_in.value.strip(),
                variant=variant_in.value.strip() or None,
                sets=int(sets_in.value or 3),
                reps=int(reps_in.value or 10),
                rest_seconds=int(rest_in.value or 90),
            )

            exercises.append(new_exercise)
            inline_card.delete()
            refresh()
            ui.notify(f"'{new_exercise.display_name}' added", color="positive")

        btn_primary("✓", on_click=save_inline)
        btn_ghost("✕", on_click=inline_card.delete)


def _save(
    session_id: str | None,
    date_in: ui.input,
    weight_in: ui.number,
    energy_in: ui.select,
    progress_in: ui.select,
    notes_in: ui.textarea,
    warmup_exs: list[Exercise],
    workout_exs: list[Exercise],
    stretch_exs: list[Exercise],
    navigate: Callable[..., None],
) -> None:
    if not str(date_in.value).strip():
        ui.notify("Date is required", color="negative")
        return

    s = Session(
        date=str(date_in.value).strip(),
        weight=float(weight_in.value) if weight_in.value else None,
        energy_level=EnergyLevel(int(energy_in.value)) if energy_in.value else None,
        progress=ProgressEnum(progress_in.value),
        notes=notes_in.value.strip() or None,
        warmup=warmup_exs,
        workout=workout_exs,
        stretches=stretch_exs,
    )

    if session_id:
        session_model.update(session_id, s)
        ui.notify("Session updated", color="positive")
    else:
        session_model.create(s)
        ui.notify("Session saved", color="positive")

    navigate("sessions")
