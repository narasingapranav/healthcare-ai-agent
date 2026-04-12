"""
Comprehensive input validators for health data, medications, and insurance information.
Provides validation functions with detailed error messages for health data processing.
"""

from datetime import datetime
import re
from typing import Any


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_health_metric(metric_name: str, metric_value: str, unit: str) -> tuple[str, float, str, str]:
    """
    Validate and normalize health metric input.
    
    Args:
        metric_name: Name of the health metric (e.g., 'blood_pressure', 'weight')
        metric_value: Numeric value as string
        unit: Unit of measurement
        
    Returns:
        Tuple of (cleaned_metric_name, float_value, cleaned_unit, iso_timestamp)
        
    Raises:
        ValidationError: If input is invalid with descriptive message
    """
    # Validate metric name
    if not metric_name or not isinstance(metric_name, str):
        raise ValidationError("Metric name is required and must be text.")
    
    clean_name = metric_name.strip().lower()
    if not clean_name or len(clean_name) < 2:
        raise ValidationError("Metric name must be at least 2 characters long.")
    
    if not re.match(r"^[a-z0-9_\s]+$", clean_name):
        raise ValidationError("Metric name can only contain letters, numbers, underscores, and spaces.")
    
    # Validate metric value
    try:
        value = float(metric_value)
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Metric value must be a valid number. Received: '{metric_value}'") from e
    
    # Range validation for common metrics
    METRIC_RANGES = {
        "blood pressure systolic": (70, 250),
        "blood pressure diastolic": (40, 150),
        "heart rate": (20, 200),
        "weight": (10, 500),
        "temperature": (32, 45),
        "blood glucose": (30, 600),
        "cholesterol": (0, 500),
        "triglycerides": (0, 500),
        "hba1c": (3.0, 15.0),
    }
    
    # Check if metric matches a known range
    for metric_key, (min_val, max_val) in METRIC_RANGES.items():
        if metric_key in clean_name:
            if not (min_val <= value <= max_val):
                raise ValidationError(
                    f"Invalid value for {clean_name}: {value} is outside normal range ({min_val}-{max_val}). "
                    f"Please verify the value and unit."
                )
    
    # Validate unit
    if not unit or not isinstance(unit, str):
        raise ValidationError("Unit is required and must be text.")
    
    clean_unit = unit.strip()
    if not clean_unit:
        raise ValidationError("Unit cannot be empty.")
    
    valid_units = {
        "mmhg", "bpm", "kg", "lbs", "°c", "°f", "mg/dl", "mmol/l", "mg/dl", "%", "mm",
        "ml", "liters", "iu", "units", "mcg", "mg", "g", "hour", "hours", "minutes"
    }
    
    if clean_unit.lower() not in valid_units:
        # Don't fail, but warn - user might have custom unit
        pass
    
    timestamp = datetime.utcnow().isoformat()
    return clean_name, value, clean_unit, timestamp


def validate_medication(name: str, dosage: str, schedule: str, active: bool = True) -> dict[str, Any]:
    """
    Validate and normalize medication input.
    
    Args:
        name: Medication name
        dosage: Dosage information (e.g., "500mg")
        schedule: Schedule information (e.g., "twice daily")
        active: Whether medication is currently active
        
    Returns:
        Dictionary with validated medication fields
        
    Raises:
        ValidationError: If input is invalid
    """
    # Validate name
    if not name or not isinstance(name, str):
        raise ValidationError("Medication name is required and must be text.")
    
    clean_name = name.strip()
    if not clean_name or len(clean_name) < 2:
        raise ValidationError("Medication name must be at least 2 characters long.")
    
    if not re.match(r"^[a-zA-Z0-9\s\-()]+$", clean_name):
        raise ValidationError(
            "Medication name contains invalid characters. Use letters, numbers, spaces, hyphens, and parentheses."
        )
    
    # Validate dosage
    if not dosage or not isinstance(dosage, str):
        raise ValidationError("Dosage is required (e.g., '500mg', '2 tablets').")
    
    clean_dosage = dosage.strip()
    if not clean_dosage or len(clean_dosage) < 1:
        raise ValidationError("Dosage cannot be empty.")
    
    if len(clean_dosage) > 100:
        raise ValidationError("Dosage description is too long. Keep it concise.")
    
    # Validate schedule
    if not schedule or not isinstance(schedule, str):
        raise ValidationError("Schedule is required (e.g., 'twice daily', 'once at bedtime').")
    
    clean_schedule = schedule.strip()
    if not clean_schedule or len(clean_schedule) < 3:
        raise ValidationError("Schedule must be descriptive (e.g., 'twice daily', 'once every 12 hours').")
    
    if len(clean_schedule) > 100:
        raise ValidationError("Schedule description is too long.")
    
    return {
        "name": clean_name,
        "dosage": clean_dosage,
        "schedule": clean_schedule,
        "active": bool(active),
        "created_at": datetime.utcnow().isoformat(),
    }


