# src/ui/components/number_field.py
from typing import Any

from nicegui import ui


def number_field(label: str, value: float | None = None, **kwargs: Any) -> ui.number:
    return ui.number(label, value=value, **kwargs).props("outlined dense")
