# src/ui/layout.py
from collections.abc import Callable

from nicegui import ui

from src import preferences
from src.ui.components.theme_toggle import theme_toggle
from src.ui.styles import STYLES

_state: dict[str, str | None] = {
    "page": "sessions",
    "param": None,
}

_nav_buttons: dict[str, ui.button] = {}
_main_container: dict[str, ui.column] = {}

_NAV_OWNERSHIP: dict[str, str] = {
    "sessions": "sessions",
    "session_detail": "sessions",
    "session_form": "sessions",
    "exercises": "exercises",
    "exercise_form": "exercises",
}


def navigate(page: str, param: str | None = None) -> None:
    _state["page"] = page
    _state["param"] = param
    _rebuild_main()
    _update_nav()


def _update_nav() -> None:
    page = _state["page"] or ""
    active_tab = _NAV_OWNERSHIP.get(page, "")
    for tab, btn in _nav_buttons.items():
        if tab == active_tab:
            btn.classes(add="active")
        else:
            btn.classes(remove="active")


def _rebuild_main() -> None:
    container = _main_container.get("el")
    if container is None:
        return
    container.clear()

    from src.ui.pages.exercise_form import render as exercise_form_page
    from src.ui.pages.exercises import render as exercises_page
    from src.ui.pages.session_detail import render as session_detail_page
    from src.ui.pages.session_form import render as session_form_page
    from src.ui.pages.sessions import render as sessions_page

    page = _state["page"] or "sessions"
    param = _state["param"]

    dispatch: dict[str, Callable[[], None]] = {
        "sessions": lambda: sessions_page(navigate),
        "session_detail": lambda: session_detail_page(param, navigate),
        "session_form": lambda: session_form_page(param, navigate),
        "exercises": lambda: exercises_page(navigate),
        "exercise_form": lambda: exercise_form_page(param, navigate),
    }

    renderer = dispatch.get(page)
    with container:
        if renderer:
            renderer()
        else:
            ui.label(f"Unknown page: {page}").style("color:#555")


def build_layout() -> None:
    prefs = preferences.load()
    dark = ui.dark_mode(value=prefs.dark_mode)

    ui.add_head_html(f"<style>{STYLES}</style>")

    with ui.row().classes("app-header w-full"):
        ui.label("FitTracker").classes("app-title")
        for label, page in [("Sessions", "sessions"), ("Exercises", "exercises")]:
            btn = ui.button(label, on_click=lambda p=page: navigate(str(p))).props("outline")
            _nav_buttons[page] = btn
        with ui.row().classes("ml-auto"):
            theme_toggle(dark)

    _main_container["el"] = ui.column().classes("w-full").style("min-height:calc(100vh - 56px)")
    navigate("sessions")
