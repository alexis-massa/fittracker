# src/ui/pages/session_form.py
from collections.abc import Callable

from nicegui import ui

from src.models import session as session_model
from src.models.exercise import ExerciseDefinition
from src.models.exercise import SessionExercise
from src.models.exercise import create as create_definition
from src.models.exercise import get_all as get_library
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
from src.ui.components import textarea_field

_ENERGY_OPTIONS: dict[int, str] = {e.value: e.name.replace("_", " ").title() for e in EnergyLevel}
_PROGRESS_OPTIONS: dict[str, str] = {p.value: p.value.title() for p in ProgressEnum}


def render(session_id: str | None, navigate: Callable[..., None]) -> None:
    existing = session_model.get_by_id(session_id) if session_id else None

    warmup_exs: list[SessionExercise] = list(existing.warmup if existing else [])
    workout_exs: list[SessionExercise] = list(existing.workout if existing else [])
    stretch_exs: list[SessionExercise] = list(existing.stretches if existing else [])

    with ui.column().classes("page-content"):
        page_title("Edit Session" if existing else "New Session")

        section_title("Session info")
        with form_card(), ui.row().classes("w-full items-center gap-4 flex-wrap"):
            date_in = date_field("Date", value=existing.date if existing else None)
            weight_in = number_field(
                "Weight (kg)",
                value=existing.weight if existing and existing.weight is not None else 0.0,
                min=0,
                max=999,
                step=0.1,
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
            )

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


# ---------------------------------------------------------------------------
# Exercise group
# ---------------------------------------------------------------------------


def _exercise_group(title: str, ex_list: list[SessionExercise]) -> None:
    section_title(title)
    container = ui.column().classes("w-full").style("gap:0")

    def refresh() -> None:
        container.clear()
        with container:
            for i, ex in enumerate(ex_list):
                _exercise_row(ex, i, ex_list, container, refresh)

    refresh()
    btn_ghost(
        "+ Add exercise", on_click=lambda: _show_exercise_form(None, ex_list, container, refresh)
    )


# ---------------------------------------------------------------------------
# Exercise row
# ---------------------------------------------------------------------------


def _exercise_row(
    ex: SessionExercise,
    index: int,
    ex_list: list[SessionExercise],
    container: ui.column,
    refresh: Callable[[], None],
) -> None:
    with (
        ui.row()
        .classes("w-full items-center gap-2")
        .style("padding:0.35rem 0;border-bottom:1px solid var(--border)")
    ):
        with ui.column().style("gap:0"):
            ui.button(
                icon="expand_less", on_click=lambda idx=index: _move(ex_list, idx, -1, refresh)
            ).classes("btn-reorder")
            ui.button(
                icon="expand_more", on_click=lambda idx=index: _move(ex_list, idx, 1, refresh)
            ).classes("btn-reorder")
        with ui.column().classes("flex-1").style("gap:1px"):
            with ui.row().classes("items-center gap-2"):
                ui.label(ex.short_name).style("font-size:0.85rem;font-weight:600")
                if ex.label or ex.variant_label:
                    desc = " / ".join(filter(None, [ex.label, ex.variant_label]))
                    ui.label(desc).classes("meta-row").style("margin-top:0")
            ui.label(f"{ex.sets} sets · {ex.reps} reps · {ex.rest_seconds}s rest").classes(
                "meta-row"
            )
        btn_ghost(
            "Edit", on_click=lambda idx=index: _show_exercise_form(idx, ex_list, container, refresh)
        )
        btn_danger("×", on_click=lambda idx=index: _remove(ex_list, idx, refresh))


# ---------------------------------------------------------------------------
# Unified exercise form with cascading selects + free input
# ---------------------------------------------------------------------------


