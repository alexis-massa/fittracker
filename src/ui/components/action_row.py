# src/ui/components/action_row.py
from nicegui import ui


def action_row() -> ui.row:
    return ui.row().style("gap:0.75rem;margin-top:1.5rem;align-items:center")
