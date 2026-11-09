# src/ui/pages/login.py
from nicegui import ui
from starlette.responses import RedirectResponse

from src import auth
from src.models import user as user_model
from src.ui.components import btn_primary
from src.ui.components import form_card
from src.ui.components import input_field
from src.ui.components import page_title
from src.ui.layout import render_head


def render(redirect_to: str) -> RedirectResponse | None:
    if auth.session_user() is not None:
        return RedirectResponse("/")

    render_head()
    target = auth.safe_redirect_target(redirect_to)

    with ui.column().classes("page-content items-center"):
        page_title("FitTracker")
        with form_card().classes("max-w-sm"):
            username = (
                input_field("Username").props("autofocus autocomplete=username").classes("w-full")
            )
            password = (
                input_field("Password", password=True, password_toggle_button=True)
                .props("autocomplete=current-password")
                .classes("w-full")
            )
            error = ui.label().classes("text-negative text-caption")

            def submit() -> None:
                key = username.value.strip().lower()
                if auth.login_throttle.is_blocked(key):
                    error.set_text("Too many failed attempts. Try again in a few minutes.")
                    return
                user = user_model.authenticate(username.value, password.value)
                if user is None:
                    auth.login_throttle.record_failure(key)
                    password.value = ""
                    error.set_text("Invalid username or password.")
                    return
                auth.login_throttle.reset(key)
                auth.login(user)
                ui.navigate.to(target)

            username.on("keydown.enter", submit)
            password.on("keydown.enter", submit)
            btn_primary("Sign in", on_click=submit).classes("w-full")
    return None
