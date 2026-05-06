# src/ui/pages/session_form.py
from collections.abc import Callable

from nicegui import ui

from src.models import session as session_model
from src.models.exercise import ExerciseDefinition
from src.models.exercise import ExerciseVariant
from src.models.exercise import SessionExercise
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
from src.ui.components import number_field
from src.ui.components import page_title
from src.ui.components import section_title
from src.ui.components import select_field
from src.ui.components import textarea_field
from src.ui.pages.exercise_create_form import exercise_create_form

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
            date_in = date_field("Date", value=existing.date if existing else None).classes(
                "flex-1"
            )
            weight_in = number_field(
                "Weight (kg)",
                value=existing.weight if existing and existing.weight is not None else 0.0,
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
    container = ui.column().classes("w-full")

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
    with ui.row().classes("w-full items-center gap-2"):
        with ui.column():
            ui.button(
                icon="expand_less", on_click=lambda idx=index: _move(ex_list, idx, -1, refresh)
            ).props("size=sm square outline")
            ui.button(
                icon="expand_more", on_click=lambda idx=index: _move(ex_list, idx, 1, refresh)
            ).props("size=sm square outline")
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
# Exercise pick + effort form
# ---------------------------------------------------------------------------


def _show_exercise_form(
    edit_index: int | None,
    ex_list: list[SessionExercise],
    container: ui.column,
    refresh: Callable[[], None],
) -> None:
    existing_ex = ex_list[edit_index] if edit_index is not None else None
    library = get_library()

    # name → (label, list of ExerciseVariant)
    lib_map: dict[str, tuple[str, list[ExerciseVariant]]] = {}
    for d in library:
        lib_map[d.name] = (d.label, d.variants)

    def name_opts() -> dict[str, str]:
        return {n: f"{n} — {lbl}" if lbl else n for n, (lbl, _) in lib_map.items()}

    def variant_opts(name: str) -> dict[str, str]:
        _, variants = lib_map.get(name, ("", []))
        return {v.name: v.display_name for v in variants}

    with container, form_card() as form_card_el:
        ui.label("Edit Exercise" if existing_ex else "Add Exercise").classes("inline-form-title")

        create_slot = ui.column().classes("w-full")

        with ui.row().classes("w-full items-center gap-2 flex-wrap"):
            name_sel = ui.select(
                options=name_opts(),
                value=existing_ex.name if existing_ex else None,
                label="Exercise",
                clearable=True,
            ).classes("flex-1 nicegui-select")

            variant_sel = ui.select(
                options=variant_opts(existing_ex.name) if existing_ex else {},
                value=existing_ex.variant_name
                if existing_ex and existing_ex.variant_name
                else None,
                label="Variant",
                clearable=True,
            ).classes("flex-1 nicegui-select")

        def on_name_change(value: str | None) -> None:
            name = value or ""
            variant_sel.options = variant_opts(name)
            variant_sel.value = None
            variant_sel.update()

        name_sel.on_value_change(lambda e: on_name_change(e.value))

        def on_exercise_created(new_defn: ExerciseDefinition) -> None:
            lib_map[new_defn.name] = (new_defn.label, new_defn.variants)
            name_sel.options = name_opts()
            name_sel.value = new_defn.name
            name_sel.update()
            on_name_change(new_defn.name)

        def show_create() -> None:
            create_slot.clear()
            exercise_create_form(create_slot, on_exercise_created)

        ui.link("+ Create new exercise", target="#").on("click", lambda _: show_create()).classes(
            "meta-row"
        ).style("cursor:pointer;color:var(--accent);text-decoration:none")

        ui.element("div").classes("spacer-sm")

        with ui.row().classes("w-full items-center gap-2 flex-wrap"):
            ui.label("After resting ").classes("text-sm text-gray-500")
            rest_before_in = number_field(
                "Rest before (s)",
                value=existing_ex.rest_before if existing_ex else 0,
                min=1,
                max=100,
                suffix="seconds",
            ).classes("flex-1")
            ui.label(": Do ").classes("text-sm text-gray-500")
            sets_in = number_field(
                "Sets", value=existing_ex.sets if existing_ex else 3, min=1, max=100, suffix="sets"
            ).classes("flex-1")
            ui.label(" of either ").classes("text-sm text-gray-500")
            with ui.row().classes("flex-1 items-center gap-2 no-wrap"):
                with ui.column():
                    ui.label("⎧").classes("text-xl text-gray-500")
                    ui.label("⎩").classes("text-xl text-gray-500")
                with ui.column().classes("w-full gap-1"):
                    reps_in = number_field(
                        "Reps",
                        value=existing_ex.reps if existing_ex else 10,
                        min=1,
                        max=200,
                        suffix="reps",
                    ).classes("w-full")
                    duration_in = number_field(
                        "Duration (s)",
                        value=existing_ex.duration if existing_ex else 0,
                        min=1,
                        max=999,
                        suffix="seconds",
                    ).classes("w-full")
            ui.label("with").classes("text-sm text-gray-500")
            rest_in = number_field(
                "Rest (s)",
                value=existing_ex.rest_seconds if existing_ex else 90,
                min=0,
                max=3600,
                suffix="seconds",
            ).classes("flex-1")
            ui.label(" rest").classes("text-sm text-gray-500")

        def save() -> None:
            name = (name_sel.value or "").strip()
            variant_name = (variant_sel.value or "").strip() or None

            if not name:
                ui.notify("Exercise name is required", color="negative")
                return
            if reps_in.value != 0 and duration_in.value != 0:
                ui.notify("Fill Reps OR Duration — not both", color="negative")
                return

            lbl, variants = lib_map.get(name, ("", []))
            chosen_variant = (
                next((v for v in variants if v.name == variant_name), None)
                if variant_name
                else None
            )

            ex = SessionExercise(
                name=name,
                label=lbl,
                variant_name=chosen_variant.name if chosen_variant else "",
                variant_label=chosen_variant.label if chosen_variant else "",
                sets=int(sets_in.value or 3),
                reps=int(reps_in.value or 10),
                duration=int(duration_in.value or 0),
                rest_before=int(rest_before_in.value or 0),
                rest_seconds=int(rest_in.value or 90),
            )

            if edit_index is not None:
                ex_list[edit_index] = ex
            else:
                ex_list.append(ex)

            action = "updated" if edit_index is not None else "added"
            ui.notify(f"'{ex.display_name}' {action}", color="positive")
            form_card_el.delete()
            refresh()

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
