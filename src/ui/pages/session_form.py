# src/ui/pages/session_form.py
from collections.abc import Callable

from nicegui import ui

from src.models import session as session_model
from src.models.exercise import ExerciseDefinition
from src.models.exercise import ExerciseVariant
from src.models.exercise import SessionExercise
from src.models.exercise import get_all as get_library
from src.models.session import Session
from src.ui.components import action_row
from src.ui.components import btn_danger
from src.ui.components import btn_ghost
from src.ui.components import btn_primary
from src.ui.components import exercise_pictogram
from src.ui.components import form_card
from src.ui.components import number_field
from src.ui.components import page_title
from src.ui.components import section_title
from src.ui.components import select_field
from src.ui.components.session_info_fields import SessionInfoInputs
from src.ui.components.session_info_fields import apply_session_info
from src.ui.components.session_info_fields import session_info_fields
from src.ui.pages.exercise_create_form import exercise_create_form
from src.ui.validation import clear_error
from src.ui.validation import flag_error
from src.utils.formatting import pluralize


def render(session_id: str | None, duplicate_from: str | None = None) -> None:
    existing = session_model.get_by_id(session_id) if session_id else None
    source = existing or (session_model.get_by_id(duplicate_from) if duplicate_from else None)

    warmup_exs: list[SessionExercise] = list(source.warmup if source else [])
    workout_exs: list[SessionExercise] = list(source.workout if source else [])
    stretch_exs: list[SessionExercise] = list(source.stretches if source else [])

    is_duplicate = existing is None and source is not None

    with ui.column().classes("page-content"):
        page_title(
            "Duplicate Session" if is_duplicate else ("Edit Session" if existing else "New Session")
        )

        # Only shown when editing something that already exists - a fresh
        # plan (new or duplicated) has nothing to reflect on yet. See
        # session_run.py, where that reflection normally happens instead.
        info: SessionInfoInputs | None = None
        if existing is not None:
            section_title("Session info")
            with form_card(), ui.row().classes("w-full items-center gap-4 flex-wrap"):
                info = session_info_fields(existing)

        _exercise_group("Warmup", warmup_exs)
        _exercise_group("Workout", workout_exs)
        _exercise_group("Stretches", stretch_exs)

        with action_row():
            btn_primary(
                "Save Session",
                on_click=lambda: _save(
                    session_id, existing, info, warmup_exs, workout_exs, stretch_exs
                ),
            )
            btn_ghost("Cancel", on_click=lambda: ui.navigate.to("/"))


# ---------------------------------------------------------------------------
# Exercise group
# ---------------------------------------------------------------------------


