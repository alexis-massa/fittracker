# src/models/user.py
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any

from psycopg import errors
from psycopg.types.json import Jsonb

from src.db import db_manager
from src.preferences import Preferences
from src.utils.passwords import hash_password
from src.utils.passwords import verify_password

MIN_PASSWORD_LENGTH = 8
_USERNAME_PATTERN = re.compile(r"[A-Za-z0-9_.-]{3,32}")
_COLUMNS = "id, username, preferences, created_at"
# Verified against when the username is unknown, so a miss costs as much as a hit.
_DUMMY_HASH = hash_password("not-a-real-password")


class UsernameTakenError(Exception):
    pass


@dataclass(frozen=True)
class User:
    id: int
    username: str
    preferences: Preferences
    created_at: datetime

    @classmethod
    def from_row(cls, row: tuple[Any, ...]) -> "User":
        user_id, username, preferences, created_at = row
        return cls(user_id, username, Preferences.from_doc(preferences), created_at)


def validate_username(raw: str) -> str:
    username = raw.strip()
    if not _USERNAME_PATTERN.fullmatch(username):
        raise ValueError("Username must be 3-32 characters: letters, digits, '.', '_' or '-'.")
    return username


def validate_password(password: str) -> None:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")


def create(username: str, password: str) -> User:
    username = validate_username(username)
    validate_password(password)
    table = db_manager.users()
    try:
        with table.pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {table.name} (username, password_hash) VALUES (%s, %s) "
                f"RETURNING {_COLUMNS}",
                (username, hash_password(password)),
            )
            row = cur.fetchone()
    except errors.UniqueViolation:
        raise UsernameTakenError(f"Username '{username}' is already taken.") from None
    assert row is not None
    return User.from_row(row)


def get_by_id(user_id: int) -> User | None:
    table = db_manager.users()
    with table.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(f"SELECT {_COLUMNS} FROM {table.name} WHERE id = %s", (user_id,))
        row = cur.fetchone()
    return User.from_row(row) if row else None


def get_by_username(username: str) -> User | None:
    table = db_manager.users()
    with table.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"SELECT {_COLUMNS} FROM {table.name} WHERE lower(username) = lower(%s)",
            (username.strip(),),
        )
        row = cur.fetchone()
    return User.from_row(row) if row else None


def get_all() -> list[User]:
    table = db_manager.users()
    with table.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(f"SELECT {_COLUMNS} FROM {table.name} ORDER BY id")
        return [User.from_row(row) for row in cur.fetchall()]


def authenticate(username: str, password: str) -> User | None:
    table = db_manager.users()
    with table.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"SELECT {_COLUMNS}, password_hash FROM {table.name} WHERE lower(username) = lower(%s)",
            (username.strip(),),
        )
        row = cur.fetchone()
    if row is None:
        verify_password(password, _DUMMY_HASH)
        return None
    *user_fields, password_hash = row
    return User.from_row(tuple(user_fields)) if verify_password(password, password_hash) else None


def set_password(user_id: int, password: str) -> bool:
    validate_password(password)
    table = db_manager.users()
    with table.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"UPDATE {table.name} SET password_hash = %s WHERE id = %s",
            (hash_password(password), user_id),
        )
        return cur.rowcount > 0


def update_preferences(user_id: int, changes: dict[str, Any]) -> Preferences:
    """Apply a partial update to a user's preferences, like $set."""
    known = {key: value for key, value in changes.items() if key in asdict(Preferences())}
    table = db_manager.users()
    with table.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"UPDATE {table.name} SET preferences = preferences || %s WHERE id = %s "
            "RETURNING preferences",
            (Jsonb(known), user_id),
        )
        row = cur.fetchone()
    return Preferences.from_doc(row[0] if row else {})


def delete(user_id: int) -> bool:
    """Delete a user; their sessions and exercises go with them (ON DELETE CASCADE)."""
    table = db_manager.users()
    with table.pool.connection() as conn, conn.cursor() as cur:
        cur.execute(f"DELETE FROM {table.name} WHERE id = %s", (user_id,))
        return cur.rowcount > 0
