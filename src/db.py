from psycopg_pool import ConnectionPool

from src.config import DATABASE_URL
from src.utils.pg import PgTable
from src.utils.pg import ensure_table

_TABLES = ("exercises", "sessions")


class DatabaseManager:
    def __init__(self) -> None:
        self._pool: ConnectionPool | None = None

    def connect(self) -> None:
        self._pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=5, open=True)
        for table in _TABLES:
            ensure_table(self._pool, table)
        print("Connected to Postgres")

    def disconnect(self) -> None:
        if self._pool is not None:
            self._pool.close()
            self._pool = None
            print("Postgres connection closed")

    def _table(self, name: str) -> PgTable:
        if self._pool is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return PgTable(self._pool, name)

    def exercises(self) -> PgTable:
        return self._table("exercises")

    def sessions(self) -> PgTable:
        return self._table("sessions")


db_manager = DatabaseManager()
