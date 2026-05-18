# src/ui/components/btn_ghost.py
from collections.abc import Callable
from typing import Any

from nicegui import ui


def btn_ghost(label: str, on_click: Callable[..., Any]) -> ui.button:
    return ui.button(label, on_click=on_click, color="secondary").props("outline")
