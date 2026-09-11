# src/ui/components/session_info_fields.py
from dataclasses import dataclass

from nicegui import ui

from src.models.session import EnergyLevel
from src.models.session import ProgressEnum
from src.models.session import Session
from src.ui.components.date_field import date_field
from src.ui.components.number_field import number_field
from src.ui.components.select_field import select_field
from src.ui.components.textarea_field import textarea_field
from src.ui.validation import clear_error
from src.ui.validation import flag_error

_ENERGY_OPTIONS: dict[int, str] = {e.value: e.name.replace("_", " ").title() for e in EnergyLevel}
_PROGRESS_OPTIONS: dict[str, str] = {p.value: p.value.title() for p in ProgressEnum}


@dataclass
class SessionInfoInputs:
    date: ui.input
    weight: ui.number
    energy: ui.select
    progress: ui.select
    notes: ui.textarea


def session_info_fields(
    existing: Session | None, default_weight: float | None = None
) -> SessionInfoInputs:
    """Render the "how did it go" fields (date, weight, energy, progress, notes).

    `existing` pre-fills values when editing an already-completed session;
    pass None for a fresh reflection (defaults to today, Medium, Maintain).
    `default_weight` fills the weight field when `existing` has none - e.g.
    carrying over the last logged weight into a fresh reflection.
    """
    date_in = date_field("Date", value=existing.date if existing else None).classes("flex-1")
    weight_in = number_field(
        "Weight (kg)",
        value=(
            existing.weight
            if existing and existing.weight is not None
            else (default_weight if default_weight is not None else 0.0)
        ),
        min=0,
        max=999,
        step=0.1,
    ).classes("flex-1")
    energy_in = select_field(
        "Energy",
        options=_ENERGY_OPTIONS,
        value=existing.energy_level.value
        if existing and existing.energy_level
        else EnergyLevel.MEDIUM.value,
    ).classes("flex-1")
    progress_in = select_field(
        "Progress",
        options=_PROGRESS_OPTIONS,
        value=existing.progress.value if existing else ProgressEnum.MAINTAIN.value,
    ).classes("flex-1")
    notes_in = textarea_field(
        "Notes",
        value=existing.notes if existing and existing.notes is not None else "",
    ).classes("flex-1")

    date_in.on_value_change(lambda: clear_error(date_in))
    return SessionInfoInputs(date_in, weight_in, energy_in, progress_in, notes_in)


def apply_session_info(session: Session, inputs: SessionInfoInputs) -> bool:
    """Validate `inputs` and apply them onto `session`, marking it completed.

    Returns False (and flags the date field) without changing `session` if
    the date is missing.
    """
    clear_error(inputs.date)
    if not str(inputs.date.value).strip():
        flag_error(inputs.date, "Date is required")
        ui.notify("Date is required", color="negative")
        return False

    session.date = str(inputs.date.value).strip()
    session.weight = float(inputs.weight.value) if inputs.weight.value else None
    session.energy_level = EnergyLevel(int(inputs.energy.value)) if inputs.energy.value else None
    session.progress = ProgressEnum(inputs.progress.value)
    session.notes = inputs.notes.value.strip() or None
    session.completed = True
    return True
