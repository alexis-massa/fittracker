# src/ui/components/textarea_field.py
from typing import Any

from nicegui import ui


def textarea_field(label: str, value: str = "", **kwargs: Any) -> ui.textarea:
    return ui.textarea(label, value=value, **kwargs).classes("nicegui-textarea").classes("w-full")
