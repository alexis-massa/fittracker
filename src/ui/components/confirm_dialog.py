# src/ui/components/confirm_dialog.py
from collections.abc import Callable

from nicegui import ui


def confirm_dialog(message: str, on_confirm: Callable[[], None]) -> None:
    with ui.dialog() as dialog, ui.card():
        ui.label(message).classes("meta-row")
        with ui.row().classes("justify-end w-full gap-2 q-mt-md"):
            ui.button("Cancel", on_click=dialog.close).props("flat")

            def confirm() -> None:
                dialog.close()
                on_confirm()

            ui.button("Delete", on_click=confirm, color="red").props("flat")
    dialog.open()
