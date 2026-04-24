# src/ui/components/section_title.py
from nicegui import ui


def section_title(text: str) -> ui.label:
    return ui.label(text).classes("section-title")
