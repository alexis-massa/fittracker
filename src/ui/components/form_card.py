# src/ui/components/form_card.py
from nicegui import ui


def form_card() -> ui.card:
    return ui.card().classes("w-full q-pa-md q-mb-md").props("dense")
