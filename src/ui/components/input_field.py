# src/ui/components/input_field.py
from typing import Any

from nicegui import ui


def input_field(label: str, value: str = "", **kwargs: Any) -> ui.input:
    return ui.input(label, value=value, **kwargs).props("outlined dense")
