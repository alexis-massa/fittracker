# main.py
from nicegui import app
from nicegui import ui

from src.config import APP_PORT
from src.db import db_manager
import src.preferences as preferences
from src.ui.layout import render_header
from src.ui.pages.exercise_form import render as exercise_form_page
from src.ui.pages.exercises import render as exercises_page
from src.ui.pages.session_detail import render as session_detail_page
from src.ui.pages.session_form import render as session_form_page
from src.ui.pages.sessions import render as sessions_page


@app.on_startup
async def startup() -> None:
    db_manager.connect()


@app.on_shutdown
async def shutdown() -> None:
    db_manager.disconnect()


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


@ui.page("/exercises")
def exercises() -> None:
    render_header("exercises")
    exercises_page()


@ui.page("/exercises/{exercise_id}/edit")
def edit_exercise(exercise_id: str) -> None:
    render_header("exercises")
    exercise_form_page(exercise_id)


if __name__ in {"__main__", "__mp_main__"}:
    prefs = preferences.load()
    ui.run(title="FitTracker", port=APP_PORT, dark=prefs.dark_mode)
