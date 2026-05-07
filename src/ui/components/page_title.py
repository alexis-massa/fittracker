# src/ui/components/page_title.py
from nicegui import ui


def page_title(text: str) -> ui.label:
    return ui.label(text).classes("text-h4 text-weight-medium grey-7")
