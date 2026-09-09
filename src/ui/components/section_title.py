# src/ui/components/section_title.py
from nicegui import ui


def section_title(text: str) -> ui.label:
    return ui.label(text).classes(
        "text-caption text-weight-medium text-uppercase letter-spacing-wide q-mt-md q-mb-xs"
    )
