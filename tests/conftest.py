from collections.abc import Iterator
import os
import uuid

from psycopg_pool import ConnectionPool
import pytest

from src.db import db_manager
from src.utils.pg import PgTable
from src.utils.pg import ensure_table

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://fittracker:fittracker@localhost:5433/fittracker"
)


@pytest.fixture(scope="session")
def pg_pool() -> Iterator[ConnectionPool]:
    pool = ConnectionPool(TEST_DATABASE_URL, min_size=1, max_size=5, open=True)
    yield pool
    pool.close()


@pytest.fixture
def pg_table(pg_pool: ConnectionPool) -> Iterator[PgTable]:
    name = f"test_{uuid.uuid4().hex}"
    ensure_table(pg_pool, name)
    table = PgTable(pg_pool, name)
    yield table
    with pg_pool.connection() as conn:
        conn.execute(f"DROP TABLE IF EXISTS {name}")


@pytest.fixture
def exercises_table(monkeypatch: pytest.MonkeyPatch, pg_table: PgTable) -> Iterator[PgTable]:
    monkeypatch.setattr(db_manager, "exercises", lambda: pg_table)
    yield pg_table


@pytest.fixture
def sessions_table(monkeypatch: pytest.MonkeyPatch, pg_table: PgTable) -> Iterator[PgTable]:
    monkeypatch.setattr(db_manager, "sessions", lambda: pg_table)
    yield pg_table
