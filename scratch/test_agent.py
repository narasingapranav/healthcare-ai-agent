import os
import sys
from datetime import datetime

# Add the root directory to path to ensure relative imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import (
    init_db,
    add_health_metric,
    add_medication,
    add_health_goal,
    add_medical_history_record,
    list_medications,
    list_all_metrics,
)
from src.rag import DatabaseRAG, get_patient_summary_string
from src.chatbot import HealthChatbot


def test_rag_and_agent():
    print("Initializing Database...")
    try:
        init_db()
    except Exception as e:
        print(f"MongoDB not running or failed to initialize: {e}")
        print("Note: RAG and tools can still fall back, but MongoDB is recommended.")

    print("\nAdding test data to MongoDB...")
    try:
        # Add a medication
        add_medication("Paracetamol", "500mg", "08:00", "Take after breakfast")
        add_medication("Aspirin", "75mg", "20:00", "For heart health")
        
        # Add a metric
        add_health_metric("blood_pressure", 120.0, "mmHg", datetime.utcnow().isoformat())
        add_health_metric("steps", 8432.0, "steps", datetime.utcnow().isoformat())
        
        # Add a goal
        add_health_goal("steps", 10000.0, "steps")
        
        # Add medical history
        add_medical_history_record(
            patient_name="John Doe",
            condition_name="Mild Hypertension",
            diagnosis_date="2025-06-10",
            medications="Aspirin",
            allergies="Pollen",
            procedures_done="None",
            notes="Keep monitoring blood pressure daily."
        )
        print("Test data inserted successfully.")
    except Exception as e:
        print(f"Failed to insert test data: {e}")

    print("\nTesting DatabaseRAG fetch and serialization...")
    rag = DatabaseRAG()
    all_docs = rag.fetch_all_documents()
    print(f"Fetched {len(all_docs)} documents from database.")
    for i, doc in enumerate(all_docs[:5]):
        print(f"  Doc {i+1} [{doc.metadata.get('type')}]: {doc.page_content[:100]}...")

    print("\nTesting DatabaseRAG search...")
    query = "blood pressure"
    search_results = rag.search(query, k=3)
    print(f"Search results for query '{query}':")
    for i, doc in enumerate(search_results):
        print(f"  Result {i+1} [{doc.metadata.get('type')}]: {doc.page_content}")

    print("\nTesting Patient Summary Generation...")
    summary = get_patient_summary_string()
    print("Patient Summary:\n" + "="*40)
    print(summary)
    print("="*40)

    print("\nTesting Chatbot Class Instantiation...")
    # Instantiate with USE_LLM=False to verify rules-based fallback compilation
    chatbot_rules = HealthChatbot(use_llm=False)
    resp = chatbot_rules.answer("What is Aspirin used for?")
    print(f"Rules-based response: {resp}")

    # Instantiate with live config to check compilation
    chatbot_agent = HealthChatbot()
    if chatbot_agent._graph is not None:
        print("Agent Graph successfully initialized.")
    else:
        print("Agent Graph in fallback/inactive mode (no active API key).")

    print("\nAll Backend Tests Completed!")


if __name__ == "__main__":
    test_rag_and_agent()
