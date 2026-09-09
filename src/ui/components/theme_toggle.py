# src/ui/components/theme_toggle.py
from nicegui import ui

from src import preferences


def theme_toggle(dark: ui.dark_mode) -> None:
    def toggle() -> None:
        if dark.value:
            dark.disable()
            btn.props("icon=light_mode")
            preferences.update({"dark_mode": False})
        else:
            dark.enable()
            btn.props("icon=dark_mode")
            preferences.update({"dark_mode": True})

    initial_icon = "dark_mode" if preferences.current.dark_mode else "light_mode"
    btn = ui.button(icon=initial_icon, on_click=toggle).props("outline round")
