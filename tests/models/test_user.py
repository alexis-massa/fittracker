import pytest

from src.models import user
from src.utils.pg import UsersTable


def test_create_returns_the_new_user(users_table: UsersTable) -> None:
    created = user.create("alice", "correct horse")
    assert created.username == "alice"
    assert created.preferences.dark_mode is False


def test_create_never_stores_the_plaintext_password(users_table: UsersTable) -> None:
    user.create("alice", "correct horse")
    with users_table.pool.connection() as conn:
        (stored,) = conn.execute(f"SELECT password_hash FROM {users_table.name}").fetchone()  # type: ignore[misc]
    assert "correct horse" not in stored


@pytest.mark.parametrize("bad", ["", "ab", "has space", "semi;colon", "x" * 33])
def test_create_rejects_invalid_usernames(users_table: UsersTable, bad: str) -> None:
    with pytest.raises(ValueError):
        user.create(bad, "correct horse")


def test_create_rejects_short_passwords(users_table: UsersTable) -> None:
    with pytest.raises(ValueError):
        user.create("alice", "short")


def test_usernames_are_unique_ignoring_case(users_table: UsersTable) -> None:
    user.create("Alice", "correct horse")
    with pytest.raises(user.UsernameTakenError):
        user.create("alice", "another password")


def test_authenticate_accepts_the_right_password_in_any_case(users_table: UsersTable) -> None:
    created = user.create("Alice", "correct horse")
    found = user.authenticate("aLiCe", "correct horse")
    assert found is not None
    assert found.id == created.id


def test_authenticate_rejects_a_wrong_password(users_table: UsersTable) -> None:
    user.create("alice", "correct horse")
    assert user.authenticate("alice", "wrong horse") is None


def test_authenticate_rejects_an_unknown_user(users_table: UsersTable) -> None:
    assert user.authenticate("nobody", "correct horse") is None


def test_set_password_replaces_the_old_one(users_table: UsersTable) -> None:
    created = user.create("alice", "correct horse")
    assert user.set_password(created.id, "battery staple") is True
    assert user.authenticate("alice", "correct horse") is None
    assert user.authenticate("alice", "battery staple") is not None


def test_get_by_id_and_username_find_the_same_user(users_table: UsersTable) -> None:
    created = user.create("alice", "correct horse")
    assert user.get_by_id(created.id) == created
    assert user.get_by_username("ALICE") == created


def test_get_by_id_returns_none_for_unknown_id(users_table: UsersTable) -> None:
    assert user.get_by_id(999999) is None


def test_get_all_lists_users_in_creation_order(users_table: UsersTable) -> None:
    user.create("alice", "correct horse")
    user.create("bob", "correct horse")
    assert [u.username for u in user.get_all()] == ["alice", "bob"]


def test_update_preferences_persists_per_user(users_table: UsersTable) -> None:
    alice = user.create("alice", "correct horse")
    bob = user.create("bob", "correct horse")
    user.update_preferences(alice.id, {"dark_mode": True})
    fetched_alice, fetched_bob = user.get_by_id(alice.id), user.get_by_id(bob.id)
    assert fetched_alice is not None and fetched_alice.preferences.dark_mode is True
    assert fetched_bob is not None and fetched_bob.preferences.dark_mode is False


def test_update_preferences_ignores_unknown_keys(users_table: UsersTable) -> None:
    alice = user.create("alice", "correct horse")
    updated = user.update_preferences(alice.id, {"dark_mode": True, "is_admin": True})
    assert updated.dark_mode is True
    assert not hasattr(updated, "is_admin")


def test_delete_removes_the_user(users_table: UsersTable) -> None:
    created = user.create("alice", "correct horse")
    assert user.delete(created.id) is True
    assert user.get_by_id(created.id) is None
    assert user.delete(created.id) is False
