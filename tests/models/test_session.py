from datetime import date

from src.models import session
from src.models.exercise import SessionExercise
from src.models.session import EnergyLevel
from src.models.session import ProgressEnum
from src.models.session import Session
from src.utils import pg
from src.utils.pg import PgTable


def test_session_date_defaults_to_today() -> None:
    assert Session().date == date.today().isoformat()


def test_session_progress_defaults_to_maintain() -> None:
    assert Session().progress == ProgressEnum.MAINTAIN


def test_session_id_property_reflects_underlying_field() -> None:
    assert Session.from_doc({"_id": "abc123"}).id == "abc123"


def test_session_from_doc_defaults_missing_fields() -> None:
    parsed = Session.from_doc({})
    assert parsed.weight is None
    assert parsed.notes is None
    assert parsed.energy_level is None
    assert parsed.progress == ProgressEnum.MAINTAIN
    assert parsed.warmup == []
    assert parsed.workout == []
    assert parsed.stretches == []


def test_session_from_doc_parses_energy_level() -> None:
    assert Session.from_doc({"energy_level": 3}).energy_level == EnergyLevel.MEDIUM


def test_session_from_doc_parses_nested_exercise_lists() -> None:
    parsed = Session.from_doc({"workout": [{"name": "A", "sets": 4}]})
    assert parsed.workout == [SessionExercise(name="A", sets=4)]


def test_session_to_doc_serializes_energy_level_value() -> None:
    doc = Session(energy_level=EnergyLevel.HIGH).to_doc()
    assert doc["energy_level"] == 5


def test_session_to_doc_serializes_none_energy_level() -> None:
    assert Session().to_doc()["energy_level"] is None


def test_session_to_doc_omits_id() -> None:
    assert "_id" not in Session.from_doc({"_id": "abc123"}).to_doc()


def test_session_round_trips_through_doc() -> None:
    original = Session(
        date="2026-01-01",
        weight=70.5,
        notes="felt good",
        energy_level=EnergyLevel.MEDIUM_HIGH,
        progress=ProgressEnum.PROGRESS,
        warmup=[SessionExercise(name="W1")],
        workout=[SessionExercise(name="A", sets=4, reps=8)],
        stretches=[SessionExercise(name="S1")],
    )
    rebuilt = Session.from_doc(original.to_doc())
    assert rebuilt.date == original.date
    assert rebuilt.weight == original.weight
    assert rebuilt.notes == original.notes
    assert rebuilt.energy_level == original.energy_level
    assert rebuilt.progress == original.progress
    assert rebuilt.warmup == original.warmup
    assert rebuilt.workout == original.workout
    assert rebuilt.stretches == original.stretches


def test_get_all_returns_sessions_sorted_by_date_descending(sessions_table: PgTable) -> None:
    pg.insert_one(sessions_table, {"date": "2026-01-01", "progress": "MAINTAIN"})
    pg.insert_one(sessions_table, {"date": "2026-02-01", "progress": "MAINTAIN"})
    assert [s.date for s in session.get_all()] == ["2026-02-01", "2026-01-01"]


def test_get_by_id_returns_matching_session(sessions_table: PgTable) -> None:
    inserted_id = pg.insert_one(sessions_table, {"date": "2026-01-01", "progress": "MAINTAIN"})
    found = session.get_by_id(inserted_id)
    assert found is not None
    assert found.date == "2026-01-01"


def test_get_by_id_returns_none_when_missing(sessions_table: PgTable) -> None:
    assert session.get_by_id("999999") is None


def test_create_persists_session_and_returns_id(sessions_table: PgTable) -> None:
    new_id = session.create(Session(date="2026-01-01"))
    stored = session.get_by_id(new_id)
    assert stored is not None
    assert stored.date == "2026-01-01"


def test_update_modifies_existing_session(sessions_table: PgTable) -> None:
    new_id = session.create(Session(date="2026-01-01"))
    assert session.update(new_id, Session(date="2026-01-02")) is True
    assert session.get_by_id(new_id).date == "2026-01-02"  # type: ignore[union-attr]


def test_delete_removes_session(sessions_table: PgTable) -> None:
    new_id = session.create(Session(date="2026-01-01"))
    assert session.delete(new_id) is True
    assert session.get_by_id(new_id) is None
