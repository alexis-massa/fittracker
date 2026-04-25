# src/ui/components/action_row.py
from nicegui import ui


def action_row() -> ui.row:
    return ui.row().classes("action-row")
