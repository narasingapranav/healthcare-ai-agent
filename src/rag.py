import re
import math
from collections import Counter
from typing import Any, List
from langchain_core.documents import Document

from .database import (
    list_medications,
    list_all_metrics,
    list_health_goals,
    list_indian_medications,
    list_nutrition_logs,
    list_insurance_profiles,
    list_medical_history,
    list_regional_preferences,
)
from .config import get_google_api_key, get_openai_api_key, get_llm_provider


def get_cosine_similarity(text1: str, text2: str) -> float:
    """Calculate basic cosine similarity of word frequencies between two texts."""
    words1 = Counter(re.findall(r"\w+", text1.lower()))
    words2 = Counter(re.findall(r"\w+", text2.lower()))
    
    intersection = set(words1.keys()) & set(words2.keys())
    numerator = sum([words1[x] * words2[x] for x in intersection])
    
    sum1 = sum([words1[x] ** 2 for x in words1.keys()])
    sum2 = sum([words2[x] ** 2 for x in words2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
    if not denominator:
        return 0.0
    return float(numerator) / denominator


class DatabaseRAG:
    @staticmethod
    def serialize_record(record_type: str, doc: dict) -> str:
        """Convert a database record into a clean, searchable paragraph."""
        if record_type == "medication":
            active_str = "Active" if doc.get("active") else "Inactive"
            return (
                f"Medication: {doc.get('name')}. Dosage: {doc.get('dosage')}. "
                f"Schedule: {doc.get('schedule_time')}. Notes: {doc.get('notes') or 'None'}. "
                f"Status: {active_str}."
            )
        elif record_type == "metric":
            return (
                f"Health Metric Log: {doc.get('metric_name')} = {doc.get('metric_value')} {doc.get('unit')}. "
                f"Recorded at: {doc.get('recorded_at')}."
            )
        elif record_type == "goal":
            active_str = "Active" if doc.get("active") else "Completed/Inactive"
            return (
                f"Health Goal: Target {doc.get('metric_name')} of {doc.get('target_value')} {doc.get('unit')}. "
                f"Status: {active_str}."
            )
        elif record_type == "nutrition":
            return (
                f"Nutrition Log: Date: {doc.get('meal_date')}, Meal: {doc.get('meal_type')}, "
                f"Food: {doc.get('food_item')}, Quantity: {doc.get('quantity')}, "
                f"Nutrients: Calories: {doc.get('calories', 0)} kcal, Protein: {doc.get('protein_g', 0)}g, "
                f"Carbs: {doc.get('carbs_g', 0)}g, Fats: {doc.get('fats_g', 0)}g, Fiber: {doc.get('fiber_g', 0)}g. "
                f"Notes: {doc.get('notes') or 'None'}."
            )
        elif record_type == "insurance":
            return (
                f"Insurance Profile: Patient: {doc.get('patient_name')}, Insurer: {doc.get('insurer')}, "
                f"Policy: {doc.get('policy_number')} ({doc.get('policy_type')}), "
                f"Sum Insured: {doc.get('sum_insured')} INR, Expiration: {doc.get('expiry_date')}. "
                f"Network Hospitals: {doc.get('network_hospitals') or 'None'}."
            )
        elif record_type == "history":
            return (
                f"Medical History: Patient: {doc.get('patient_name')}, Condition: {doc.get('condition_name')}, "
                f"Diagnosed: {doc.get('diagnosis_date')}. Medications Prescribed: {doc.get('medications') or 'None'}. "
                f"Allergies: {doc.get('allergies') or 'None'}. Procedures Done: {doc.get('procedures_done') or 'None'}. "
                f"Notes: {doc.get('notes') or 'None'}."
            )
        elif record_type == "preference":
            return (
                f"Patient Regional Preferences: Patient: {doc.get('patient_name')}, "
                f"Location: {doc.get('city')}, {doc.get('state')}. Language: {doc.get('preferred_language')}. "
                f"Diet: {doc.get('diet_preference')}. Mode: {doc.get('consultation_mode')}. "
                f"Budget: Up to {doc.get('max_budget_inr')} INR. Preferred Specialties: {doc.get('preferred_specialties')}."
            )
        elif record_type == "indian_medication":
            return (
                f"Indian Medication Database: Name: {doc.get('name')}. Manufacturer: {doc.get('manufacturer') or 'Unknown'}. "
                f"Price: {doc.get('price_inr') or 'N/A'} INR. Uses: {doc.get('uses')}. Source: {doc.get('source')}."
            )
        return str(doc)

    def fetch_all_documents(self) -> List[Document]:
        """Fetch all database records across collections and wrap them as LangChain Documents."""
        documents = []
        try:
            # 1. Medications
            for med in list_medications(active_only=False):
                documents.append(
                    Document(
                        page_content=self.serialize_record("medication", med),
                        metadata={"type": "medication", "id": med.get("id")},
                    )
                )

            # 2. Metrics
            for metric in list_all_metrics():
                documents.append(
                    Document(
                        page_content=self.serialize_record("metric", metric),
                        metadata={"type": "metric"},
                    )
                )

            # 3. Health Goals
            for goal in list_health_goals(active_only=False):
                documents.append(
                    Document(
                        page_content=self.serialize_record("goal", goal),
                        metadata={"type": "goal", "id": goal.get("id")},
                    )
                )

            # 4. Nutrition Logs
            for nutr in list_nutrition_logs(limit=200):
                documents.append(
                    Document(
                        page_content=self.serialize_record("nutrition", nutr),
                        metadata={"type": "nutrition", "id": nutr.get("id")},
                    )
                )

            # 5. Insurance Profiles
            for ins in list_insurance_profiles(limit=50):
                documents.append(
                    Document(
                        page_content=self.serialize_record("insurance", ins),
                        metadata={"type": "insurance", "id": ins.get("id")},
                    )
                )

            # 6. Medical History Records
            for hist in list_medical_history(limit=100):
                documents.append(
                    Document(
                        page_content=self.serialize_record("history", hist),
                        metadata={"type": "history", "id": hist.get("id")},
                    )
                )

            # 7. Regional Preferences
            for pref in list_regional_preferences(limit=50):
                documents.append(
                    Document(
                        page_content=self.serialize_record("preference", pref),
                        metadata={"type": "preference", "id": pref.get("id")},
                    )
                )

            # 8. Indian Medication Records
            for ind_med in list_indian_medications(limit=100):
                documents.append(
                    Document(
                        page_content=self.serialize_record("indian_medication", ind_med),
                        metadata={"type": "indian_medication", "id": ind_med.get("id")},
                    )
                )

        except Exception as e:
            # If DB is not ready or connection fails, return empty list safely
            import logging
            logging.getLogger(__name__).error(f"Error fetching RAG documents: {str(e)}")
            
        return documents

    def search(self, query: str, k: int = 5) -> List[Document]:
        """Perform similarity search over the entire database content.

        Utilizes embedding-based InMemoryVectorStore if credentials are set,
        otherwise falls back to custom keyword cosine-similarity matching.
        """
        documents = self.fetch_all_documents()
        if not documents:
            return []

        provider = get_llm_provider().lower()
        openai_key = get_openai_api_key()
        google_key = get_google_api_key()

        # Attempt to use embedding-based RAG if keys are configured
        if provider == "openai" and openai_key:
            try:
                from langchain_openai import OpenAIEmbeddings
                from langchain_core.vectorstores import InMemoryVectorStore
                embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_key)
                vectorstore = InMemoryVectorStore.from_documents(documents, embeddings)
                return vectorstore.similarity_search(query, k=k)
            except Exception:
                pass  # Fall back to local search if import or runtime error occurs

        elif provider == "google" and google_key:
            try:
                from langchain_google_genai import GoogleGenAIEmbeddings
                from langchain_core.vectorstores import InMemoryVectorStore
                embeddings = GoogleGenAIEmbeddings(model="models/embedding-001", google_api_key=google_key)
                vectorstore = InMemoryVectorStore.from_documents(documents, embeddings)
                return vectorstore.similarity_search(query, k=k)
            except Exception:
                pass  # Fall back to local search

        # Fallback keyword-based similarity matching (robust, works offline/without embeddings API)
        scored_docs = []
        for doc in documents:
            score = get_cosine_similarity(query, doc.page_content)
            if score > 0:
                scored_docs.append((score, doc))
        
        # Sort by score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        results = [doc for score, doc in scored_docs[:k]]
        
        # If no similarity matches, return the most recent active schedules/history documents as default context
        if not results:
            results = [doc for doc in documents if doc.metadata.get("type") in ("medication", "goal", "history")][:k]
            
        return results


def get_patient_summary_string() -> str:
    """Generate a quick text overview of the patient state for system prompt injection."""
    try:
        active_meds = list_medications(active_only=True)
        active_goals = list_health_goals(active_only=True)
        metrics = list_recent_metrics_raw(limit=5)
        history = list_medical_history(limit=2)
        pref = list_regional_preferences(limit=1)

        summary_parts = []
        
        # Patient identity & location
        if pref:
            p = pref[0]
            summary_parts.append(
                f"Patient Name: {p.get('patient_name')}, Location: {p.get('city')}, {p.get('state')}, "
                f"Preferred Language: {p.get('preferred_language')}, Diet: {p.get('diet_preference')}."
            )
        else:
            summary_parts.append("Patient Name: Unknown/General.")

        # Medical Conditions
        if history:
            conds = [h.get("condition_name") for h in history if h.get("condition_name")]
            summary_parts.append(f"Known Conditions: {', '.join(conds)}.")

        # Medications
        if active_meds:
            meds_list = [f"{m['name']} ({m['dosage']} at {m['schedule_time']})" for m in active_meds]
            summary_parts.append(f"Active Medications: {', '.join(meds_list)}.")
        else:
            summary_parts.append("Active Medications: None scheduled.")

        # Goals
        if active_goals:
            goals_list = [f"Target {g['metric_name']}: {g['target_value']} {g['unit']}" for g in active_goals]
            summary_parts.append(f"Active Goals: {', '.join(goals_list)}.")
        else:
            summary_parts.append("Active Goals: None set.")

        # Recent Metrics
        if metrics:
            mets_list = [f"{m.get('metric_name')}={m.get('metric_value')}{m.get('unit')} ({m.get('recorded_at')})" for m in metrics]
            summary_parts.append(f"Recent Metrics: {', '.join(mets_list)}.")
        
        return "\n".join(summary_parts)
    except Exception:
        return "Patient Status: Database connection inactive or empty patient profile."


def list_recent_metrics_raw(limit: int = 5) -> list:
    """Helper to get recent metrics with unit, internal connection to DB."""
    try:
        from .database import _metrics_collection
        from pymongo import DESCENDING
        cursor = _metrics_collection().find({}).sort("recorded_at_dt", DESCENDING).limit(limit)
        return list(cursor)
    except Exception:
        return []
