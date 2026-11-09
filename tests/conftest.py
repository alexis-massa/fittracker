from collections.abc import Iterator
import os
import uuid

from psycopg_pool import ConnectionPool
import pytest

from src.db import db_manager
from src.utils.pg import PgTable
from src.utils.pg import UsersTable
from src.utils.pg import ensure_table
from src.utils.pg import ensure_users_table

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://fittracker:fittracker@localhost:5433/fittracker"
)
TEST_USER_ID = 1


@pytest.fixture(scope="session")
def pg_pool() -> Iterator[ConnectionPool]:
    pool = ConnectionPool(TEST_DATABASE_URL, min_size=1, max_size=5, open=True)
    yield pool
    pool.close()


def _temp_table(pool: ConnectionPool) -> Iterator[str]:
    name = f"test_{uuid.uuid4().hex}"
    ensure_table(pool, name)
    yield name
    with pool.connection() as conn:
        conn.execute(f"DROP TABLE IF EXISTS {name}")


@pytest.fixture
def table_name(pg_pool: ConnectionPool) -> Iterator[str]:
    yield from _temp_table(pg_pool)


@pytest.fixture
def pg_table(pg_pool: ConnectionPool, table_name: str) -> PgTable:
    return PgTable(pg_pool, table_name, TEST_USER_ID)


@pytest.fixture
def exercises_table(monkeypatch: pytest.MonkeyPatch, pg_pool: ConnectionPool) -> Iterator[PgTable]:
    for name in _temp_table(pg_pool):
        monkeypatch.setattr(
            db_manager, "exercises", lambda user_id, name=name: PgTable(pg_pool, name, user_id)
        )
        yield PgTable(pg_pool, name, TEST_USER_ID)


@pytest.fixture
def sessions_table(monkeypatch: pytest.MonkeyPatch, pg_pool: ConnectionPool) -> Iterator[PgTable]:
    for name in _temp_table(pg_pool):
        monkeypatch.setattr(
            db_manager, "sessions", lambda user_id, name=name: PgTable(pg_pool, name, user_id)
        )
        yield PgTable(pg_pool, name, TEST_USER_ID)


@pytest.fixture
def users_table(monkeypatch: pytest.MonkeyPatch, pg_pool: ConnectionPool) -> Iterator[UsersTable]:
    name = f"test_users_{uuid.uuid4().hex}"
    ensure_users_table(pg_pool, name)
    table = UsersTable(pg_pool, name)
    monkeypatch.setattr(db_manager, "users", lambda: table)
    yield table
    with pg_pool.connection() as conn:
        conn.execute(f"DROP TABLE IF EXISTS {name}")


@pytest.fixture(autouse=True)
def _never_touch_the_real_database(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse() -> None:
        raise RuntimeError("Tests must not connect to the real database; use the table fixtures.")

    monkeypatch.setattr(db_manager, "connect", refuse)
