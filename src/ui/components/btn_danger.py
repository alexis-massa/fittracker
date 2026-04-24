# src/ui/components/btn_danger.py
from collections.abc import Callable
from typing import Any

from nicegui import ui


def btn_danger(label: str, on_click: Callable[..., Any]) -> ui.button:
    return ui.button(label, on_click=on_click).classes("btn-danger")
