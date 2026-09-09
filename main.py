# main.py
from nicegui import app
from nicegui import ui

from src.config import APP_PORT
from src.db import db_manager
import src.preferences as preferences
from src.ui.layout import build_layout


@app.on_startup
async def startup() -> None:
    db_manager.connect()


@app.on_shutdown
async def shutdown() -> None:
    db_manager.disconnect()


@ui.page("/")
def index() -> None:
    build_layout()


if __name__ in {"__main__", "__mp_main__"}:
    prefs = preferences.load()
    ui.run(title="FitTracker", port=APP_PORT, dark=prefs.dark_mode)
