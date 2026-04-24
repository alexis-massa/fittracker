# src/ui/components/tag.py
from nicegui import ui


def tag(text: str, accent: bool = False) -> ui.html:
    css_class = "tag accent" if accent else "tag"
    return ui.html(f'<span class="{css_class}">{text}</span>')
