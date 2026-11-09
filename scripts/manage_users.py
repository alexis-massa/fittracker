#!/usr/bin/env python3
"""Manage who can sign in to FitTracker. There is no self-signup: accounts exist only
because you create them here.

Usage (locally; in production prefix with `docker compose exec app .venv/bin/`):
    uv run python scripts/manage_users.py create USERNAME
    uv run python scripts/manage_users.py passwd USERNAME
    uv run python scripts/manage_users.py list
    uv run python scripts/manage_users.py delete USERNAME
    uv run python scripts/manage_users.py claim-legacy USERNAME

Passwords are always prompted for (never passed as arguments), so they stay out of
shell history.
"""

import argparse
from getpass import getpass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import db_manager
from src.models import exercise as exercise_model
from src.models import session as session_model
from src.models import user as user_model
from src.models.user import User


def _find(username: str) -> User:
    user = user_model.get_by_username(username)
    if user is None:
        sys.exit(f"No such user: {username}")
    return user


def _prompt_password() -> str:
    password = getpass("Password: ")
    if password != getpass("Repeat password: "):
        sys.exit("Passwords do not match.")
    return password


def create(args: argparse.Namespace) -> None:
    user = user_model.create(args.username, _prompt_password())
    print(f"Created user '{user.username}'.")
    print(f"Optionally give them the Lafay exercise library: seed_exercises.py {user.username}")


def passwd(args: argparse.Namespace) -> None:
    user = _find(args.username)
    user_model.set_password(user.id, _prompt_password())
    print(f"Password updated for '{user.username}'.")


def list_users(_: argparse.Namespace) -> None:
    users = user_model.get_all()
    for user in users:
        sessions = len(session_model.get_all(user.id))
        exercises = len(exercise_model.get_all(user.id))
        print(f"{user.username:<20} {sessions} sessions, {exercises} exercises")
    unowned = db_manager.count_unowned()
    if not users:
        print("No users yet.")
    if unowned:
        print(f"\n{unowned} rows have no owner (claim them with: claim-legacy USERNAME)")


def delete(args: argparse.Namespace) -> None:
    user = _find(args.username)
    print(f"This permanently deletes '{user.username}' and all their sessions and exercises.")
    if input("Type the username to confirm: ").strip() != user.username:
        sys.exit("Aborted.")
    user_model.delete(user.id)
    print(f"Deleted '{user.username}'.")


def claim_legacy(args: argparse.Namespace) -> None:
    user = _find(args.username)
    claimed = db_manager.claim_unowned(user.id)
    print(f"Assigned {claimed} previously-unowned rows to '{user.username}'.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0] if __doc__ else None)
    commands = parser.add_subparsers(dest="command", required=True)
    for name, func in (
        ("create", create),
        ("passwd", passwd),
        ("delete", delete),
        ("claim-legacy", claim_legacy),
    ):
        sub = commands.add_parser(name)
        sub.add_argument("username")
        sub.set_defaults(func=func)
    commands.add_parser("list").set_defaults(func=list_users)

    args = parser.parse_args()
    db_manager.connect()
    try:
        args.func(args)
    except (ValueError, user_model.UsernameTakenError) as exc:
        sys.exit(str(exc))
    finally:
        db_manager.disconnect()


if __name__ == "__main__":
    main()
