# src/ui/layout.py
from nicegui import ui

from src import preferences
from src.ui.components.theme_toggle import theme_toggle
from src.ui.styles import STYLES

_NAV_TABS: list[tuple[str, str, str]] = [
    ("Sessions", "sessions", "/"),
    ("Exercises", "exercises", "/exercises"),
]


def render_header(active_tab: str) -> None:
    prefs = preferences.load()
    dark = ui.dark_mode(value=prefs.dark_mode)

    ui.add_head_html(f"<style>{STYLES}</style>")

    with ui.row().classes("app-header w-full"):
        ui.label("FitTracker").classes("app-title text-primary")
        for label, tab, path in _NAV_TABS:
            classes = "nav-btn" + (" active" if tab == active_tab else "")
            ui.link(label, target=path).classes(classes)
        with ui.row().classes("q-ml-auto"):
            theme_toggle(dark)
