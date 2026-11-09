# src/ui/components/theme_toggle.py
from nicegui import ui

from src.models import user as user_model
from src.models.user import User


def theme_toggle(dark: ui.dark_mode, user: User) -> None:
    def toggle() -> None:
        if dark.value:
            dark.disable()
            btn.props("icon=light_mode")
            user_model.update_preferences(user.id, {"dark_mode": False})
        else:
            dark.enable()
            btn.props("icon=dark_mode")
            user_model.update_preferences(user.id, {"dark_mode": True})

    initial_icon = "dark_mode" if user.preferences.dark_mode else "light_mode"
    btn = ui.button(icon=initial_icon, on_click=toggle).props("outline round")