def _show_exercise_form(
    edit_index: int | None,
    ex_list: list[SessionExercise],
    container: ui.column,
    refresh: Callable[[], None],
) -> None:
    existing_ex = ex_list[edit_index] if edit_index is not None else None
    library = get_library()

    # Build lookup structures
    # name → label  (unique exercise families)
    name_map: dict[str, str] = {}
    for d in library:
        if d.name not in name_map:
            name_map[d.name] = d.label

    # (name, variant) → (variant_label, definition)
    variant_map: dict[tuple[str, str], tuple[str, ExerciseDefinition]] = {}
    for d in library:
        if d.variant:
            variant_map[(d.name, d.variant)] = (d.variant_label, d)

    # name select options: "A — Pushup" or just "A" if no label
    def name_option(n: str, lbl: str) -> str:
        return f"{n} — {lbl}" if lbl else n

    name_options = [name_option(name, label) for name, label in name_map.items()]

    with container, ui.card().classes("card-inline") as form_card_el:
        ui.label("Edit Exercise" if existing_ex else "Add Exercise").classes("inline-form-title")

        # ── Row 1: name + label ───────────────────────────────────────────
        with ui.row().classes("w-full items-center gap-2 flex-wrap"):
            # Name — select with free input
            name_sel = ui.select(
                options=name_options,
                value=name_option(existing_ex.name, existing_ex.label) if existing_ex else None,
                label="Exercise (e.g. A)",
                new_value_mode="add-unique",  # allows typing new values
                clearable=True,
            ).classes("flex-1 nicegui-select")

            label_in = input_field(
                "Name (e.g. Pushup)",
                value=existing_ex.label if existing_ex else "",
            ).classes("flex-1")

        ui.element("div").classes("spacer-sm")

        # ── Row 2: variant + variant_label ───────────────────────────────
        variant_options: list[str] = []  # populated when name is chosen

        def variant_option(v: str, vl: str) -> str:
            return f"{v} — {vl}" if vl else v

        variant_sel = ui.select(
            options=variant_options,
            value=variant_option(existing_ex.variant, existing_ex.variant_label)
            if existing_ex and existing_ex.variant
            else None,
            label="Variant (e.g. 1)",
            new_value_mode="add-unique",
            clearable=True,
        ).classes("flex-1 nicegui-select")

        variant_label_in = input_field(
            "Variant name (e.g. Wide)",
            value=existing_ex.variant_label if existing_ex else "",
        ).classes("flex-1")

        with ui.row().classes("w-full items-center gap-2 flex-wrap"):
            ui.element("div")  # placeholder so variant_sel and label are built before row

        # When name changes, refresh variant options and auto-fill label
        def on_name_change(value: str) -> None:
            raw = value.strip() if value else ""

            # Extract name part before " — " if user picked from list
            name_part = raw.split(" — ")[0].strip() if " — " in raw else raw

            # Auto-fill label if this name exists in library
            if name_part in name_map:
                label_in.value = name_map[name_part]

            # Rebuild variant options for this name
            opts = [
                variant_option(v, vl) for (n, v), (vl, _) in variant_map.items() if n == name_part
            ]
            variant_sel.options = opts
            variant_sel.update()
            variant_sel.value = None
            variant_label_in.value = ""

        name_sel.on_value_change(lambda e: on_name_change(e.value or ""))

        # When variant changes, auto-fill variant_label
        def on_variant_change(value: str) -> None:
            raw = value.strip() if value else ""
            v_part = raw.split(" — ")[0].strip() if " — " in raw else raw

            # Get current name
            name_raw = (name_sel.value or "").strip()
            name_part = name_raw.split(" — ")[0].strip() if " — " in name_raw else name_raw

            key = (name_part, v_part)
            if key in variant_map:
                variant_label_in.value = variant_map[key][0]

        variant_sel.on_value_change(lambda e: on_variant_change(e.value or ""))

        # Trigger initial variant population if editing
        if existing_ex:
            on_name_change(name_option(existing_ex.name, existing_ex.label))

        ui.element("div").classes("spacer-sm")

        # ── Row 3: sets / reps / rest ─────────────────────────────────────
        with ui.row().classes("w-full items-center gap-2 flex-wrap"):
            sets_in = number_field(
                "Sets", value=existing_ex.sets if existing_ex else 3, min=1, max=100
            ).classes("flex-1")
            reps_in = number_field(
                "Reps", value=existing_ex.reps if existing_ex else 10, min=1, max=200
            ).classes("flex-1")
            rest_in = number_field(
                "Rest (s)", value=existing_ex.rest_seconds if existing_ex else 90, min=0, max=3600
            ).classes("flex-1")

        ui.element("div").classes("spacer-sm")

        # ── Save ──────────────────────────────────────────────────────────
        def save() -> None:
            name_raw = (name_sel.value or "").strip()
            name_part = name_raw.split(" — ")[0].strip() if " — " in name_raw else name_raw

            if not name_part:
                ui.notify("Exercise name is required", color="negative")
                return

            label = label_in.value.strip()
            variant_raw = (variant_sel.value or "").strip()
            variant_part = (
                variant_raw.split(" — ")[0].strip() if " — " in variant_raw else variant_raw
            )
            variant = variant_part or None
            variant_label = variant_label_in.value.strip()

            # Check if this exact definition exists in library
            match = next(
                (d for d in library if d.name == name_part and d.variant == variant),
                None,
            )

            if match is None:
                # Create new definition in the library
                new_defn = ExerciseDefinition(
                    name=name_part,
                    label=label,
                    variant=variant,
                    variant_label=variant_label,
                )
                create_definition(new_defn)
                ui.notify(f"'{new_defn.display_name}' added to library", color="info")

            ex = SessionExercise(
                name=name_part,
                label=label,
                variant=variant,
                variant_label=variant_label,
                sets=int(sets_in.value or 3),
                reps=int(reps_in.value or 10),
                rest_seconds=int(rest_in.value or 90),
            )

            if edit_index is not None:
                ex_list[edit_index] = ex
            else:
                ex_list.append(ex)

            form_card_el.delete()
            refresh()
            ui.notify(
                f"'{ex.display_name}' updated"
                if edit_index is not None
                else f"'{ex.display_name}' added",
                color="positive",
            )

        with ui.row().classes("items-center gap-2"):
            btn_primary("Save", on_click=save)
            btn_ghost("Cancel", on_click=form_card_el.delete)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _remove(ex_list: list[SessionExercise], index: int, refresh: Callable[[], None]) -> None:
    ex_list.pop(index)
    refresh()


def _move(
    ex_list: list[SessionExercise], index: int, direction: int, refresh: Callable[[], None]
) -> None:
    target = index + direction
    if 0 <= target < len(ex_list):
        ex_list[index], ex_list[target] = ex_list[target], ex_list[index]
        refresh()


# ---------------------------------------------------------------------------
# Save session
# ---------------------------------------------------------------------------


def _save(
    session_id: str | None,
    date_in: ui.input,
    weight_in: ui.number,
    energy_in: ui.select,
    progress_in: ui.select,
    notes_in: ui.textarea,
    warmup_exs: list[SessionExercise],
    workout_exs: list[SessionExercise],
    stretch_exs: list[SessionExercise],
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
        warmup=list(warmup_exs),
        workout=list(workout_exs),
        stretches=list(stretch_exs),
    )

    if session_id:
        session_model.update(session_id, s)
        ui.notify("Session updated", color="positive")
    else:
        session_model.create(s)
        ui.notify("Session saved", color="positive")

    navigate("sessions")
