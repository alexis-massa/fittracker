from datetime import date

from src.utils.formatting import format_duration
from src.utils.formatting import pluralize
from src.utils.formatting import scale_label
from src.utils.formatting import today_iso


def test_today_iso_matches_current_date() -> None:
    assert today_iso() == date.today().isoformat()


def test_scale_label_returns_mapped_value() -> None:
    scale = {1: "Low", 2: "Medium", 3: "High"}
    assert scale_label(2, scale) == "Medium"


def test_scale_label_returns_default_fallback_for_missing_value() -> None:
    assert scale_label(99, {1: "Low"}) == "—"


def test_scale_label_returns_custom_fallback_for_missing_value() -> None:
    assert scale_label(99, {1: "Low"}, fallback="n/a") == "n/a"


def test_pluralize_singular_count() -> None:
    assert pluralize(1, "rep") == "1 rep"


def test_pluralize_plural_count_defaults_to_appending_s() -> None:
    assert pluralize(3, "rep") == "3 reps"


def test_pluralize_zero_count_uses_plural_form() -> None:
    assert pluralize(0, "rep") == "0 reps"


def test_pluralize_uses_explicit_plural_form() -> None:
    assert pluralize(2, "set", "sets") == "2 sets"
    assert pluralize(4, "class", "classes") == "4 classes"


def test_format_duration_under_a_minute() -> None:
    assert format_duration(45) == "45 s"


def test_format_duration_zero_seconds() -> None:
    assert format_duration(0) == "0 s"


def test_format_duration_exact_minute() -> None:
    assert format_duration(60) == "1 min"


def test_format_duration_minutes_and_seconds() -> None:
    assert format_duration(90) == "1 min 30 s"
