# src/ui/components/date_field.py
from typing import Any

from nicegui import ui

from src.utils.formatting import today_iso


def date_field(label: str, value: str | None = None, **kwargs: Any) -> ui.date:
    return (
        ui.date(value=value or today_iso(), **kwargs)
        .props("mask='YYYY-MM-DD'")
        .classes("nicegui-input")
        .style("width:100%")
    )
