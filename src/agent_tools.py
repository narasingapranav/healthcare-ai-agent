import json
from datetime import datetime
from langchain_core.tools import tool

from .database import (
    add_health_metric,
    list_recent_metrics,
    list_all_metrics,
    add_medication,
    list_medications,
    add_health_goal,
    list_health_goals,
    add_nutrition_log,
    list_nutrition_logs,
    upsert_insurance_profile,
    list_insurance_profiles,
    add_medical_history_record,
    list_medical_history,
    upsert_regional_preference,
    list_regional_preferences,
)
from .medication_interactions import check_interactions
from .medical_lookup import get_medical_info
from .indian_health import IndianHealthService
from .rag import DatabaseRAG


# Dynamic RAG Search tool
@tool
def search_health_records(query: str) -> str:
    """Search through all historical records in the patient's database (metrics, medications, medical history, nutrition, preferences, insurance) using semantic/keyword similarity search. Use this for open-ended queries about past logs or status."""
    rag = DatabaseRAG()
    docs = rag.search(query, k=5)
    if not docs:
        return "No matching patient health database records found."
    
    results = []
    for doc in docs:
        t = doc.metadata.get("type", "general")
        results.append(f"[{t.upper()}] {doc.page_content}")
    return "\n\n".join(results)


# Medications tools
@tool
def get_user_medications(active_only: bool = True) -> str:
    """Retrieve the patient's active or inactive medication schedules from MongoDB."""
    meds = list_medications(active_only=active_only)
    if not meds:
        return "No medications found in database."
    return json.dumps(meds, indent=2, default=str)


@tool
def schedule_new_medication(name: str, dosage: str, schedule_time: str, notes: str = "") -> str:
    """Schedule a new medication reminder for the patient. Required parameters: name (e.g. Metformin), dosage (e.g. 500mg), schedule_time (format HH:MM, e.g. 08:00 or 20:30). Optional: notes."""
    try:
        # Validate time format
        datetime.strptime(schedule_time, "%H:%M")
        add_medication(name.strip(), dosage.strip(), schedule_time.strip(), notes.strip())
        return f"Medication '{name}' ({dosage}) successfully scheduled at {schedule_time}."
    except ValueError:
        return "Error: schedule_time must be in HH:MM 24-hour format (e.g., '14:30' or '08:00')."
    except Exception as e:
        return f"Error scheduling medication: {str(e)}"


# Health Metrics tools
@tool
def get_health_metrics(limit: int = 20) -> str:
    """Retrieve the recent logged health metrics like steps, weight, blood_pressure, heart_rate, blood_sugar, etc."""
    metrics = list_recent_metrics(limit=limit)
    if not metrics:
        return "No health metrics logged yet."
    return json.dumps(metrics, indent=2, default=str)


@tool
def log_new_health_metric(metric_name: str, metric_value: float, unit: str, recorded_at: str = None) -> str:
    """Log a health metric (e.g., steps, heart_rate, blood_pressure, weight) to MongoDB. Parameters: metric_name (str), metric_value (float), unit (str, e.g. bpm, steps, kg, mmHg), and optional ISO timestamp recorded_at (defaults to current time)."""
    try:
        timestamp = recorded_at or datetime.utcnow().isoformat()
        add_health_metric(metric_name.strip(), float(metric_value), unit.strip(), timestamp)
        return f"Successfully logged metric '{metric_name}' = {metric_value} {unit} at {timestamp}."
    except Exception as e:
        return f"Error logging health metric: {str(e)}"


# Goals tools
@tool
def get_health_goals(active_only: bool = True) -> str:
    """Retrieve current health goals set by the patient, indicating targets for steps, weight, blood_pressure, etc."""
    goals = list_health_goals(active_only=active_only)
    if not goals:
        return "No health goals set."
    return json.dumps(goals, indent=2, default=str)


