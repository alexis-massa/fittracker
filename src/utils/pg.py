# src/utils/pg.py
from dataclasses import dataclass
from typing import Any

from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool

# Table/field names below are always internal constants (never user input),
# so building queries with f-strings is safe here.


@dataclass(frozen=True)
class PgTable:
    """A handle on a document table, scoped to one user's rows."""

    pool: ConnectionPool
    name: str
    user_id: int


@dataclass(frozen=True)
class UsersTable:
    pool: ConnectionPool
    name: str


def ensure_users_table(pool: ConnectionPool, name: str) -> None:
    with pool.connection() as conn:
        conn.execute(
            f"CREATE TABLE IF NOT EXISTS {name} ("
            "id SERIAL PRIMARY KEY, "
            "username TEXT NOT NULL, "
            "password_hash TEXT NOT NULL, "
            "preferences JSONB NOT NULL DEFAULT '{}', "
            "created_at TIMESTAMPTZ NOT NULL DEFAULT now())"
        )
        conn.execute(
            f"CREATE UNIQUE INDEX IF NOT EXISTS {name}_username_key ON {name} (lower(username))"
        )


def ensure_table(pool: ConnectionPool, name: str, owner_table: str | None = None) -> None:
    """Create a document table and make sure it has an owner column.

    Adding the column to an existing table leaves its rows unowned (NULL):
    they match no user's queries until claimed with `claim_unowned`.
    """
    owner_ref = f" REFERENCES {owner_table}(id) ON DELETE CASCADE" if owner_table else ""
    with pool.connection() as conn:
        conn.execute(
            f"CREATE TABLE IF NOT EXISTS {name} (id SERIAL PRIMARY KEY, doc JSONB NOT NULL)"
        )
        conn.execute(f"ALTER TABLE {name} ADD COLUMN IF NOT EXISTS user_id INTEGER{owner_ref}")
        conn.execute(f"CREATE INDEX IF NOT EXISTS {name}_user_id_idx ON {name} (user_id)")


def count_unowned(pool: ConnectionPool, name: str) -> int:
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(f"SELECT count(*) FROM {name} WHERE user_id IS NULL")
        row = cur.fetchone()
        assert row is not None
        return int(row[0])


def claim_unowned(pool: ConnectionPool, name: str, user_id: int) -> int:
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(f"UPDATE {name} SET user_id = %s WHERE user_id IS NULL", (user_id,))
        return cur.rowcount


def find_all(
    table: PgTable, sort_field: str = "_id", ascending: bool = True
) -> list[dict[str, Any]]:
    direction = "ASC" if ascending else "DESC"
    order_expr = "id" if sort_field == "_id" else f"doc ->> '{sort_field}'"
    with table.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"SELECT id, doc FROM {table.name} WHERE user_id = %s "
            f"ORDER BY {order_expr} {direction}",
            (table.user_id,),
        )
        return [_with_id(row_id, doc) for row_id, doc in cur.fetchall()]


def find_one(table: PgTable, doc_id: Any) -> dict[str, Any] | None:
    row_id = to_id(doc_id)
    if row_id is None:
        return None
    with table.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"SELECT id, doc FROM {table.name} WHERE id = %s AND user_id = %s",
            (row_id, table.user_id),
        )
        row = cur.fetchone()
        return _with_id(*row) if row else None


def insert_one(table: PgTable, data: dict[str, Any]) -> str:
    with table.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO {table.name} (doc, user_id) VALUES (%s, %s) RETURNING id",
            (Jsonb(data), table.user_id),
        )
        new_id = cur.fetchone()
        assert new_id is not None
    return str(new_id[0])


def update_one(table: PgTable, doc_id: Any, data: dict[str, Any]) -> bool:
    row_id = to_id(doc_id)
    if row_id is None:
        return False
    with table.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"UPDATE {table.name} SET doc = %s WHERE id = %s AND user_id = %s",
            (Jsonb(data), row_id, table.user_id),
        )
        return cur.rowcount > 0


def delete_one(table: PgTable, doc_id: Any) -> bool:
    row_id = to_id(doc_id)
    if row_id is None:
        return False
    with table.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"DELETE FROM {table.name} WHERE id = %s AND user_id = %s", (row_id, table.user_id)
        )
        return cur.rowcount > 0


def to_id(value: Any) -> int | None:
    """Coerce a str or int to a row id, or None if it isn't one."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _with_id(row_id: int, doc: dict[str, Any]) -> dict[str, Any]:
    return {**doc, "_id": str(row_id)}
