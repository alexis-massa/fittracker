# src/ui/components/form_card.py
from nicegui import ui


def form_card() -> ui.card:
    return ui.card().style(
        "background:#141414;"
        "border:1px solid #1e1e1e;"
        "padding:1.5rem;"
        "border-radius:4px;"
        "width:100%;"
        "max-width:520px;"
        "box-shadow:none;"
    )
