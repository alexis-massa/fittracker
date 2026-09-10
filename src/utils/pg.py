# src/utils/pg.py
from dataclasses import dataclass
from typing import Any

from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool

# Table/field names below are always internal constants (never user input),
# so building queries with f-strings is safe here.


@dataclass
class PgTable:
    pool: ConnectionPool
    name: str


def ensure_table(pool: ConnectionPool, name: str) -> None:
    with pool.connection() as conn:
        conn.execute(
            f"CREATE TABLE IF NOT EXISTS {name} (id SERIAL PRIMARY KEY, doc JSONB NOT NULL)"
        )


def find_all(
    table: PgTable, sort_field: str = "_id", ascending: bool = True
) -> list[dict[str, Any]]:
    direction = "ASC" if ascending else "DESC"
    order_expr = "id" if sort_field == "_id" else f"doc ->> '{sort_field}'"
    with table.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(f"SELECT id, doc FROM {table.name} ORDER BY {order_expr} {direction}")
        return [_with_id(row_id, doc) for row_id, doc in cur.fetchall()]


def find_one(table: PgTable, doc_id: Any) -> dict[str, Any] | None:
    row_id = to_id(doc_id)
    if row_id is None:
        return None
    with table.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(f"SELECT id, doc FROM {table.name} WHERE id = %s", (row_id,))
        row = cur.fetchone()
        return _with_id(*row) if row else None


def insert_one(table: PgTable, data: dict[str, Any]) -> str:
    with table.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(f"INSERT INTO {table.name} (doc) VALUES (%s) RETURNING id", (Jsonb(data),))
        new_id = cur.fetchone()
        assert new_id is not None
    return str(new_id[0])


def update_one(table: PgTable, doc_id: Any, data: dict[str, Any]) -> bool:
    row_id = to_id(doc_id)
    if row_id is None:
        return False
    with table.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(f"UPDATE {table.name} SET doc = %s WHERE id = %s", (Jsonb(data), row_id))
        return cur.rowcount > 0


def delete_one(table: PgTable, doc_id: Any) -> bool:
    row_id = to_id(doc_id)
    if row_id is None:
        return False
    with table.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(f"DELETE FROM {table.name} WHERE id = %s", (row_id,))
        return cur.rowcount > 0


def to_id(value: Any) -> int | None:
    """Coerce a str or int to a row id, or None if it isn't one."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _with_id(row_id: int, doc: dict[str, Any]) -> dict[str, Any]:
    return {**doc, "_id": str(row_id)}
