# src/ui/components/date_field.py
from typing import Any

from nicegui import ui

from src.utils.formatting import today_iso


def date_field(label: str, value: str | None = None, **kwargs: Any) -> ui.input:

    with (
        ui.input("Date", value=value if value else today_iso()) as date,
        ui.menu().props("no-parent-event") as menu,
        ui.date().bind_value(date),
        ui.row().classes("justify-end"),
    ):
        ui.button("Close", on_click=menu.close).props("flat")
        with date.add_slot("append"):
            ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
    return date