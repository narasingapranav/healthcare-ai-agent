import difflib
import re

from .config import get_google_api_key, get_groq_api_key, get_llm_provider, get_openai_api_key, get_use_llm


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
        self._chain = None
        provider_name = (provider or get_llm_provider()).lower()
        groq_key = groq_api_key if groq_api_key is not None else get_groq_api_key()
        openai_key = openai_api_key if openai_api_key is not None else get_openai_api_key()
        google_key = google_api_key if google_api_key is not None else get_google_api_key()

        if use_llm is None:
            use_llm = get_use_llm() or bool(groq_key or openai_key or google_key)

        if use_llm:
            try:
                from langchain_core.prompts import ChatPromptTemplate

                model = None
                if groq_key:
                    from langchain_groq import ChatGroq

                    model = ChatGroq(
                        model="llama-3.3-70b-versatile",
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

                if model is None:
                    return

                prompt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            "You are a healthcare assistant. Give short, safe, non-diagnostic guidance and suggest consulting a doctor for emergencies.",
                        ),
                        ("human", "{query}"),
                    ]
                )
                self._chain = prompt | model
            except Exception:
                self._chain = None

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

        if self._chain is not None:
            try:
                response = self._chain.invoke({"query": query})
                return str(response.content)
            except Exception:
                pass

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
