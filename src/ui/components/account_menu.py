# src/ui/components/account_menu.py
from collections.abc import Callable

from nicegui import ui

from src import auth
from src.models import user as user_model
from src.models.user import User
from src.ui.components.input_field import input_field


def account_menu(user: User) -> None:
    open_password_dialog = _password_dialog(user)

    def sign_out() -> None:
        auth.logout()
        ui.navigate.to("/login")

    with (
        ui.button(icon="account_circle").props("outline round").tooltip(user.username),
        ui.menu(),
    ):
        ui.menu_item(user.username).props("disable")
        ui.separator()
        ui.menu_item("Change password", on_click=open_password_dialog)
        ui.menu_item("Sign out", on_click=sign_out)


def _password_dialog(user: User) -> Callable[[], None]:
    with ui.dialog() as dialog, ui.card().classes("w-80"):
        ui.label("Change password").classes("text-h6")
        current = _password_input("Current password", "current-password")
        new = _password_input("New password", "new-password")
        repeat = _password_input("Repeat new password", "new-password")
        error = ui.label().classes("text-negative text-caption")

        def save() -> None:
            key = user.username.lower()
            if new.value != repeat.value:
                error.set_text("New passwords do not match.")
                return
            if auth.login_throttle.is_blocked(key):
                error.set_text("Too many failed attempts. Try again in a few minutes.")
                return
            if user_model.authenticate(user.username, current.value) is None:
                auth.login_throttle.record_failure(key)
                error.set_text("Current password is incorrect.")
                return
            try:
                user_model.set_password(user.id, new.value)
            except ValueError as exc:
                error.set_text(str(exc))
                return
            auth.login_throttle.reset(key)
            dialog.close()
            ui.notify("Password changed", color="positive")

        with ui.row().classes("justify-end w-full gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Save", on_click=save).props("flat")

    def open_fresh() -> None:
        for field in (current, new, repeat):
            field.value = ""
        error.set_text("")
        dialog.open()

    return open_fresh


def _password_input(label: str, autocomplete: str) -> ui.input:
    return (
        input_field(label, password=True, password_toggle_button=True)
        .props(f"autocomplete={autocomplete}")
        .classes("w-full")
    )
