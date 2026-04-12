from datetime import datetime
from typing import Any
import logging

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError, ConnectionFailure, ServerSelectionTimeoutError

from .config import MONGODB_DB_NAME, MONGODB_URI

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database operation failures."""
    pass


_client: MongoClient | None = None


def _get_database() -> Database:
    """Get MongoDB database with error handling."""
    global _client
    try:
        if _client is None:
            _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
        # Verify connection
        _client.admin.command('ping')
        return _client[MONGODB_DB_NAME]
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"MongoDB connection failed: {str(e)}")
        raise DatabaseError(
            f"Failed to connect to MongoDB. Please ensure MongoDB is running at {MONGODB_URI}. Error: {str(e)}"
        ) from e
    except Exception as e:
        logger.error(f"Unexpected database error: {str(e)}")
        raise DatabaseError(f"Database initialization error: {str(e)}") from e


def _metrics_collection() -> Collection:
    return _get_database()["health_metrics"]


def _medications_collection() -> Collection:
    return _get_database()["medications"]


def _goals_collection() -> Collection:
    return _get_database()["health_goals"]


def _indian_medications_collection() -> Collection:
    return _get_database()["indian_medications"]


def _nutrition_logs_collection() -> Collection:
    return _get_database()["nutrition_logs"]


def _insurance_profiles_collection() -> Collection:
    return _get_database()["insurance_profiles"]


def _medical_history_collection() -> Collection:
    return _get_database()["medical_history"]


def _regional_preferences_collection() -> Collection:
    return _get_database()["regional_preferences"]


def _to_object_id(value: Any) -> ObjectId | None:
    if isinstance(value, ObjectId):
        return value
    if isinstance(value, str) and ObjectId.is_valid(value):
        return ObjectId(value)
    return None


def init_db() -> None:
    """Initialize database collections and indexes with error handling."""
    try:
        metrics = _metrics_collection()
        medications = _medications_collection()
        goals = _goals_collection()
        indian_medications = _indian_medications_collection()
        nutrition_logs = _nutrition_logs_collection()
        insurance_profiles = _insurance_profiles_collection()
        medical_history = _medical_history_collection()
        regional_preferences = _regional_preferences_collection()

        # Create indexes
        metrics.create_index([("recorded_at_dt", DESCENDING)])
        medications.create_index([("active", ASCENDING), ("schedule_time", ASCENDING)])
        goals.create_index([("active", ASCENDING), ("created_at", DESCENDING)])
        indian_medications.create_index([("name", ASCENDING), ("source", ASCENDING)], unique=True)
        indian_medications.create_index([("updated_at", DESCENDING)])
        nutrition_logs.create_index([("meal_date", DESCENDING), ("created_at", DESCENDING)])
        nutrition_logs.create_index([("region", ASCENDING)])
        insurance_profiles.create_index([("patient_name", ASCENDING), ("policy_number", ASCENDING)], unique=True)
        insurance_profiles.create_index([("updated_at", DESCENDING)])
        medical_history.create_index([("patient_name", ASCENDING), ("created_at", DESCENDING)])
        regional_preferences.create_index([("patient_name", ASCENDING)], unique=True)
        regional_preferences.create_index([("updated_at", DESCENDING)])
        
        logger.info("Database initialized successfully with all indexes created.")
    except PyMongoError as e:
        logger.error(f"Index creation failed: {str(e)}")
        raise DatabaseError(f"Failed to initialize database indexes: {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {str(e)}")
        raise DatabaseError(f"Database initialization failed: {str(e)}") from e


def add_health_metric(metric_name: str, metric_value: float, unit: str, recorded_at: str) -> None:
    """Add health metric with error handling."""
    try:
        try:
            recorded_at_dt = datetime.fromisoformat(recorded_at)
        except ValueError:
            logger.warning(f"Invalid timestamp format '{recorded_at}', using current time.")
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
        logger.info(f"Health metric '{metric_name}' saved successfully (value: {metric_value} {unit})")
    except PyMongoError as e:
        logger.error(f"Failed to save health metric: {str(e)}")
        raise DatabaseError(f"Failed to save health metric '{metric_name}': {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error saving health metric: {str(e)}")
        raise DatabaseError(f"Error saving health metric: {str(e)}") from e


def list_recent_metrics(limit: int = 20) -> list[dict[str, Any]]:
    cursor = (
        _metrics_collection()
        .find({}, {"_id": 0, "metric_name": 1, "metric_value": 1, "unit": 1, "recorded_at": 1})
        .sort("recorded_at_dt", DESCENDING)
        .limit(limit)
    )
    return list(cursor)


def list_all_metrics() -> list[dict[str, Any]]:
    cursor = _metrics_collection().find(
        {},
        {"_id": 0, "metric_name": 1, "metric_value": 1, "unit": 1, "recorded_at": 1},
    )
    return list(cursor)


def add_medication(name: str, dosage: str, schedule_time: str, notes: str = "") -> None:
    """Add medication with error handling."""
    try:
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
        logger.info(f"Medication '{name}' ({dosage}) scheduled successfully.")
    except PyMongoError as e:
        logger.error(f"Failed to add medication: {str(e)}")
        raise DatabaseError(f"Failed to add medication '{name}': {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error adding medication: {str(e)}")
        raise DatabaseError(f"Error adding medication: {str(e)}") from e


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


def add_health_goal(metric_name: str, target_value: float, unit: str) -> None:
    now = datetime.utcnow()
    _goals_collection().insert_one(
        {
            "metric_name": metric_name,
            "target_value": target_value,
            "unit": unit,
            "active": True,
            "created_at": now,
        }
    )


def list_health_goals(active_only: bool = True) -> list[dict[str, Any]]:
    query: dict[str, Any] = {"active": True} if active_only else {}
    cursor = _goals_collection().find(query).sort("created_at", DESCENDING)

    goals: list[dict[str, Any]] = []
    for document in cursor:
        goals.append(
            {
                "id": str(document["_id"]),
                "metric_name": document.get("metric_name", ""),
                "target_value": float(document.get("target_value", 0)),
                "unit": document.get("unit", ""),
                "active": 1 if document.get("active", True) else 0,
                "created_at": document.get("created_at"),
            }
        )

    return goals


def deactivate_health_goal(goal_id: Any) -> None:
    object_id = _to_object_id(goal_id)
    if object_id is None:
        return

    _goals_collection().update_one({"_id": object_id}, {"$set": {"active": False}})


def upsert_indian_medication(
    source: str,
    name: str,
    manufacturer: str = "",
    price_inr: float | None = None,
    uses: str = "",
    product_url: str = "",
    raw_payload: dict[str, Any] | None = None,
) -> None:
    now = datetime.utcnow()
    _indian_medications_collection().update_one(
        {"source": source.strip().lower(), "name": name.strip().lower()},
        {
            "$set": {
                "source": source.strip().lower(),
                "name": name.strip(),
                "manufacturer": manufacturer.strip(),
                "price_inr": price_inr,
                "uses": uses.strip(),
                "product_url": product_url.strip(),
                "raw_payload": raw_payload or {},
                "updated_at": now,
            },
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
    )


def list_indian_medications(search: str = "", source: str = "", limit: int = 25) -> list[dict[str, Any]]:
    query: dict[str, Any] = {}
    if search.strip():
        query["name"] = {"$regex": search.strip(), "$options": "i"}
    if source.strip():
        query["source"] = source.strip().lower()

    cursor = _indian_medications_collection().find(query).sort("updated_at", DESCENDING).limit(limit)
    records: list[dict[str, Any]] = []
    for document in cursor:
        records.append(
            {
                "id": str(document.get("_id")),
                "source": document.get("source", ""),
                "name": document.get("name", ""),
                "manufacturer": document.get("manufacturer", ""),
                "price_inr": document.get("price_inr"),
                "uses": document.get("uses", ""),
                "product_url": document.get("product_url", ""),
                "updated_at": document.get("updated_at"),
            }
        )
    return records


def add_nutrition_log(
    meal_date: str,
    meal_type: str,
    region: str,
    food_item: str,
    quantity: str,
    calories: float,
    protein_g: float,
    carbs_g: float,
    fats_g: float,
    fiber_g: float,
    notes: str = "",
) -> None:
    """Add nutrition log with error handling."""
    try:
        _nutrition_logs_collection().insert_one(
            {
                "meal_date": meal_date,
                "meal_type": meal_type,
                "region": region,
                "food_item": food_item,
                "quantity": quantity,
                "calories": calories,
                "protein_g": protein_g,
                "carbs_g": carbs_g,
                "fats_g": fats_g,
                "fiber_g": fiber_g,
                "notes": notes,
                "created_at": datetime.utcnow(),
            }
        )
        logger.info(f"Nutrition log for '{food_item}' ({calories} cal) saved successfully.")
    except PyMongoError as e:
        logger.error(f"Failed to add nutrition log: {str(e)}")
        raise DatabaseError(f"Failed to save nutrition log for '{food_item}': {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error adding nutrition log: {str(e)}")
        raise DatabaseError(f"Error adding nutrition log: {str(e)}") from e


def list_nutrition_logs(patient_region: str = "", limit: int = 100) -> list[dict[str, Any]]:
    query: dict[str, Any] = {}
    if patient_region.strip():
        query["region"] = {"$regex": patient_region.strip(), "$options": "i"}

    cursor = _nutrition_logs_collection().find(query).sort("created_at", DESCENDING).limit(limit)
    rows: list[dict[str, Any]] = []
    for document in cursor:
        rows.append(
            {
                "id": str(document.get("_id")),
                "meal_date": document.get("meal_date", ""),
                "meal_type": document.get("meal_type", ""),
                "region": document.get("region", ""),
                "food_item": document.get("food_item", ""),
                "quantity": document.get("quantity", ""),
                "calories": document.get("calories", 0.0),
                "protein_g": document.get("protein_g", 0.0),
                "carbs_g": document.get("carbs_g", 0.0),
                "fats_g": document.get("fats_g", 0.0),
                "fiber_g": document.get("fiber_g", 0.0),
                "notes": document.get("notes", ""),
                "created_at": document.get("created_at"),
            }
        )
    return rows


def upsert_insurance_profile(
    patient_name: str,
    insurer: str,
    policy_number: str,
    policy_type: str,
    sum_insured: float,
    expiry_date: str,
    network_hospitals: str,
) -> None:
    """Upsert insurance profile with error handling."""
    try:
        now = datetime.utcnow()
        result = _insurance_profiles_collection().update_one(
            {"patient_name": patient_name.strip(), "policy_number": policy_number.strip()},
            {
                "$set": {
                    "patient_name": patient_name.strip(),
                    "insurer": insurer.strip(),
                    "policy_number": policy_number.strip(),
                    "policy_type": policy_type.strip(),
                    "sum_insured": sum_insured,
                    "expiry_date": expiry_date.strip(),
                    "network_hospitals": network_hospitals.strip(),
                    "updated_at": now,
                },
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
        )
        if result.upserted_id:
            logger.info(f"Insurance profile created for patient '{patient_name}' (Policy: {policy_number}).")
        else:
            logger.info(f"Insurance profile updated for patient '{patient_name}'.")
    except PyMongoError as e:
        logger.error(f"Failed to upsert insurance profile: {str(e)}")
        raise DatabaseError(f"Failed to save insurance profile for '{patient_name}': {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error upserting insurance profile: {str(e)}")
        raise DatabaseError(f"Error saving insurance profile: {str(e)}") from e


def list_insurance_profiles(patient_name: str = "", limit: int = 50) -> list[dict[str, Any]]:
    query: dict[str, Any] = {}
    if patient_name.strip():
        query["patient_name"] = {"$regex": patient_name.strip(), "$options": "i"}

    cursor = _insurance_profiles_collection().find(query).sort("updated_at", DESCENDING).limit(limit)
    rows: list[dict[str, Any]] = []
    for document in cursor:
        rows.append(
            {
                "id": str(document.get("_id")),
                "patient_name": document.get("patient_name", ""),
                "insurer": document.get("insurer", ""),
                "policy_number": document.get("policy_number", ""),
                "policy_type": document.get("policy_type", ""),
                "sum_insured": document.get("sum_insured", 0.0),
                "expiry_date": document.get("expiry_date", ""),
                "network_hospitals": document.get("network_hospitals", ""),
                "updated_at": document.get("updated_at"),
            }
        )
    return rows


def add_medical_history_record(
    patient_name: str,
    condition_name: str,
    diagnosis_date: str,
    medications: str,
    allergies: str,
    procedures_done: str,
    notes: str,
) -> None:
    """Add medical history record with error handling."""
    try:
        _medical_history_collection().insert_one(
            {
                "patient_name": patient_name.strip(),
                "condition_name": condition_name.strip(),
                "diagnosis_date": diagnosis_date.strip(),
                "medications": medications.strip(),
                "allergies": allergies.strip(),
                "procedures_done": procedures_done.strip(),
                "notes": notes.strip(),
                "created_at": datetime.utcnow(),
            }
        )
        logger.info(f"Medical history record for patient '{patient_name}' (Condition: {condition_name}) saved.")
    except PyMongoError as e:
        logger.error(f"Failed to add medical history record: {str(e)}")
        raise DatabaseError(f"Failed to save medical history for '{patient_name}': {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error adding medical history: {str(e)}")
        raise DatabaseError(f"Error adding medical history: {str(e)}") from e


def list_medical_history(patient_name: str = "", limit: int = 100) -> list[dict[str, Any]]:
    query: dict[str, Any] = {}
    if patient_name.strip():
        query["patient_name"] = {"$regex": patient_name.strip(), "$options": "i"}

    cursor = _medical_history_collection().find(query).sort("created_at", DESCENDING).limit(limit)
    rows: list[dict[str, Any]] = []
    for document in cursor:
        rows.append(
            {
                "id": str(document.get("_id")),
                "patient_name": document.get("patient_name", ""),
                "condition_name": document.get("condition_name", ""),
                "diagnosis_date": document.get("diagnosis_date", ""),
                "medications": document.get("medications", ""),
                "allergies": document.get("allergies", ""),
                "procedures_done": document.get("procedures_done", ""),
                "notes": document.get("notes", ""),
                "created_at": document.get("created_at"),
            }
        )
    return rows


def upsert_regional_preference(
    patient_name: str,
    state: str,
    city: str,
    preferred_language: str,
    diet_preference: str,
    consultation_mode: str,
    max_budget_inr: float,
    preferred_specialties: str,
) -> None:
    """Upsert regional preference with error handling."""
    try:
        now = datetime.utcnow()
        result = _regional_preferences_collection().update_one(
            {"patient_name": patient_name.strip()},
            {
                "$set": {
                    "patient_name": patient_name.strip(),
                    "state": state.strip(),
                    "city": city.strip(),
                    "preferred_language": preferred_language.strip(),
                    "diet_preference": diet_preference.strip(),
                    "consultation_mode": consultation_mode.strip(),
                    "max_budget_inr": max_budget_inr,
                    "preferred_specialties": preferred_specialties.strip(),
                    "updated_at": now,
                },
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
        )
        if result.upserted_id:
            logger.info(f"Regional preference created for patient '{patient_name}'.")
        else:
            logger.info(f"Regional preference updated for patient '{patient_name}'.")
    except PyMongoError as e:
        logger.error(f"Failed to upsert regional preference: {str(e)}")
        raise DatabaseError(f"Failed to save regional preference for '{patient_name}': {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error upserting regional preference: {str(e)}")
        raise DatabaseError(f"Error saving regional preference: {str(e)}") from e


def list_regional_preferences(patient_name: str = "", limit: int = 50) -> list[dict[str, Any]]:
    query: dict[str, Any] = {}
    if patient_name.strip():
        query["patient_name"] = {"$regex": patient_name.strip(), "$options": "i"}

    cursor = _regional_preferences_collection().find(query).sort("updated_at", DESCENDING).limit(limit)
    rows: list[dict[str, Any]] = []
    for document in cursor:
        rows.append(
            {
                "id": str(document.get("_id")),
                "patient_name": document.get("patient_name", ""),
                "state": document.get("state", ""),
                "city": document.get("city", ""),
                "preferred_language": document.get("preferred_language", ""),
                "diet_preference": document.get("diet_preference", ""),
                "consultation_mode": document.get("consultation_mode", ""),
                "max_budget_inr": document.get("max_budget_inr", 0.0),
                "preferred_specialties": document.get("preferred_specialties", ""),
                "updated_at": document.get("updated_at"),
            }
        )
    return rows
