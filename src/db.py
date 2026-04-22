from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from src.config import DB_NAME
from src.config import MONGO_URI


class DatabaseManager:
    def __init__(self) -> None:
        self._client: MongoClient[dict[str, Any]] | None = None
        self._db: Database[dict[str, Any]] | None = None

    def connect(self) -> None:
        self._client = MongoClient(MONGO_URI)
        self._db = self._client[DB_NAME]
        print(f"Connected to MongoDB — {DB_NAME}")

    def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None
            print("MongoDB connection closed")

    def get_collection(self, name: str) -> Collection[dict[str, Any]]:
        if self._db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._db[name]

    def exercises(self) -> Collection[dict[str, Any]]:
        return self.get_collection("exercises")

    def sessions(self) -> Collection[dict[str, Any]]:
        return self.get_collection("sessions")


db_manager = DatabaseManager()
