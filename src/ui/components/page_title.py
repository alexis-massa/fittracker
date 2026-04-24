# src/ui/components/page_title.py
from nicegui import ui


def page_title(text: str) -> ui.label:
    return ui.label(text).style(
        "font-family:'Syne',sans-serif;"
        "font-weight:700;"
        "font-size:1.55rem;"
        "color:#e8e4dc;"
        "margin-bottom:1.25rem;"
    )
