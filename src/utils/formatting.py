# src/utils/formatting.py
from datetime import date


def today_iso() -> str:
    return date.today().isoformat()


def scale_label(value: int, scale: dict[int, str], fallback: str = "—") -> str:
    """Return a human label for an integer scale value."""
    return scale.get(value, fallback)


def pluralise(count: int, singular: str, plural: str | None = None) -> str:
    if plural is None:
        plural = singular + "s"
    return f"{count} {singular if count == 1 else plural}"


def format_duration(seconds: int) -> str:
    """e.g. 90 → '1 min 30 s', 60 → '1 min', 45 → '45 s'"""
    if seconds < 60:
        return f"{seconds} s"
    mins, secs = divmod(seconds, 60)
    return f"{mins} min {secs} s" if secs else f"{mins} min"
