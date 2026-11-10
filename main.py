# main.py
from nicegui import app
from nicegui import ui
from starlette.responses import RedirectResponse

from src.auth import AuthMiddleware
from src.config import APP_ENV
from src.config import APP_PORT
from src.config import STORAGE_SECRET
from src.db import db_manager
from src.ui.layout import render_header
from src.ui.pages.exercise_form import render as exercise_form_page
from src.ui.pages.exercises import render as exercises_page
from src.ui.pages.login import render as login_page
from src.ui.pages.session_detail import render as session_detail_page
from src.ui.pages.session_form import render as session_form_page
from src.ui.pages.session_run import render as session_run_page
from src.ui.pages.sessions import render as sessions_page

app.add_static_files("/static", "static")
# Served at the root (not under /static) so its default scope covers the
# whole app - a worker scoped to /static/ can't control the "/" start_url,
# which Chrome's install-prompt eligibility check requires.
app.add_static_file(local_file="static/sw.js", url_path="/sw.js")
# Added before ui.run so it sits inside NiceGUI's session middleware.
app.add_middleware(AuthMiddleware)


@app.on_startup
async def startup() -> None:
    db_manager.connect()


@app.on_shutdown
async def shutdown() -> None:
    db_manager.disconnect()


@ui.page("/login")
def login(redirect_to: str = "/") -> RedirectResponse | None:
    return login_page(redirect_to)


@ui.page("/")
def index() -> None:
    render_header("sessions")
    sessions_page()


@ui.page("/sessions/new")
def new_session() -> None:
    render_header("sessions")
    session_form_page(None)


@ui.page("/sessions/{session_id}")
def session_detail(session_id: str) -> None:
    render_header("sessions")
    session_detail_page(session_id)


@ui.page("/sessions/{session_id}/edit")
def edit_session(session_id: str) -> None:
    render_header("sessions")
    session_form_page(session_id)


@ui.page("/sessions/{session_id}/duplicate")
def duplicate_session(session_id: str) -> None:
    render_header("sessions")
    session_form_page(None, duplicate_from=session_id)


# A locked phone drops the websocket; waiting longer before discarding the page keeps
# the workout on screen instead of reloading it from the start.
@ui.page("/sessions/{session_id}/run", reconnect_timeout=3600)
def run_session(session_id: str) -> None:
    render_header("sessions")
    session_run_page(session_id)


@ui.page("/exercises")
def exercises() -> None:
    render_header("exercises")
    exercises_page()


@ui.page("/exercises/{exercise_id}/edit")
def edit_exercise(exercise_id: str) -> None:
    render_header("exercises")
    exercise_form_page(exercise_id)


if __name__ in {"__main__", "__mp_main__"}:
    is_prod = APP_ENV == "production"
    if is_prod and not STORAGE_SECRET:
        raise RuntimeError("STORAGE_SECRET must be set in production (it signs session cookies).")
    ui.run(
        title="FitTracker",
        host="0.0.0.0",
        port=APP_PORT,
        dark=None,
        reload=not is_prod,
        show=not is_prod,
        favicon="static/icons/favicon-32.png",
        storage_secret=STORAGE_SECRET or "dev-only-insecure-secret",
        session_middleware_kwargs={"https_only": is_prod, "max_age": 60 * 60 * 24 * 30},
    )
