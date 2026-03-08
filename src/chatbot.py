from .config import GOOGLE_API_KEY, GROQ_API_KEY, LLM_PROVIDER, OPENAI_API_KEY, USE_LLM


class HealthChatbot:
    def __init__(self) -> None:
        self._chain = None
        if USE_LLM:
            try:
                from langchain_core.prompts import ChatPromptTemplate

                model = None
                if LLM_PROVIDER == "groq" and GROQ_API_KEY:
                    from langchain_groq import ChatGroq

                    model = ChatGroq(
                        model="llama-3.3-70b-versatile",
                        api_key=GROQ_API_KEY,
                        temperature=0.2,
                    )
                elif LLM_PROVIDER == "google" and GOOGLE_API_KEY:
                    from langchain_google_genai import ChatGoogleGenerativeAI

                    model = ChatGoogleGenerativeAI(
                        model="gemini-1.5-flash",
                        google_api_key=GOOGLE_API_KEY,
                        temperature=0.2,
                    )
                elif LLM_PROVIDER == "openai" and OPENAI_API_KEY:
                    from langchain_openai import ChatOpenAI

                    model = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0.2)

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

        if "medication" in text or "medicine" in text:
            return "You can add medicine name, dosage, and schedule in the Medication Scheduler tab."
        if "steps" in text or "fitness" in text or "exercise" in text:
            return "Track daily steps and compare trends in Health Metrics to monitor activity."
        if "fever" in text or "cold" in text:
            return "For mild symptoms, rest and hydration can help. If symptoms worsen, consult a doctor."

        return "I can help with medication reminders, health metric logging, and basic wellness guidance."
