from psycopg_pool import ConnectionPool

from src.config import DATABASE_URL
from src.utils import pg
from src.utils.pg import PgTable
from src.utils.pg import UsersTable

_USERS_TABLE = "users"
_OWNED_TABLES = ("exercises", "sessions")


class DatabaseManager:
    def __init__(self) -> None:
        self._pool: ConnectionPool | None = None

    def connect(self) -> None:
        self._pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=5, open=True)
        pg.ensure_users_table(self._pool, _USERS_TABLE)
        for table in _OWNED_TABLES:
            pg.ensure_table(self._pool, table, owner_table=_USERS_TABLE)
        print("Connected to Postgres")
        if unowned := self.count_unowned():
            print(
                f"{unowned} existing rows have no owner and are hidden from every user - "
                "assign them with: scripts/manage_users.py claim-legacy USERNAME"
            )

    def disconnect(self) -> None:
        if self._pool is not None:
            self._pool.close()
            self._pool = None
            print("Postgres connection closed")

    def _connected_pool(self) -> ConnectionPool:
        if self._pool is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._pool

    def users(self) -> UsersTable:
        return UsersTable(self._connected_pool(), _USERS_TABLE)

    def exercises(self, user_id: int) -> PgTable:
        return PgTable(self._connected_pool(), "exercises", user_id)

    def sessions(self, user_id: int) -> PgTable:
        return PgTable(self._connected_pool(), "sessions", user_id)

    def count_unowned(self) -> int:
        pool = self._connected_pool()
        return sum(pg.count_unowned(pool, table) for table in _OWNED_TABLES)

    def claim_unowned(self, user_id: int) -> int:
        pool = self._connected_pool()
        return sum(pg.claim_unowned(pool, table, user_id) for table in _OWNED_TABLES)


db_manager = DatabaseManager()
