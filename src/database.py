from datetime import datetime
from typing import Any

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from .config import MONGODB_DB_NAME, MONGODB_URI


_client: MongoClient | None = None


def _get_database() -> Database:
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
    return _client[MONGODB_DB_NAME]


def _metrics_collection() -> Collection:
    return _get_database()["health_metrics"]


def _medications_collection() -> Collection:
    return _get_database()["medications"]


def _to_object_id(value: Any) -> ObjectId | None:
    if isinstance(value, ObjectId):
        return value
    if isinstance(value, str) and ObjectId.is_valid(value):
        return ObjectId(value)
    return None


def init_db() -> None:
    metrics = _metrics_collection()
    medications = _medications_collection()

    metrics.create_index([("recorded_at_dt", DESCENDING)])
    medications.create_index([("active", ASCENDING), ("schedule_time", ASCENDING)])


def add_health_metric(metric_name: str, metric_value: float, unit: str, recorded_at: str) -> None:
    try:
        recorded_at_dt = datetime.fromisoformat(recorded_at)
    except ValueError:
        recorded_at_dt = datetime.utcnow()

    _metrics_collection().insert_one(
        {
            "metric_name": metric_name,
            "metric_value": metric_value,
            "unit": unit,
            "recorded_at": recorded_at,
            "recorded_at_dt": recorded_at_dt,
        }
    )


def list_recent_metrics(limit: int = 20) -> list[dict[str, Any]]:
    cursor = (
        _metrics_collection()
        .find({}, {"_id": 0, "metric_name": 1, "metric_value": 1, "unit": 1, "recorded_at": 1})
        .sort("recorded_at_dt", DESCENDING)
        .limit(limit)
    )
    return list(cursor)


def add_medication(name: str, dosage: str, schedule_time: str, notes: str = "") -> None:
    now = datetime.utcnow()
    _medications_collection().insert_one(
        {
            "name": name,
            "dosage": dosage,
            "schedule_time": schedule_time,
            "notes": notes,
            "active": True,
            "created_at": now,
        }
    )


def list_medications(active_only: bool = True) -> list[dict[str, Any]]:
    query: dict[str, Any] = {"active": True} if active_only else {}
    cursor = _medications_collection().find(query).sort("schedule_time", ASCENDING)

    medications: list[dict[str, Any]] = []
    for document in cursor:
        medications.append(
            {
                "id": str(document["_id"]),
                "name": document.get("name", ""),
                "dosage": document.get("dosage", ""),
                "schedule_time": document.get("schedule_time", ""),
                "notes": document.get("notes", ""),
                "active": 1 if document.get("active", True) else 0,
                "created_at": document.get("created_at"),
            }
        )

    return medications


def deactivate_medication(medication_id: Any) -> None:
    object_id = _to_object_id(medication_id)
    if object_id is None:
        return

    _medications_collection().update_one({"_id": object_id}, {"$set": {"active": False}})
