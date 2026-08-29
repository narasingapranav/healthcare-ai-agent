# Healthcare AI Agent

A Streamlit-based healthcare assistant for tracking daily health, medications, and wellness goals. The app combines a patient dashboard, natural-language assistant, MongoDB records, and India-specific health utilities such as local doctor lookup, dietary recommendations, and Ayurvedic remedies.

This project is designed to help users log health data, monitor medication schedules, review health trends, and ask conversational questions about their personal health records.

## Overview

The application includes:

- Health metric tracking for steps, heart rate, weight, sleep, water intake, and similar values
- Medication scheduling and completion tracking
- Health goal management with goal lists and status tracking
- Nutrition and meal logging
- Insurance profile records
- Medical history entry and retrieval
- Regional preference and doctor matching workflows
- AI-assisted health questions using LangChain-compatible LLM providers
- CSV, JSON, and XML import/export for health metrics

## Features

### Dashboard and health tracking

- Main Streamlit app in `app.py`
- Overview cards for active medications, goals, and health logs
- Charts for recent metric trends
- Import and export of metric data
- Medication adherence summary

### Medication management

- Add medication name, dosage, time, and notes
- View active schedules
- Mark medications as complete
- Check medication interaction warnings using the interaction helper

### Health goals

- Add goals such as steps, weight, sleep, or custom metrics
- Track active goals from MongoDB
- Deactivate or complete goals as needed

### AI chatbot

- Built in `src/chatbot.py`
- Uses LangChain agent tooling with healthcare-specific actions
- Connects to Groq, OpenAI, or Google models when API keys are configured
- Falls back to rule-based guidance when no LLM is available

### Indian health features

- Medicine lookup and local health information via `src/indian_health.py`
- Local doctor network filtering
- Ayurvedic remedy lookup
- Dietary recommendations based on region and health goal
- Regional health preferences and user context

### Database layer

- MongoDB collections are created and indexed in `src/database.py`
- Supported collections include:
  - `health_metrics`
  - `medications`
  - `health_goals`
  - `nutrition_logs`
  - `insurance_profiles`
  - `medical_history`
  - `regional_preferences`
  - `indian_medications`

## Tech stack

- Python 3.10+
- Streamlit
- MongoDB + PyMongo
- LangChain
- Groq / OpenAI / Google Generative AI support
- Pandas
- python-dotenv

## Project structure

```text
healthcare-ai-agent/
├── app.py
├── requirements.txt
├── run_app.ps1
├── LICENSE
├── README.md
├── data/
├── scratch/
├── src/
│   ├── __init__.py
│   ├── agent_tools.py
│   ├── chatbot.py
│   ├── config.py
│   ├── data_io.py
│   ├── database.py
│   ├── fitness_import.py
│   ├── health_parser.py
│   ├── indian_health.py
│   ├── medical_lookup.py
│   ├── medication.py
│   ├── medication_interactions.py
│   ├── rag.py
│   ├── reporting.py
│   └── validators.py
├── WEEK1_STATUS.md
├── WEEK3_4_STATUS.md
├── WEEK5_STATUS.md
└── project_text.txt
```

## Prerequisites

- Python 3.10 or later
- MongoDB running locally or reachable via a cloud connection
- pip installed
- Optional API keys for AI and external health data features

## Setup

1. Clone the repository

```bash
git clone https://github.com/narasingapranav/healthcare-ai-agent.git
cd healthcare-ai-agent
```

2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Start MongoDB

Make sure MongoDB is running before starting the app. A default local connection is used by the app if no custom `.env` is configured:

```text
mongodb://localhost:27017
```

5. Create a `.env` file in the project root

Example:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=healthcare_agent

USE_LLM=false
LLM_PROVIDER=groq

GROQ_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=

ONE_MG_API_URL=
ONE_MG_API_KEY=
PRACTO_API_URL=
PRACTO_API_KEY=
AYURVEDA_API_URL=
AYURVEDA_API_KEY=
```

## Running the app

From the project root:

```bash
streamlit run app.py
```

A Windows helper script is also included:

```powershell
./run_app.ps1
```

The app is typically available at:

```text
http://localhost:8501
```

## How the app works

### Health dashboard

The dashboard provides:

- a quick snapshot of active medications, goals, and health logs
- metric charts and latest values
- quick health Q&A
- medical topic lookup

### Chatbot panel

The chatbot can answer:

- medication questions
- wellness guidance
- reminders and scheduling help
- general health prompts
- database-backed personal health questions when an LLM is configured

### Metrics import/export

The app can import and export health metrics in multiple formats:

- CSV
- JSON
- XML

This is handled through the data I/O utilities and parser modules.

## Database behavior

On startup, the app calls `init_db()` and creates indexes for the major collections. If MongoDB is unavailable, the app will raise a clear error and the user will need to ensure the database server is reachable.

## Notes

- The AI features are optional. If no API keys are set, the app still runs in a limited offline mode.
- The system is intended for personal health tracking and educational guidance.
- It does not replace professional medical advice or diagnosis.

## Troubleshooting

### MongoDB connection issues

Check that MongoDB is running and the `MONGODB_URI` is correctly set.

### LLM not responding

Set one of the following keys in `.env` and ensure `USE_LLM=true`:

- `GROQ_API_KEY`
- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`

### App does not start

Make sure dependencies are installed:

```bash
pip install -r requirements.txt
```

Then run:

```bash
streamlit run app.py
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Repository

- GitHub: https://github.com/narasingapranav/healthcare-ai-agent
