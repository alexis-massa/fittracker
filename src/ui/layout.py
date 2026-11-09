# src/ui/layout.py
from nicegui import ui

from src import auth
from src.ui.components.account_menu import account_menu
from src.ui.components.theme_toggle import theme_toggle
from src.ui.styles import STYLES

_NAV_TABS: list[tuple[str, str, str]] = [
    ("Sessions", "sessions", "/"),
    ("Exercises", "exercises", "/exercises"),
]

_PWA_HEAD = """
<link rel="manifest" href="/static/manifest.webmanifest" crossorigin="use-credentials">
<link rel="apple-touch-icon" href="/static/icons/apple-touch-icon.png">
<meta name="theme-color" content="#5898d4">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="FitTracker">
<script>
if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js");
}
</script>
"""


def render_head() -> None:
    ui.add_head_html(f"<style>{STYLES}</style>")
    ui.add_head_html(_PWA_HEAD)


def render_header(active_tab: str) -> None:
    user = auth.current_user()
    dark = ui.dark_mode(value=user.preferences.dark_mode)

    render_head()

    with ui.row().classes("app-header w-full"):
        ui.label("FitTracker").classes("app-title text-primary")
        for label, tab, path in _NAV_TABS:
            classes = "nav-btn" + (" active" if tab == active_tab else "")
            ui.link(label, target=path).classes(classes)
        with ui.row().classes("q-ml-auto items-center"):
            ui.label(user.username).classes("text-caption opacity-70 gt-xs")
            theme_toggle(dark, user)
            account_menu(user)
