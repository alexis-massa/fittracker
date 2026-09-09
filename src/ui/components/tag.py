# src/ui/components/tag.py
from nicegui import ui


def tag(text: str, accent: bool = False) -> ui.chip:
    color = "primary" if accent else "grey"
    return ui.chip(text, color=color).props("dense outline square")
