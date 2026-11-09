from psycopg_pool import ConnectionPool

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


def _as_user(table: PgTable, user_id: int) -> PgTable:
    return PgTable(table.pool, table.name, user_id)


def test_find_all_only_returns_the_users_own_rows(pg_table: PgTable) -> None:
    pg.insert_one(pg_table, {"name": "mine"})
    pg.insert_one(_as_user(pg_table, 2), {"name": "theirs"})
    assert [d["name"] for d in pg.find_all(pg_table)] == ["mine"]


def test_find_one_ignores_rows_owned_by_someone_else(pg_table: PgTable) -> None:
    theirs = pg.insert_one(_as_user(pg_table, 2), {"name": "theirs"})
    assert pg.find_one(pg_table, theirs) is None


def test_update_one_cannot_touch_rows_owned_by_someone_else(pg_table: PgTable) -> None:
    other = _as_user(pg_table, 2)
    theirs = pg.insert_one(other, {"name": "theirs"})
    assert pg.update_one(pg_table, theirs, {"name": "hijacked"}) is False
    assert pg.find_one(other, theirs) == {"name": "theirs", "_id": theirs}


def test_delete_one_cannot_touch_rows_owned_by_someone_else(pg_table: PgTable) -> None:
    other = _as_user(pg_table, 2)
    theirs = pg.insert_one(other, {"name": "theirs"})
    assert pg.delete_one(pg_table, theirs) is False
    assert pg.find_one(other, theirs) is not None


def test_ensure_table_adds_owner_column_leaving_existing_rows_unowned(
    pg_pool: ConnectionPool, table_name: str
) -> None:
    legacy = f"{table_name}_legacy"
    with pg_pool.connection() as conn:
        conn.execute(f"CREATE TABLE {legacy} (id SERIAL PRIMARY KEY, doc JSONB NOT NULL)")
        conn.execute(f'INSERT INTO {legacy} (doc) VALUES (\'{{"name": "old"}}\')')
    try:
        pg.ensure_table(pg_pool, legacy)
        assert pg.count_unowned(pg_pool, legacy) == 1
        assert pg.find_all(PgTable(pg_pool, legacy, 1)) == []
    finally:
        with pg_pool.connection() as conn:
            conn.execute(f"DROP TABLE {legacy}")


def test_claim_unowned_assigns_orphans_to_a_user(pg_pool: ConnectionPool, table_name: str) -> None:
    with pg_pool.connection() as conn:
        conn.execute(f'INSERT INTO {table_name} (doc) VALUES (\'{{"name": "old"}}\')')
    assert pg.claim_unowned(pg_pool, table_name, 7) == 1
    assert pg.count_unowned(pg_pool, table_name) == 0
    assert [d["name"] for d in pg.find_all(PgTable(pg_pool, table_name, 7))] == ["old"]