def _exercise_group(title: str, ex_list: list[SessionExercise]) -> None:
    heading = section_title(f"{title} — {pluralize(len(ex_list), 'exercise')}")
    container = ui.column().classes("w-full")

    def refresh() -> None:
        heading.set_text(f"{title} — {pluralize(len(ex_list), 'exercise')}")
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
        exercise_pictogram(ex.name)
        with ui.column().classes("flex-1").style("gap:1px"):
            with ui.row().classes("items-center gap-2"):
                ui.label(ex.short_name).classes("text-subtitle1 text-weight-bold")
                if ex.label or ex.variant_label:
                    desc = " / ".join(filter(None, [ex.label, ex.variant_label]))
                    ui.label(desc).classes("text-caption opacity-70")
            ui.label(f"{ex.sets} sets · {ex.reps} reps · {ex.rest_seconds}s rest").classes(
                "text-caption opacity-70"
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
        ui.label("Edit Exercise" if existing_ex else "Add Exercise").classes(
            "text-subtitle1 text-weight-bold q-mb-sm"
        )

        create_slot = ui.column().classes("w-full")

        with ui.row().classes("w-full items-center gap-2 flex-wrap"):
            name_sel = select_field(
                "Exercise",
                options=name_opts(),
                value=existing_ex.name if existing_ex else None,
                clearable=True,
                with_input=True,
            ).classes("flex-1")

            variant_sel = select_field(
                "Variant",
                options=variant_opts(existing_ex.name) if existing_ex else {},
                value=existing_ex.variant_name
                if existing_ex and existing_ex.variant_name
                else None,
                clearable=True,
            ).classes("flex-1")

        def on_name_change(value: str | None) -> None:
            clear_error(name_sel)
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
            "text-caption text-primary"
        ).style("cursor:pointer;text-decoration:none")

        ui.element("div").classes("q-mb-sm")

        effort_row_classes = (
            "w-full items-start sm:items-center gap-2 flex-col sm:flex-row sm:flex-wrap"
        )

        section_title("Sets & timing")
        with ui.row().classes(effort_row_classes):
            rest_before_in = number_field(
                "Rest before this exercise (s)",
                value=existing_ex.rest_before if existing_ex else 0,
                min=0,
                max=3600,
                suffix="seconds",
            ).classes("w-full sm:flex-1")
            sets_in = number_field(
                "Sets", value=existing_ex.sets if existing_ex else 3, min=1, max=100, suffix="sets"
            ).classes("w-full sm:flex-1")
            rest_in = number_field(
                "Rest between sets (s)",
                value=existing_ex.rest_seconds if existing_ex else 90,
                min=0,
                max=3600,
                suffix="seconds",
            ).classes("w-full sm:flex-1")

        section_title("Reps or duration — fill exactly one")
        with ui.row().classes(effort_row_classes):
            reps_in = number_field(
                "Reps",
                value=existing_ex.reps if existing_ex else 10,
                min=0,
                max=200,
                suffix="reps",
            ).classes("w-full sm:flex-1")
            duration_in = number_field(
                "Duration (s)",
                value=existing_ex.duration if existing_ex else 0,
                min=0,
                max=999,
                suffix="seconds",
            ).classes("w-full sm:flex-1")

        def prefill_effort(name: str, variant: str) -> None:
            # Only for a fresh row - editing an existing one keeps its own values.
            if existing_ex is not None or not name:
                return
            last = session_model.get_last_used(name, variant)
            if not last:
                return
            rest_before_in.value = last.rest_before
            sets_in.value = last.sets
            rest_in.value = last.rest_seconds
            reps_in.value = last.reps
            duration_in.value = last.duration

        name_sel.on_value_change(lambda e: prefill_effort(e.value or "", ""))
        variant_sel.on_value_change(lambda e: prefill_effort(name_sel.value or "", e.value or ""))

        def clear_effort_errors() -> None:
            clear_error(reps_in)
            clear_error(duration_in)

        reps_in.on_value_change(clear_effort_errors)
        duration_in.on_value_change(clear_effort_errors)

        def save() -> None:
            clear_error(name_sel)
            name = (name_sel.value or "").strip()
            variant_name = (variant_sel.value or "").strip() or None

            if not name:
                flag_error(name_sel, "Exercise name is required")
                ui.notify("Exercise name is required", color="negative")
                return
            if reps_in.value != 0 and duration_in.value != 0:
                flag_error(reps_in, "Choose reps or duration, not both")
                flag_error(duration_in, "Choose reps or duration, not both")
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
                sets=int(sets_in.value) if sets_in.value is not None else 3,
                reps=int(reps_in.value) if reps_in.value is not None else 10,
                duration=int(duration_in.value) if duration_in.value is not None else 0,
                rest_before=int(rest_before_in.value) if rest_before_in.value is not None else 0,
                rest_seconds=int(rest_in.value) if rest_in.value is not None else 90,
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
    existing: Session | None,
    info: SessionInfoInputs | None,
    warmup_exs: list[SessionExercise],
    workout_exs: list[SessionExercise],
    stretch_exs: list[SessionExercise],
) -> None:
    s = existing or Session()
    if info is not None and not apply_session_info(s, info):
        return

    s.warmup = list(warmup_exs)
    s.workout = list(workout_exs)
    s.stretches = list(stretch_exs)

    if session_id:
        session_model.update(session_id, s)
        ui.notify("Session updated", color="positive")
        ui.navigate.to(f"/sessions/{session_id}")
    else:
        new_id = session_model.create(s)
        ui.notify("Plan saved", color="positive")
        ui.navigate.to(f"/sessions/{new_id}")