def validate_nutrition_log(meal_type: str, calories: str, protein: str, carbs: str, fat: str, 
                          meal_date: str, region: str = "") -> dict[str, Any]:
    """
    Validate and normalize nutrition log input.
    
    Args:
        meal_type: Type of meal (e.g., 'breakfast', 'lunch', 'dinner', 'snack')
        calories: Caloric intake
        protein: Protein in grams
        carbs: Carbohydrates in grams
        fat: Fat in grams
        meal_date: Date of meal (YYYY-MM-DD)
        region: Optional region for dietary recommendations
        
    Returns:
        Dictionary with validated nutrition log fields
        
    Raises:
        ValidationError: If input is invalid
    """
    # Validate meal type
    if not meal_type or not isinstance(meal_type, str):
        raise ValidationError("Meal type is required.")
    
    valid_meal_types = ["breakfast", "lunch", "dinner", "snack", "other"]
    if meal_type.lower() not in valid_meal_types:
        raise ValidationError(f"Invalid meal type. Choose from: {', '.join(valid_meal_types)}")
    
    # Validate macros
    def validate_macro(value: str, macro_name: str, max_value: float = 2000) -> float:
        try:
            macro_val = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{macro_name} must be a valid number.")
        
        if macro_val < 0:
            raise ValidationError(f"{macro_name} cannot be negative.")
        
        if macro_val > max_value:
            raise ValidationError(f"{macro_name} exceeds reasonable maximum ({max_value}g). Please verify.")
        
        return macro_val
    
    calories_val = validate_macro(calories, "Calories", max_value=5000)
    protein_val = validate_macro(protein, "Protein", max_value=500)
    carbs_val = validate_macro(carbs, "Carbohydrates", max_value=500)
    fat_val = validate_macro(fat, "Fat", max_value=500)
    
    # Validate meal date
    try:
        meal_date_obj = datetime.strptime(meal_date.strip(), "%Y-%m-%d")
        # Don't allow future dates
        if meal_date_obj > datetime.utcnow():
            raise ValidationError("Meal date cannot be in the future.")
    except ValueError:
        raise ValidationError("Meal date must be in YYYY-MM-DD format.")
    
    # Basic region validation if provided
    if region:
        region = region.strip()
        if len(region) > 50:
            raise ValidationError("Region name is too long.")
    
    return {
        "meal_type": meal_type.lower(),
        "calories": calories_val,
        "protein": protein_val,
        "carbs": carbs_val,
        "fat": fat_val,
        "meal_date": meal_date.strip(),
        "region": region,
        "created_at": datetime.utcnow().isoformat(),
    }