@tool
def add_new_health_goal(metric_name: str, target_value: float, unit: str) -> str:
    """Set a new health goal for the patient. Parameters: metric_name (e.g., steps, weight), target_value (float, e.g., 10000, 70), unit (e.g. steps, kg)."""
    try:
        add_health_goal(metric_name.strip(), float(target_value), unit.strip())
        return f"Successfully added health goal: target {metric_name} of {target_value} {unit}."
    except Exception as e:
        return f"Error adding health goal: {str(e)}"


# Nutrition tools
@tool
def get_nutrition_logs(patient_region: str = "", limit: int = 10) -> str:
    """Retrieve food and nutrition logs. Can optionally filter by patient_region (e.g., North, South, West, East)."""
    logs = list_nutrition_logs(patient_region=patient_region, limit=limit)
    if not logs:
        return "No nutrition logs found."
    return json.dumps(logs, indent=2, default=str)


@tool
def log_nutrition(
    meal_date: str,
    meal_type: str,
    region: str,
    food_item: str,
    quantity: str,
    calories: float,
    protein_g: float = 0.0,
    carbs_g: float = 0.0,
    fats_g: float = 0.0,
    fiber_g: float = 0.0,
    notes: str = "",
) -> str:
    """Log a meal details to nutrition records. Required: meal_date (YYYY-MM-DD), meal_type (Breakfast, Lunch, Dinner, or Snack), region (e.g., North India), food_item, quantity, and calories. Optional: protein_g, carbs_g, fats_g, fiber_g, notes."""
    try:
        add_nutrition_log(
            meal_date=meal_date.strip(),
            meal_type=meal_type.strip(),
            region=region.strip(),
            food_item=food_item.strip(),
            quantity=quantity.strip(),
            calories=float(calories),
            protein_g=float(protein_g),
            carbs_g=float(carbs_g),
            fats_g=float(fats_g),
            fiber_g=float(fiber_g),
            notes=notes.strip(),
        )
        return f"Nutrition logged successfully: {food_item} ({quantity}, {calories} calories) on {meal_date}."
    except Exception as e:
        return f"Error logging nutrition: {str(e)}"


# Insurance tools
@tool
def get_insurance_profile(patient_name: str = "") -> str:
    """Retrieve insurance policy details, insurer, policy number, sum insured, and list of network hospitals."""
    profiles = list_insurance_profiles(patient_name=patient_name)
    if not profiles:
        return "No insurance profiles found."
    return json.dumps(profiles, indent=2, default=str)


@tool
def add_insurance_profile(
    patient_name: str,
    insurer: str,
    policy_number: str,
    policy_type: str,
    sum_insured: float,
    expiry_date: str,
    network_hospitals: str = "",
) -> str:
    """Add or update an insurance policy details for the patient. Parameters: patient_name, insurer, policy_number, policy_type (e.g., Family Floater, Individual), sum_insured (float), expiry_date (YYYY-MM-DD), network_hospitals (comma-separated list)."""
    try:
        upsert_insurance_profile(
            patient_name=patient_name.strip(),
            insurer=insurer.strip(),
            policy_number=policy_number.strip(),
            policy_type=policy_type.strip(),
            sum_insured=float(sum_insured),
            expiry_date=expiry_date.strip(),
            network_hospitals=network_hospitals.strip(),
        )
        return f"Insurance profile for '{patient_name}' (Insurer: {insurer}, Policy: {policy_number}) successfully saved."
    except Exception as e:
        return f"Error saving insurance profile: {str(e)}"


# Medical History tools
@tool
def get_medical_history(patient_name: str = "") -> str:
    """Retrieve patient medical history records (pre-existing conditions, diagnosis dates, prescribed meds, allergies, procedures, and doctor notes)."""
    records = list_medical_history(patient_name=patient_name)
    if not records:
        return "No medical history records found."
    return json.dumps(records, indent=2, default=str)


