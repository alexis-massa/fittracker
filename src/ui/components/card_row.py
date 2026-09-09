# src/ui/components/card_row.py
from nicegui import ui


def card_row() -> ui.card:
    return ui.card().classes("w-full q-pa-md q-mb-sm").props("flat bordered")
