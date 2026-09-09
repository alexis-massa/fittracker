# src/utils/mongo.py
from typing import Any

from bson import ObjectId
from pymongo.collection import Collection


def serialize(doc: dict[str, Any]) -> dict[str, Any]:
    """Recursively convert ObjectId values to str for JSON safety."""
    out: dict[str, Any] = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, list):
            out[k] = [str(i) if isinstance(i, ObjectId) else i for i in v]
        elif isinstance(v, dict):
            out[k] = serialize(v)
        else:
            out[k] = v
    return out


def to_oid(value: Any) -> ObjectId:
    """Coerce a str or ObjectId to ObjectId."""
    if isinstance(value, ObjectId):
        return value
    return ObjectId(str(value))


def find_all(
    col: Collection[dict[str, Any]], sort_field: str = "_id", ascending: bool = True
) -> list[dict[str, Any]]:
    """Find all documents in `col`.

    Args:
        col (Collection[dict[str, Any]]): Collection to query
        sort_field (str, optional): Field to sort by. Defaults to "_id".
        ascending (bool, optional): Direction to sort in. Defaults to True (ASC).

    Returns:
        list[dict[str, Any]]: All documents of collection, sorted.
    """
    direction = 1 if ascending else -1
    return [serialize(doc) for doc in col.find().sort(sort_field, direction)]


def find_one(col: Collection[dict[str, Any]], doc_id: Any) -> dict[str, Any] | None:
    """Find document with id `doc_id` in `col` collection"""
    doc = col.find_one({"_id": to_oid(doc_id)})
    return serialize(doc) if doc else None


def insert_one(col: Collection[dict[str, Any]], data: dict[str, Any]) -> str:
    """Insert `data` document in `col`."""
    result = col.insert_one(data)
    return str(result.inserted_id)


def update_one(col: Collection[dict[str, Any]], doc_id: Any, data: dict[str, Any]) -> bool:
    """Update `data` of document `doc_id` in `col` collection"""
    result = col.update_one({"_id": to_oid(doc_id)}, {"$set": data})
    return result.matched_count > 0


def delete_one(col: Collection[dict[str, Any]], doc_id: Any) -> bool:
    """Delete `doc_id` document from `col` collection"""
    result = col.delete_one({"_id": to_oid(doc_id)})
    return result.deleted_count > 0
