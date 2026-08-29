import difflib
import re
from typing import Any

from .config import (
    get_google_api_key,
    get_groq_api_key,
    get_llm_provider,
    get_openai_api_key,
    get_use_llm,
)

COMMON_MEDICATION_USES: dict[str, str] = {
    "prednisolone": (
        "Prednisolone is a corticosteroid used to reduce inflammation and suppress immune reactions. "
        "Doctors may prescribe it for asthma flare-ups, allergic reactions, autoimmune conditions, and other inflammatory disorders. "
        "It should be used only as prescribed because it can cause side effects such as increased blood sugar, mood changes, and stomach irritation."
    ),
    "prednisone": (
        "Prednisone is a corticosteroid used to reduce inflammation and immune activity. "
        "It is commonly prescribed for asthma, severe allergies, autoimmune conditions, and some inflammatory illnesses. "
        "Use it only under medical supervision because it can have significant side effects."
    ),
    "paracetamol": (
        "Paracetamol is used to relieve mild to moderate pain and reduce fever. "
        "It does not treat the underlying cause of symptoms, and the dose should stay within the recommended daily limit."
    ),
    "ibuprofen": (
        "Ibuprofen is a nonsteroidal anti-inflammatory medicine used for pain, fever, and inflammation. "
        "It can irritate the stomach and may not be suitable for everyone, especially people with kidney disease or ulcers."
    ),
}


