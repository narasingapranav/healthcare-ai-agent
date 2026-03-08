# Healthcare Monitoring AI Agent - Track A (Week 1)

This repo implements **Track A** for the Healthcare Monitoring AI Agent project and covers the first-week deliverables.

## What is completed (Week 1 scope)

- Project structure with Python + Streamlit + pandas + LangChain dependencies
- Basic health chatbot (safe, non-diagnostic guidance)
- Medication scheduler with reminder alerts
- Health metrics parser and storage
- MongoDB database for medication and health metrics

## Project structure

- `app.py` - Streamlit dashboard
- `src/database.py` - MongoDB collections and CRUD helpers
- `src/health_parser.py` - metric input parsing and validation
- `src/medication.py` - reminder logic
- `src/chatbot.py` - chatbot with optional LangChain/OpenAI
- `requirements.txt` - dependencies

## Setup

1. Create and activate a virtual environment (recommended).
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Optional LLM setup:

```powershell
copy .env.example .env
```

Set in `.env`:

- `USE_LLM=true`
- `OPENAI_API_KEY=your_key_here`
- `MONGODB_URI=mongodb://localhost:27017`
- `MONGODB_DB_NAME=healthcare_agent`

If not set, chatbot uses built-in fallback responses.

4. Ensure MongoDB is running locally (or use a MongoDB Atlas URI).

## Run

```powershell
streamlit run app.py
```

## Week 1 demo flow

1. Add 2-3 medications with schedule times.
2. Add health metrics (steps, heart rate, weight).
3. Open Health Chat and ask simple health questions.
4. Show reminders and metric trend chart.

## Next for Week 2

- Add health data API integration (Google Fit/Fitbit mock or real)
- Add medication adherence % summary
- Deploy to Streamlit Cloud
- Record 2-minute demo video
