# src/ui/components/page_header_row.py
from nicegui import ui


def page_header_row() -> ui.row:
    return ui.row().style(
        "align-items:center;justify-content:space-between;width:100%;margin-bottom:1.5rem;"
    )
