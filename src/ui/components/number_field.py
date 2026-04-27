# src/ui/components/number_field.py
from typing import Any

from nicegui import ui


def number_field(label: str, value: float = 0.0, **kwargs: Any) -> ui.number:
    return ui.number(label, value=value, **kwargs).classes("nicegui-input").classes("w-full")
