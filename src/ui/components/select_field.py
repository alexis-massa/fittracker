# src/ui/components/select_field.py
from typing import Any

from nicegui import ui


def select_field(
    label: str,
    options: list[Any] | dict[Any, str],
    value: Any = None,
    **kwargs: Any,
) -> ui.select:
    return (
        ui.select(label=label, options=options, value=value, **kwargs)
        .classes("nicegui-select")
        .style("width:100%")
    )