def validate_insurance_profile(patient_name: str, policy_number: str, provider: str, 
                              policy_type: str, coverage_limit: str) -> dict[str, Any]:
    """
    Validate and normalize insurance profile input.
    
    Args:
        patient_name: Patient name
        policy_number: Insurance policy number
        provider: Insurance provider name
        policy_type: Type of policy (e.g., 'Individual', 'Family')
        coverage_limit: Coverage limit in numeric format
        
    Returns:
        Dictionary with validated insurance profile fields
        
    Raises:
        ValidationError: If input is invalid
    """
    # Validate patient name
    if not patient_name or not isinstance(patient_name, str):
        raise ValidationError("Patient name is required.")
    
    clean_name = patient_name.strip()
    if not clean_name or len(clean_name) < 2:
        raise ValidationError("Patient name must be at least 2 characters.")
    
    if not re.match(r"^[a-zA-Z\s\-'.]+$", clean_name):
        raise ValidationError("Patient name contains invalid characters.")
    
    # Validate policy number
    if not policy_number or not isinstance(policy_number, str):
        raise ValidationError("Policy number is required.")
    
    clean_policy = policy_number.strip()
    if not clean_policy or len(clean_policy) < 3:
        raise ValidationError("Policy number must be at least 3 characters.")
    
    if len(clean_policy) > 50:
        raise ValidationError("Policy number is too long.")
    
    # Validate provider
    if not provider or not isinstance(provider, str):
        raise ValidationError("Insurance provider name is required.")
    
    clean_provider = provider.strip()
    if len(clean_provider) < 2 or len(clean_provider) > 100:
        raise ValidationError("Provider name must be between 2 and 100 characters.")
    
    # Validate policy type
    valid_policy_types = ["Individual", "Family", "Senior Citizen", "Group", "Other"]
    if policy_type not in valid_policy_types:
        raise ValidationError(f"Invalid policy type. Choose from: {', '.join(valid_policy_types)}")
    
    # Validate coverage limit
    try:
        coverage_limit_val = float(coverage_limit)
    except (ValueError, TypeError):
        raise ValidationError("Coverage limit must be a valid number.")
    
    if coverage_limit_val <= 0:
        raise ValidationError("Coverage limit must be greater than zero.")
    
    if coverage_limit_val > 100000000:  # Reasonable upper bound
        raise ValidationError("Coverage limit exceeds reasonable maximum.")
    
    return {
        "patient_name": clean_name,
        "policy_number": clean_policy,
        "provider": clean_provider,
        "policy_type": policy_type,
        "coverage_limit": coverage_limit_val,
        "updated_at": datetime.utcnow().isoformat(),
    }


def validate_health_goal(goal_name: str, target_value: str, deadline: str, metric_unit: str) -> dict[str, Any]:
    """
    Validate and normalize health goal input.
    
    Args:
        goal_name: Name of the health goal
        target_value: Target value to achieve
        deadline: Deadline date (YYYY-MM-DD)
        metric_unit: Unit of measurement
        
    Returns:
        Dictionary with validated health goal fields
        
    Raises:
        ValidationError: If input is invalid
    """
    # Validate goal name
    if not goal_name or not isinstance(goal_name, str):
        raise ValidationError("Goal name is required.")
    
    clean_goal = goal_name.strip()
    if not clean_goal or len(clean_goal) < 3:
        raise ValidationError("Goal name must be at least 3 characters.")
    
    if len(clean_goal) > 150:
        raise ValidationError("Goal name is too long.")
    
    # Validate target value
    try:
        target_val = float(target_value)
    except (ValueError, TypeError):
        raise ValidationError("Target value must be a valid number.")
    
    if target_val < 0:
        raise ValidationError("Target value cannot be negative.")
    
    # Validate deadline
    try:
        deadline_obj = datetime.strptime(deadline.strip(), "%Y-%m-%d")
        if deadline_obj <= datetime.utcnow():
            raise ValidationError("Deadline must be in the future.")
    except ValueError:
        raise ValidationError("Deadline must be in YYYY-MM-DD format and in the future.")
    
    # Validate metric unit
    if not metric_unit or not isinstance(metric_unit, str):
        raise ValidationError("Metric unit is required.")
    
    clean_unit = metric_unit.strip()
    if not clean_unit:
        raise ValidationError("Metric unit cannot be empty.")
    
    return {
        "goal_name": clean_goal,
        "target_value": target_val,
        "deadline": deadline.strip(),
        "metric_unit": clean_unit,
        "created_at": datetime.utcnow().isoformat(),
    }


