# src/ui/components/btn_primary.py
from collections.abc import Callable
from typing import Any

from nicegui import ui


def btn_primary(label: str, on_click: Callable[..., Any]) -> ui.button:
    return ui.button(label, on_click=on_click, color="primary").props("unelevated outline")
