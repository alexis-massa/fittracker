from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.collection import Collection
import pytest

from src.utils import mongo


def test_serialize_converts_top_level_object_id() -> None:
    oid = ObjectId()
    assert mongo.serialize({"_id": oid})["_id"] == str(oid)


def test_serialize_converts_object_ids_in_lists() -> None:
    oid = ObjectId()
    result = mongo.serialize({"ids": [oid, "plain"]})
    assert result["ids"] == [str(oid), "plain"]


def test_serialize_converts_object_ids_in_nested_dicts() -> None:
    oid = ObjectId()
    result = mongo.serialize({"nested": {"_id": oid, "name": "a"}})
    assert result["nested"] == {"_id": str(oid), "name": "a"}


def test_serialize_leaves_other_values_untouched() -> None:
    doc = {"name": "squat", "sets": 3, "weight": 12.5, "active": True, "notes": None}
    assert mongo.serialize(doc) == doc


def test_to_oid_passes_through_object_id() -> None:
    oid = ObjectId()
    assert mongo.to_oid(oid) is oid


def test_to_oid_converts_string_to_object_id() -> None:
    oid = ObjectId()
    assert mongo.to_oid(str(oid)) == oid


def test_find_all_sorts_ascending_by_default(mongo_collection: Collection[dict[str, Any]]) -> None:
    mongo_collection.insert_many([{"name": "b"}, {"name": "a"}])
    names = [doc["name"] for doc in mongo.find_all(mongo_collection, sort_field="name")]
    assert names == ["a", "b"]


def test_find_all_sorts_descending_when_requested(
    mongo_collection: Collection[dict[str, Any]],
) -> None:
    mongo_collection.insert_many([{"name": "a"}, {"name": "b"}])
    names = [
        doc["name"] for doc in mongo.find_all(mongo_collection, sort_field="name", ascending=False)
    ]
    assert names == ["b", "a"]


def test_find_all_serializes_object_ids_to_strings(
    mongo_collection: Collection[dict[str, Any]],
) -> None:
    mongo_collection.insert_one({"name": "a"})
    doc = mongo.find_all(mongo_collection)[0]
    assert isinstance(doc["_id"], str)


def test_find_one_returns_matching_document(mongo_collection: Collection[dict[str, Any]]) -> None:
    inserted_id = mongo_collection.insert_one({"name": "squat"}).inserted_id
    doc = mongo.find_one(mongo_collection, str(inserted_id))
    assert doc is not None
    assert doc["name"] == "squat"
    assert doc["_id"] == str(inserted_id)


def test_find_one_returns_none_when_missing(mongo_collection: Collection[dict[str, Any]]) -> None:
    assert mongo.find_one(mongo_collection, ObjectId()) is None


def test_insert_one_returns_new_id_and_persists_document(
    mongo_collection: Collection[dict[str, Any]],
) -> None:
    new_id = mongo.insert_one(mongo_collection, {"name": "squat"})
    assert mongo_collection.find_one({"_id": ObjectId(new_id)}) is not None


def test_update_one_returns_true_when_document_matched(
    mongo_collection: Collection[dict[str, Any]],
) -> None:
    inserted_id = mongo_collection.insert_one({"name": "squat"}).inserted_id
    assert mongo.update_one(mongo_collection, str(inserted_id), {"name": "lunge"}) is True
    assert mongo_collection.find_one({"_id": inserted_id})["name"] == "lunge"  # type: ignore[index]


def test_update_one_returns_false_when_document_missing(
    mongo_collection: Collection[dict[str, Any]],
) -> None:
    assert mongo.update_one(mongo_collection, ObjectId(), {"name": "lunge"}) is False


def test_delete_one_returns_true_and_removes_document(
    mongo_collection: Collection[dict[str, Any]],
) -> None:
    inserted_id = mongo_collection.insert_one({"name": "squat"}).inserted_id
    assert mongo.delete_one(mongo_collection, str(inserted_id)) is True
    assert mongo_collection.find_one({"_id": inserted_id}) is None


def test_delete_one_returns_false_when_document_missing(
    mongo_collection: Collection[dict[str, Any]],
) -> None:
    assert mongo.delete_one(mongo_collection, ObjectId()) is False


@pytest.mark.parametrize("bad_value", ["not-an-oid", "123"])
def test_to_oid_raises_for_invalid_string(bad_value: str) -> None:
    with pytest.raises(InvalidId):
        mongo.to_oid(bad_value)
