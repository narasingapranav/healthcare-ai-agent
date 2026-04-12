from typing import Any


def get_medical_info(topic: str) -> dict[str, Any]:
    key = topic.strip().lower()
    if not key:
        return {
            "title": "",
            "summary": "",
            "guidance": [],
            "citations": [],
        }

    knowledge: dict[str, dict[str, Any]] = {
        "hypertension": {
            "title": "Hypertension (High Blood Pressure)",
            "summary": "Hypertension is persistently elevated blood pressure and is a major risk factor for heart, brain, and kidney disease.",
            "guidance": [
                "Monitor blood pressure regularly and record trends.",
                "Reduce sodium intake and follow a balanced diet.",
                "Seek clinician guidance for sustained readings above target.",
            ],
            "citations": [
                "WHO: Hypertension - https://www.who.int/news-room/fact-sheets/detail/hypertension",
                "CDC: About High Blood Pressure - https://www.cdc.gov/high-blood-pressure/about/index.html",
            ],
        },
        "diabetes": {
            "title": "Diabetes Mellitus",
            "summary": "Diabetes is a chronic condition where blood glucose levels are high due to insulin deficiency, resistance, or both.",
            "guidance": [
                "Track glucose, diet, physical activity, and medication adherence.",
                "Schedule periodic HbA1c and complication screening.",
                "Consult a doctor for personalized targets and medication plans.",
            ],
            "citations": [
                "WHO: Diabetes - https://www.who.int/news-room/fact-sheets/detail/diabetes",
                "NIDDK: Diabetes Overview - https://www.niddk.nih.gov/health-information/diabetes/overview/what-is-diabetes",
            ],
        },
        "fever": {
            "title": "Fever",
            "summary": "Fever is usually a symptom of infection or inflammation. Persistent high fever needs clinical evaluation.",
            "guidance": [
                "Stay hydrated and monitor temperature over time.",
                "Watch for red flags like breathing difficulty, confusion, or persistent high fever.",
                "Seek medical care promptly for severe symptoms.",
            ],
            "citations": [
                "NHS: High temperature (fever) - https://www.nhs.uk/conditions/fever-in-adults/",
                "Mayo Clinic: Fever - https://www.mayoclinic.org/diseases-conditions/fever/symptoms-causes/syc-20352759",
            ],
        },
        "heart health": {
            "title": "Heart Health",
            "summary": "Heart health improves with physical activity, nutrition quality, blood pressure control, and avoiding tobacco use.",
            "guidance": [
                "Aim for regular physical activity each week.",
                "Prefer high-fiber foods and reduce trans fat intake.",
                "Track blood pressure, weight, and resting heart rate.",
            ],
            "citations": [
                "American Heart Association: Life's Essential 8 - https://www.heart.org/en/healthy-living/healthy-lifestyle/lifes-essential-8",
                "WHO: Cardiovascular diseases - https://www.who.int/health-topics/cardiovascular-diseases",
            ],
        },
    }

    for known_key, value in knowledge.items():
        if known_key in key or key in known_key:
            return value

    return {
        "title": topic.strip().title(),
        "summary": "No curated summary found for this topic in the local knowledge base.",
        "guidance": [
            "Use trusted medical sources for reference.",
            "Consult a licensed clinician for diagnosis and treatment decisions.",
        ],
        "citations": [
            "WHO health topics - https://www.who.int/health-topics",
            "CDC health topics - https://www.cdc.gov/",
        ],
    }
