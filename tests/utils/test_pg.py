from src.utils import pg
from src.utils.pg import PgTable


def test_to_id_converts_valid_string() -> None:
    assert pg.to_id("42") == 42


def test_to_id_passes_through_int() -> None:
    assert pg.to_id(7) == 7


def test_to_id_returns_none_for_invalid_string() -> None:
    assert pg.to_id("not-an-id") is None


def test_find_all_sorts_ascending_by_default(pg_table: PgTable) -> None:
    pg.insert_one(pg_table, {"name": "b"})
    pg.insert_one(pg_table, {"name": "a"})
    names = [doc["name"] for doc in pg.find_all(pg_table, sort_field="name")]
    assert names == ["a", "b"]


def test_find_all_sorts_descending_when_requested(pg_table: PgTable) -> None:
    pg.insert_one(pg_table, {"name": "a"})
    pg.insert_one(pg_table, {"name": "b"})
    names = [doc["name"] for doc in pg.find_all(pg_table, sort_field="name", ascending=False)]
    assert names == ["b", "a"]


def test_find_all_includes_string_id(pg_table: PgTable) -> None:
    pg.insert_one(pg_table, {"name": "a"})
    doc = pg.find_all(pg_table)[0]
    assert isinstance(doc["_id"], str)


def test_find_one_returns_matching_document(pg_table: PgTable) -> None:
    new_id = pg.insert_one(pg_table, {"name": "squat"})
    doc = pg.find_one(pg_table, new_id)
    assert doc is not None
    assert doc["name"] == "squat"
    assert doc["_id"] == new_id


def test_find_one_returns_none_when_missing(pg_table: PgTable) -> None:
    assert pg.find_one(pg_table, 999999) is None


def test_find_one_returns_none_for_invalid_id(pg_table: PgTable) -> None:
    assert pg.find_one(pg_table, "not-an-id") is None


def test_insert_one_returns_new_id_and_persists_document(pg_table: PgTable) -> None:
    new_id = pg.insert_one(pg_table, {"name": "squat"})
    assert pg.find_one(pg_table, new_id) is not None


def test_update_one_returns_true_when_document_matched(pg_table: PgTable) -> None:
    new_id = pg.insert_one(pg_table, {"name": "squat"})
    assert pg.update_one(pg_table, new_id, {"name": "lunge"}) is True
    doc = pg.find_one(pg_table, new_id)
    assert doc is not None
    assert doc["name"] == "lunge"


def test_update_one_returns_false_when_document_missing(pg_table: PgTable) -> None:
    assert pg.update_one(pg_table, 999999, {"name": "lunge"}) is False


def test_delete_one_returns_true_and_removes_document(pg_table: PgTable) -> None:
    new_id = pg.insert_one(pg_table, {"name": "squat"})
    assert pg.delete_one(pg_table, new_id) is True
    assert pg.find_one(pg_table, new_id) is None


def test_delete_one_returns_false_when_document_missing(pg_table: PgTable) -> None:
    assert pg.delete_one(pg_table, 999999) is False
