# src/ui/pages/session_form.py
from collections.abc import Callable

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
from src.ui.components import form_card
from src.ui.components import input_field
from src.ui.components import number_field
from src.ui.components import page_title
from src.ui.components import section_title
from src.ui.components import select_field
from src.ui.components import tag
from src.ui.components import textarea_field
from src.utils.formatting import today_iso

_ENERGY_OPTIONS: dict[int, str] = {e.value: e.name.replace("_", " ").title() for e in EnergyLevel}
_PROGRESS_OPTIONS: dict[str, str] = {p.value: p.value.title() for p in ProgressEnum}


def render(session_id: str | None, navigate: Callable[..., None]) -> None:
    existing = session_model.get_by_id(session_id) if session_id else None

    warmup_ids: list[str] = list(existing.warmup if existing else [])
    workout_ids: list[str] = list(existing.workout if existing else [])
    stretch_ids: list[str] = list(existing.stretches if existing else [])

    with ui.column().classes("page-content"):
        page_title("Edit Session" if existing else "New Session")

        section_title("Session info")
        with form_card():
            date_in = input_field(
                "Date (YYYY-MM-DD)",
                value=existing.date if existing else today_iso(),
            )
            ui.element("div").style("height:0.5rem")
            weight_in = number_field(
                "Bodyweight (kg)",
                value=existing.weight if existing and existing.weight is not None else 0.0,
                min=0,
                max=300,
            )
            ui.element("div").style("height:0.5rem")
            energy_in = select_field(
                "Energy Level",
                options=_ENERGY_OPTIONS,
                value=existing.energy_level.value
                if existing and existing.energy_level
                else EnergyLevel.MEDIUM.value,
            )
            ui.element("div").style("height:0.5rem")
            progress_in = select_field(
                "Progress",
                options=_PROGRESS_OPTIONS,
                value=existing.progress.value if existing else ProgressEnum.MAINTAIN.value,
            )
            ui.element("div").style("height:0.5rem")
            notes_in = textarea_field(
                "Notes",
                value=existing.notes if existing and existing.notes is not None else "",
            )

        ui.element("div").style("height:1.5rem")

        _exercise_group("Warmup", warmup_ids)
        ui.element("div").style("height:1.25rem")
        _exercise_group("Workout", workout_ids)
        ui.element("div").style("height:1.25rem")
        _exercise_group("Stretches", stretch_ids)

        ui.element("div").style("height:1rem")
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
                    warmup_ids,
                    workout_ids,
                    stretch_ids,
                    navigate,
                ),
            )
            btn_ghost("Cancel", on_click=lambda: navigate("sessions"))


def _exercise_group(title: str, id_list: list[str]) -> None:
    section_title(title)
    container = ui.column().style("width:100%;max-width:520px;gap:0")

    def refresh() -> None:
        container.clear()
        with container:
            for i, eid in enumerate(id_list):
                ex = exercise_model.get_by_id(eid)
                label = ex.display_name if ex else eid
                with ui.row().style("align-items:center;gap:8px;margin-bottom:4px;width:100%"):
                    ui.label(label).style("flex:1;font-size:0.82rem;color:#e8e4dc")
                    if ex and ex.variant:
                        tag(ex.variant, accent=True)
                    btn_danger("×", on_click=lambda idx=i: _remove(id_list, int(idx), refresh))

    refresh()

    all_ex = exercise_model.get_all()
    ex_map = {e.display_name: e.id for e in all_ex}
    ex_labels = list(ex_map.keys())

    with ui.row().style(
        "gap:8px;margin-top:0.5rem;max-width:520px;align-items:center;flex-wrap:wrap"
    ):
        if ex_labels:
            sel = select_field("Add existing", options=ex_labels).style(
                "flex:1;width:auto;min-width:180px"
            )
            btn_ghost("Add", on_click=lambda: _add_existing(id_list, ex_map, sel, refresh))
        btn_ghost("+ Create new", on_click=lambda: _show_inline_form(id_list, container, refresh))


def _remove(id_list: list[str], index: int, refresh: Callable[[], None]) -> None:
    id_list.pop(index)
    refresh()


def _add_existing(
    id_list: list[str],
    ex_map: dict[str, str],
    selector: ui.select,
    refresh: Callable[[], None],
) -> None:
    if selector.value and selector.value in ex_map:
        id_list.append(ex_map[selector.value])
        refresh()


def _show_inline_form(
    id_list: list[str],
    container: ui.column,
    refresh: Callable[[], None],
) -> None:
    with container, ui.card() as inline_card:
        ui.label("New Exercise").style(
            "font-size:0.72rem;color:#555;letter-spacing:0.1em;"
            "text-transform:uppercase;margin-bottom:0.5rem"
        )
        name_in = input_field("Name")
        ui.element("div").style("height:0.4rem")
        variant_in = input_field("Variant (e.g. A1)")
        ui.element("div").style("height:0.4rem")
        with ui.row().style("gap:0.5rem;width:100%"):
            sets_in = number_field("Sets", value=3, min=1, max=20).style("flex:1;width:auto")
            reps_in = number_field("Reps", value=10, min=1, max=200).style("flex:1;width:auto")
            rest_in = number_field("Rest (s)", value=90, min=0, max=600).style("flex:1;width:auto")
        ui.element("div").style("height:0.5rem")

        def save_inline() -> None:
            if not name_in.value.strip():
                ui.notify("Name is required", color="negative")
                return
            ex = Exercise(
                name=name_in.value.strip(),
                variant=variant_in.value.strip() or None,
                sets=int(sets_in.value or 3),
                reps=int(reps_in.value or 10),
                rest_seconds=int(rest_in.value or 90),
            )
            new_id = exercise_model.create(ex)
            id_list.append(new_id)
            inline_card.delete()
            refresh()
            ui.notify(f"'{ex.name}' created and added", color="positive")

        with ui.row().style("gap:0.5rem"):
            btn_primary("Save", on_click=save_inline)
            btn_ghost("Cancel", on_click=inline_card.delete)


def _save(
    session_id: str | None,
    date_in: ui.input,
    weight_in: ui.number,
    energy_in: ui.select,
    progress_in: ui.select,
    notes_in: ui.textarea,
    warmup_ids: list[str],
    workout_ids: list[str],
    stretch_ids: list[str],
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
        warmup=list(warmup_ids),
        workout=list(workout_ids),
        stretches=list(stretch_ids),
    )

    if session_id:
        session_model.update(session_id, s)
        ui.notify("Session updated", color="positive")
    else:
        session_model.create(s)
        ui.notify("Session saved", color="positive")

    navigate("sessions")