def validate_medical_history(condition: str, diagnosis_date: str, treatment: str = "") -> dict[str, Any]:
    """
    Validate and normalize medical history record input.
    
    Args:
        condition: Medical condition or diagnosis
        diagnosis_date: Date of diagnosis (YYYY-MM-DD)
        treatment: Treatment or notes (optional)
        
    Returns:
        Dictionary with validated medical history fields
        
    Raises:
        ValidationError: If input is invalid
    """
    # Validate condition
    if not condition or not isinstance(condition, str):
        raise ValidationError("Medical condition is required.")
    
    clean_condition = condition.strip()
    if not clean_condition or len(clean_condition) < 2:
        raise ValidationError("Condition description must be at least 2 characters.")
    
    if len(clean_condition) > 200:
        raise ValidationError("Condition description is too long.")
    
    # Validate diagnosis date
    try:
        diag_date_obj = datetime.strptime(diagnosis_date.strip(), "%Y-%m-%d")
        if diag_date_obj > datetime.utcnow():
            raise ValidationError("Diagnosis date cannot be in the future.")
    except ValueError:
        raise ValidationError("Diagnosis date must be in YYYY-MM-DD format and not in the future.")
    
    # Validate treatment (optional)
    clean_treatment = ""
    if treatment:
        clean_treatment = treatment.strip()
        if len(clean_treatment) > 500:
            raise ValidationError("Treatment notes are too long.")
    
    return {
        "condition": clean_condition,
        "diagnosis_date": diagnosis_date.strip(),
        "treatment": clean_treatment,
        "created_at": datetime.utcnow().isoformat(),
    }


def validate_regional_preference(region: str, preferred_language: str, preferred_doctor_type: str = "") -> dict[str, Any]:
    """
    Validate and normalize regional preference input.
    
    Args:
        region: Region or state name
        preferred_language: Preferred language (e.g., 'Hindi', 'English', 'Tamil')
        preferred_doctor_type: Preferred doctor specialty (optional)
        
    Returns:
        Dictionary with validated regional preference fields
        
    Raises:
        ValidationError: If input is invalid
    """
    # Validate region
    if not region or not isinstance(region, str):
        raise ValidationError("Region is required.")
    
    clean_region = region.strip()
    if not clean_region or len(clean_region) < 2:
        raise ValidationError("Region name must be at least 2 characters.")
    
    if len(clean_region) > 100:
        raise ValidationError("Region name is too long.")
    
    # Validate language
    if not preferred_language or not isinstance(preferred_language, str):
        raise ValidationError("Preferred language is required.")
    
    clean_language = preferred_language.strip()
    valid_languages = {"Hindi", "English", "Tamil", "Telugu", "Kannada", "Malayalam", "Bengali", "Marathi", "Gujarati", "Punjabi", "Other"}
    if clean_language not in valid_languages:
        raise ValidationError(
            f"Invalid language. Choose from: {', '.join(sorted(valid_languages))}"
        )
    
    # Validate doctor type (optional)
    clean_doctor_type = ""
    if preferred_doctor_type:
        clean_doctor_type = preferred_doctor_type.strip()
        valid_specialties = {"General Practice", "Ayurveda", "Cardiology", "Endocrinology", "Neurology", "Other"}
        if clean_doctor_type not in valid_specialties:
            # Allow custom specialties but don't fail
            if len(clean_doctor_type) > 100:
                raise ValidationError("Doctor specialty is too long.")
    
    return {
        "region": clean_region,
        "preferred_language": clean_language,
        "preferred_doctor_type": clean_doctor_type,
        "updated_at": datetime.utcnow().isoformat(),
    }