@tool
def add_medical_history(
    patient_name: str,
    condition_name: str,
    diagnosis_date: str,
    medications: str = "",
    allergies: str = "",
    procedures_done: str = "",
    notes: str = "",
) -> str:
    """Add a medical history record for a patient. Parameters: patient_name, condition_name (e.g., Diabetes, Hypertension), diagnosis_date (YYYY-MM-DD). Optional: medications, allergies, procedures_done, notes."""
    try:
        add_medical_history_record(
            patient_name=patient_name.strip(),
            condition_name=condition_name.strip(),
            diagnosis_date=diagnosis_date.strip(),
            medications=medications.strip(),
            allergies=allergies.strip(),
            procedures_done=procedures_done.strip(),
            notes=notes.strip(),
        )
        return f"Medical history record for '{patient_name}' ({condition_name}) successfully saved."
    except Exception as e:
        return f"Error adding medical history record: {str(e)}"


# Regional preferences tools
@tool
def get_regional_preferences(patient_name: str = "") -> str:
    """Retrieve patient regional profile (location city/state, preferred language, diet, budget limit, preferred specialties)."""
    prefs = list_regional_preferences(patient_name=patient_name)
    if not prefs:
        return "No regional preferences found."
    return json.dumps(prefs, indent=2, default=str)


@tool
def add_regional_preferences(
    patient_name: str,
    state: str,
    city: str,
    preferred_language: str,
    diet_preference: str,
    consultation_mode: str,
    max_budget_inr: float,
    preferred_specialties: str,
) -> str:
    """Add or update regional profile preferences for a patient. Parameters: patient_name, state, city, preferred_language (e.g., Hindi), diet_preference (e.g. Vegetarian), consultation_mode (e.g. Online, In-Person), max_budget_inr (float), preferred_specialties (comma-separated)."""
    try:
        upsert_regional_preference(
            patient_name=patient_name.strip(),
            state=state.strip(),
            city=city.strip(),
            preferred_language=preferred_language.strip(),
            diet_preference=diet_preference.strip(),
            consultation_mode=consultation_mode.strip(),
            max_budget_inr=float(max_budget_inr),
            preferred_specialties=preferred_specialties.strip(),
        )
        return f"Regional preferences for '{patient_name}' successfully updated."
    except Exception as e:
        return f"Error updating regional preferences: {str(e)}"


# Medication check & external lookup tools
@tool
def check_medication_interactions(medication_names: list[str]) -> str:
    """Check potential drug-to-drug interaction risks between a list of medication names. Pass a list of strings."""
    findings = check_interactions(medication_names)
    if not findings:
        return "No known dangerous drug interaction pairs found in the list."
    return "WARNING: Found potential interactions:\n" + "\n".join(findings)


@tool
def search_indian_medications(query: str) -> str:
    """Search for medicine details, prices, manufacturers, and uses in the Indian drug database catalog."""
    service = IndianHealthService()
    results = service.search_1mg_medicines(query)
    if not results:
        return f"No medicine info found for query: {query}."
    return json.dumps(results, indent=2, default=str)


@tool
def search_local_doctors(city: str, specialty: str) -> str:
    """Search for local doctors and consultation clinics by city and clinical specialty (e.g. Cardiologist, Dermatologist)."""
    service = IndianHealthService()
    results = service.search_practo_doctors(city=city, specialty=specialty)
    if not results:
        return f"No doctors found for specialty: {specialty} in city: {city}."
    return json.dumps(results, indent=2, default=str)


@tool
def lookup_ayurvedic_remedies(remedy_name: str) -> str:
    """Look up traditional Ayurvedic remedies, formulations, precautions/cautions, and evidence summaries (e.g. Ashwagandha, Triphala, Tulsi)."""
    service = IndianHealthService()
    result = service.get_ayurvedic_info(remedy_name)
    if not result:
        return f"No Ayurvedic information found for remedy: {remedy_name}."
    return json.dumps(result, indent=2, default=str)


@tool
def lookup_general_medical_info(topic: str) -> str:
    """Retrieve trusted medical information summaries, citations, and recommended actions for a general health topic (e.g. hypertension, fever, diabetes)."""
    result = get_medical_info(topic)
    if not result.get("title"):
        return f"No medical info found for topic: {topic}."
    return json.dumps(result, indent=2, default=str)
