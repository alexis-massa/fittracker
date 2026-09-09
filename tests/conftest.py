from collections.abc import Iterator
from typing import Any

import mongomock
from pymongo.collection import Collection
import pytest

from src.db import db_manager


@pytest.fixture
def mongo_collection() -> Collection[dict[str, Any]]:
    client: mongomock.MongoClient[dict[str, Any]] = mongomock.MongoClient()
    return client.db.collection


@pytest.fixture
def exercises_collection(
    monkeypatch: pytest.MonkeyPatch, mongo_collection: Collection[dict[str, Any]]
) -> Iterator[Collection[dict[str, Any]]]:
    monkeypatch.setattr(db_manager, "exercises", lambda: mongo_collection)
    yield mongo_collection


@pytest.fixture
def sessions_collection(
    monkeypatch: pytest.MonkeyPatch, mongo_collection: Collection[dict[str, Any]]
) -> Iterator[Collection[dict[str, Any]]]:
    monkeypatch.setattr(db_manager, "sessions", lambda: mongo_collection)
    yield mongo_collection
