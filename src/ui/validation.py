# src/ui/validation.py
from nicegui.elements.mixins.validation_element import ValidationElement


def flag_error(field: ValidationElement, message: str) -> None:
    field.error = message


def clear_error(field: ValidationElement) -> None:
    field.error = None
