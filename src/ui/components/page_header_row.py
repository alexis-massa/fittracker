# src/ui/components/page_header_row.py
from nicegui import ui


def page_header_row() -> ui.row:
    return ui.row().classes("items-center justify-between w-full q-mb-md")
