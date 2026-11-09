"""End-to-end checks of the login wall and per-user isolation, through the real app."""

from collections.abc import Iterator

from nicegui.testing import User
import pytest

from src import auth
from src.db import db_manager
from src.models import exercise as exercise_model
from src.models import session as session_model
from src.models import user as user_model
from src.models.exercise import ExerciseDefinition
from src.models.session import Session
from src.utils.pg import PgTable
from src.utils.pg import UsersTable
from src.utils.throttle import LoginThrottle

PASSWORD = "correct horse"


@pytest.fixture(autouse=True)
def app_data(
    monkeypatch: pytest.MonkeyPatch,
    users_table: UsersTable,
    exercises_table: PgTable,
    sessions_table: PgTable,
) -> Iterator[None]:
    monkeypatch.setattr(db_manager, "connect", lambda: None)
    monkeypatch.setattr(db_manager, "disconnect", lambda: None)
    monkeypatch.setattr(auth, "login_throttle", LoginThrottle())
    yield


async def sign_in(user: User, username: str, password: str = PASSWORD) -> None:
    await user.open("/login")
    user.find("Username").type(username)
    user.find("Password").type(password)
    user.find("Sign in").click()


@pytest.mark.parametrize(
    "path",
    ["/", "/exercises", "/sessions/new", "/sessions/1", "/sessions/1/edit", "/sessions/1/run"]
    + ["/sessions/1/duplicate", "/exercises/1/edit"],
)
async def test_every_page_redirects_anonymous_visitors_to_login(
    user: User, app_data: None, path: str
) -> None:
    await user.open(path)
    await user.should_see("Sign in")


async def test_pwa_files_are_reachable_without_logging_in(user: User, app_data: None) -> None:
    for path in ["/sw.js", "/static/manifest.webmanifest", "/static/icons/icon-192.png"]:
        assert (await user.http_client.get(path)).status_code == 200


async def test_wrong_password_is_rejected(user: User, app_data: None) -> None:
    user_model.create("alice", PASSWORD)
    await sign_in(user, "alice", "wrong horse")
    await user.should_see("Invalid username or password.")


async def test_unknown_user_is_rejected_the_same_way(user: User, app_data: None) -> None:
    await sign_in(user, "nobody")
    await user.should_see("Invalid username or password.")


async def test_account_locks_after_repeated_failures_even_for_the_right_password(
    user: User, app_data: None
) -> None:
    user_model.create("alice", PASSWORD)
    for _ in range(5):
        await sign_in(user, "alice", "wrong horse")
    await sign_in(user, "alice", PASSWORD)
    await user.should_see("Too many failed attempts")


async def test_signing_in_lands_on_the_page_originally_requested(
    user: User, app_data: None
) -> None:
    alice = user_model.create("alice", PASSWORD)
    session_id = session_model.create(alice.id, Session(date="2026-03-04"))
    await user.open(f"/sessions/{session_id}")
    user.find("Username").type("alice")
    user.find("Password").type(PASSWORD)
    user.find("Sign in").click()
    await user.should_see("Session — 2026-03-04")


async def test_a_user_sees_their_own_session(user: User, app_data: None) -> None:
    alice = user_model.create("alice", PASSWORD)
    session_id = session_model.create(alice.id, Session(date="2026-03-04"))
    await sign_in(user, "alice")
    await user.open(f"/sessions/{session_id}")
    await user.should_see("Session — 2026-03-04")


@pytest.mark.parametrize("suffix", ["", "/edit", "/run", "/duplicate"])
async def test_a_user_cannot_open_another_users_session(
    user: User, app_data: None, suffix: str
) -> None:
    alice = user_model.create("alice", PASSWORD)
    user_model.create("bob", PASSWORD)
    session_id = session_model.create(alice.id, Session(date="2026-03-04"))
    await sign_in(user, "bob")
    await user.open(f"/sessions/{session_id}{suffix}")
    await user.should_see("Session not found.")
    await user.should_not_see("2026-03-04")


async def test_a_user_cannot_open_another_users_exercise(user: User, app_data: None) -> None:
    alice = user_model.create("alice", PASSWORD)
    user_model.create("bob", PASSWORD)
    exercise_id = exercise_model.create(alice.id, ExerciseDefinition(name="Z", label="Secret"))
    await sign_in(user, "bob")
    await user.open(f"/exercises/{exercise_id}/edit")
    await user.should_see("Exercise not found.")
    await user.should_not_see("Secret")


async def test_the_exercise_library_only_lists_the_users_own_exercises(
    user: User, app_data: None
) -> None:
    alice = user_model.create("alice", PASSWORD)
    bob = user_model.create("bob", PASSWORD)
    exercise_model.create(alice.id, ExerciseDefinition(name="A", label="AliceOnly"))
    exercise_model.create(bob.id, ExerciseDefinition(name="B", label="BobOnly"))
    await sign_in(user, "bob")
    await user.open("/exercises")
    await user.should_see("BobOnly")
    await user.should_not_see("AliceOnly")


async def test_a_deleted_user_is_logged_out_on_the_next_page_load(
    user: User, app_data: None
) -> None:
    alice = user_model.create("alice", PASSWORD)
    await sign_in(user, "alice")
    await user.open("/exercises")
    await user.should_see("Exercise Library")
    user_model.delete(alice.id)
    await user.open("/exercises")
    await user.should_see("Sign in")