class HealthChatbot:
    def __init__(
        self,
        provider: str | None = None,
        groq_api_key: str | None = None,
        openai_api_key: str | None = None,
        google_api_key: str | None = None,
        use_llm: bool | None = None,
    ) -> None:
        self._graph = None
        provider_name = (provider or get_llm_provider()).lower()
        groq_key = groq_api_key if groq_api_key is not None else get_groq_api_key()
        openai_key = openai_api_key if openai_api_key is not None else get_openai_api_key()
        google_key = google_api_key if google_api_key is not None else get_google_api_key()

        if use_llm is None:
            use_llm = get_use_llm() or bool(groq_key or openai_key or google_key)

        if use_llm:
            try:
                from langchain.agents import create_agent
                
                # Import all our tools
                from .agent_tools import (
                    search_health_records,
                    get_user_medications,
                    schedule_new_medication,
                    get_health_metrics,
                    log_new_health_metric,
                    get_health_goals,
                    add_new_health_goal,
                    get_nutrition_logs,
                    log_nutrition,
                    get_insurance_profile,
                    add_insurance_profile,
                    get_medical_history,
                    add_medical_history,
                    get_regional_preferences,
                    add_regional_preferences,
                    check_medication_interactions,
                    search_indian_medications,
                    search_local_doctors,
                    lookup_ayurvedic_remedies,
                    lookup_general_medical_info,
                )

                tools = [
                    search_health_records,
                    get_user_medications,
                    schedule_new_medication,
                    get_health_metrics,
                    log_new_health_metric,
                    get_health_goals,
                    add_new_health_goal,
                    get_nutrition_logs,
                    log_nutrition,
                    get_insurance_profile,
                    add_insurance_profile,
                    get_medical_history,
                    add_medical_history,
                    get_regional_preferences,
                    add_regional_preferences,
                    check_medication_interactions,
                    search_indian_medications,
                    search_local_doctors,
                    lookup_ayurvedic_remedies,
                    lookup_general_medical_info,
                ]

                model = None
                if groq_key:
                    from langchain_groq import ChatGroq
                    # Use a Groq model in this environment that supports tool calling
                    model = ChatGroq(
                        model="openai/gpt-oss-120b",
                        api_key=groq_key,
                        temperature=0.2,
                    )
                elif provider_name == "google" and google_key:
                    from langchain_google_genai import ChatGoogleGenerativeAI
                    model = ChatGoogleGenerativeAI(
                        model="gemini-1.5-flash",
                        google_api_key=google_key,
                        temperature=0.2,
                    )
                elif provider_name == "openai" and openai_key:
                    from langchain_openai import ChatOpenAI
                    model = ChatOpenAI(model="gpt-4o-mini", api_key=openai_key, temperature=0.2)

                if model is not None:
                    # Create compiled agent graph
                    self._graph = create_agent(model=model, tools=tools)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to initialize Agent: {str(e)}")
                self._graph = None

    def _match_medication(self, query: str) -> str | None:
        text = query.lower()
        candidate_text = re.sub(r"[^a-z0-9\s]", " ", text)

        for medication_name, description in COMMON_MEDICATION_USES.items():
            if medication_name in candidate_text:
                return description

        words = [word for word in candidate_text.split() if len(word) > 3]
        if not words:
            return None

        for word in words:
            close_match = difflib.get_close_matches(word, COMMON_MEDICATION_USES.keys(), n=1, cutoff=0.84)
            if close_match:
                return COMMON_MEDICATION_USES[close_match[0]]

        return None

    def answer(self, query: str) -> str:
        text = query.strip().lower()
        if not text:
            return "Please type a health-related question."

        # Execute dynamic agent loop if initialized
        if self._graph is not None:
            try:
                # 1. Fetch dynamic patient overview summary
                from .rag import get_patient_summary_string
                patient_summary = get_patient_summary_string()

                # 2. Reconstruct chat history from Streamlit session state
                chat_history = []
                try:
                    import streamlit as st
                    if "chat_history" in st.session_state:
                        history_raw = st.session_state.chat_history
                        # Exclude current query if it was already appended
                        if history_raw and history_raw[-1]["content"] == query:
                            history_raw = history_raw[:-1]
                        
                        from langchain_core.messages import AIMessage, HumanMessage
                        for entry in history_raw:
                            if entry.get("role") == "user":
                                chat_history.append(HumanMessage(content=entry["content"]))
                            else:
                                chat_history.append(AIMessage(content=entry["content"]))
                except Exception:
                    pass

                # 3. Formulate system prompt dynamically
                from langchain_core.messages import SystemMessage, HumanMessage
                system_prompt_text = (
                    "You are a professional, helpful, and safe healthcare assistant AI Agent.\n"
                    "You have direct access to the patient's MongoDB database records through tools.\n\n"
                    "CRITICAL OPERATIONAL RULES:\n"
                    "1. When asked about patient records (e.g. medications, metrics, goals, diet logs, history), ALWAYS call the corresponding query tools first (e.g. `get_user_medications`, `get_health_metrics`, or database RAG search `search_health_records`) to obtain accurate, factual information before responding. Do not guess or hallucinate records.\n"
                    "2. When asked to schedule a medication, log a metric, set a goal, or add history/diet/insurance logs, call the appropriate database action tool and confirm when completed successfully.\n"
                    "3. Keep your explanations concise, professional, and non-diagnostic. Recommend consulting a licensed medical professional for diagnoses and emergencies.\n"
                    "4. Use the patient summary context below to tailor your guidance (e.g. diet restrictions, location, language preferences).\n\n"
                    f"Patient Current Status Overview:\n{patient_summary}"
                )

                messages = [SystemMessage(content=system_prompt_text)]
                messages.extend(chat_history)
                messages.append(HumanMessage(content=query))

                # 4. Invoke agent graph
                response = self._graph.invoke({"messages": messages})
                return str(response["messages"][-1].content)
            except Exception as e:
                # Log error and fall back to rule-based logic
                import logging
                logging.getLogger(__name__).warning(f"Agent execution failed, falling back to rule-based: {str(e)}")

        # Fallback rule-based matching
        medication_answer = self._match_medication(text)
        if medication_answer is not None:
            return medication_answer

        if "medication" in text or "medicine" in text or "used for" in text or "what is" in text:
            return "You can add medicine name, dosage, and schedule in the Medication Scheduler tab."
        if "steps" in text or "fitness" in text or "exercise" in text:
            return "Track daily steps and compare trends in Health Metrics to monitor activity."
        if "fever" in text or "cold" in text:
            return "For mild symptoms, rest and hydration can help. If symptoms worsen, consult a doctor."

        return "I can help with medication reminders, health metric logging, and basic wellness guidance."
