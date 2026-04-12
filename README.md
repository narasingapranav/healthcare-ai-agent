# 🏥 Healthcare Monitoring AI Agent - Professional Edition

An **AI-powered personal health assistant** for comprehensive health tracking, medication management, and domain-specialized Indian health services. Built with **Streamlit**, **MongoDB**, and **LangChain LLMs** for production-ready performance.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Tech Stack](#tech-stack)
4. [Prerequisites](#prerequisites)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [Running the Application](#running-the-application)
8. [API Integrations](#api-integrations)
9. [Database Schema](#database-schema)
10. [Input Validation & Error Handling](#input-validation--error-handling)
11. [Project Structure](#project-structure)
12. [Usage Guide](#usage-guide)
13. [Troubleshooting](#troubleshooting)
14. [Contributing](#contributing)
15. [License](#license)

---

## 🚀 Project Overview

The **Healthcare Monitoring AI Agent** is an 8-week capstone project in the Healthcare AI Development track. It provides a unified interface for:

- **Health Metrics Tracking**: Record and visualize vital signs, fitness data, and health benchmarks
- **Medication Management**: Schedule medications, check interactions, track adherence
- **Health Goals**: Set targets and monitor progress toward wellness objectives
- **Indian Health Specialization**: 
  - Country-specific medication database (1mg, Practo APIs)
  - Ayurvedic medicine information with safety guidance
  - Regional dietary recommendations and nutrition tracking
  - Health insurance profile management
  - Medical history timeline records
  - Local doctor network and regional preferences

The application prioritizes **data accuracy**, **comprehensive error handling**, and **user-friendly error messages** for seamless health data management.

---

## ✨ Key Features

### Core Health Management
✅ **Add & manage medications** with scheduling and reminders  
✅ **Log health metrics** (blood pressure, heart rate, weight, sleep, water intake)  
✅ **Set and track health goals** with deadline monitoring  
✅ **Import/export health data** in multiple formats (CSV, JSON, XML)  
✅ **Visualize trends** with interactive charts and dashboards  
✅ **Check drug interactions** from known medication pair database  

### Indian Health Specialization (Week 5-6)
✅ **1mg Medicine Integration**: Search Indian medications by name/salt/brand  
✅ **Practo Doctor Network**: Find regional doctors with filters (specialty, language, budget)  
✅ **Ayurvedic Medicine Info**: 20+ common Ayurvedic herbs with indications and safety notes  
✅ **Dietary Recommendations**: Region-specific food guidance based on health goals  
✅ **Nutrition Tracking**: Log meals with macro tracking (calories, protein, carbs, fats, fiber)  
✅ **Insurance Management**: Store and filter insurance profiles with policy details  
✅ **Medical History Timeline**: Track diagnoses, treatments, procedures, and allergies  
✅ **Regional Preferences**: Customize language, diet, consultation mode, and doctor budget  

### AI & Analytics
✅ **Health Chatbot**: AI-powered Q&A using configurable LLM (Groq, OpenAI, Google)  
✅ **Medication Interaction Warnings**: Real-time alerts for known drug combinations  
✅ **Health Report Generation**: Exportable PDFs with trend summaries  
✅ **Medical Information Lookup**: Curated disease/condition information with citations  

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit (web UI) |
| **Backend** | Python 3.10+ |
| **Database** | MongoDB (document storage & indexes) |
| **ORM/Driver** | PyMongo 4.x |
| **LLM Integration** | LangChain with Groq/OpenAI/Google APIs |
| **Data Processing** | Pandas, NumPy |
| **Validation** | Custom validators module with detailed error messages |
| **Logging** | Python logging (info, error, warning levels) |
| **Environment** | python-dotenv |

---

## 📋 Prerequisites

- **Python 3.10 or higher**
- **MongoDB 4.4 or higher** (local or cloud instance)
- **pip** (Python package manager)
- **Git** (for version control)
- **API Keys** (optional, for enhanced features):
  - Groq API key (or OpenAI / Google Generative AI)
  - 1mg API credentials
  - Practo API credentials

---

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd healthcare-ai-agent
```

### 2. Create Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set Up MongoDB

**Option A: Local MongoDB Installation**

- **macOS**: `brew install mongodb-community && brew services start mongodb-community`
- **Linux**: [Official MongoDB install guide](https://docs.mongodb.com/manual/installation/)
- **Windows**: [Download & run MongoDB installer](https://www.mongodb.com/try/download/community)

Then, verify connection:
```bash
mongosh  # or mongo in older versions
> db.adminCommand('ping')  # Should return { ok: 1 }
> exit
```

**Option B: MongoDB Atlas (Cloud)**

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free account or log in
3. Create a cluster (M0 free tier recommended)
4. Get your connection string: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`
5. **Store securely in `.env` file** (see Configuration section below)

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your configuration (see Configuration section below).

---

## ⚙️ Configuration

### Basic Configuration (`.env` file)

```ini
# === MongoDB Configuration ===
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=healthcare_agent

# === LLM Configuration (Optional) ===
USE_LLM=true
LLM_PROVIDER=groq  # Options: groq, openai, google

# === API Keys for LLM ===
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# === Indian Health Platform APIs (Optional) ===
ONE_MG_API_URL=https://api.1mg.example.com
ONE_MG_API_KEY=your_1mg_api_key_here
PRACTO_API_URL=https://api.practo.example.com
PRACTO_API_KEY=your_practo_api_key_here
AYURVEDA_API_URL=https://api.ayurveda.example.com
AYURVEDA_API_KEY=your_ayurveda_api_key_here

# === Optional: External Service Keys ===
WEATHERSTACK_API_KEY=your_weatherstack_key
EXCHANGERATE_API_KEY=your_exchange_rate_key
SERP_API_KEY=your_serp_search_key
```

### Configuration Details

#### MongoDB Connection

- **Local Development**: `mongodb://localhost:27017`
- **MongoDB Atlas**: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`
- **Remote Server**: `mongodb://host:port` or with auth

#### LLM Provider Selection

By default, the app uses **Groq** (free tier available). To switch providers:

```python
# In src/config.py, the LLM_PROVIDER is read from .env
# USE_LLM=false will disable AI features but keep the app functional
```

#### API Integration (India-Specific)

**Important**: These APIs are optional. The app includes fallback data and works offline:

- **1mg**: Medicine search API for Indian pharmaceutical products
- **Practo**: Doctor network and appointment booking API
- **Ayurveda**: Ayurvedic herb and treatment database

If API keys are not configured, the app will use pre-loaded sample data.

---

## 🚀 Running the Application

### Development Server

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` automatically.

### Production Deployment

```bash
streamlit run app.py --logger.level=warning --client.toolbarPosition=bottom
```

### Common Streamlit Flags

```bash
streamlit run app.py \
  --server.port 8502 \                    # Custom port
  --client.showErrorDetails=false \       # Hide error details
  --logger.level=info \                   # Log level
  --cache_code=true                       # Cache compiled code
```

---

## 🌐 API Integrations

### 1mg Medicine Search

**Purpose**: Search for Indian medications, including salt composition, brand names, and pricing.

```python
from src.indian_health import IndianHealthService

service = IndianHealthService()
medicines = service.search_1mg_medicines(query="aspirin")
# Returns: [{"name": "Aspirin", "manufacturer": "Bayer", "price": 50, ...}]
```

**Configuration**:
- Set `ONE_MG_API_URL` and `ONE_MG_API_KEY` in `.env`
- Without credentials, uses fallback sample data

### Practo Doctor Search

**Purpose**: Find doctors and healthcare providers by specialty, location, and language.

```python
doctors = service.search_practo_doctors(city="Bengaluru", specialty="Cardiologist", limit=10)
# Returns filtered doctor profiles with contact and ratings
```

**Configuration**:
- Set `PRACTO_API_URL` and `PRACTO_API_KEY` in `.env`
- Supports language filters, budget ranges, and consultation modes

### Ayurvedic Medicine Info

**Purpose**: Access curated Ayurvedic herb information with indications and safety notes.

```python
ayurveda_info = service.get_ayurvedic_info(herb="ashwagandha")
# Returns: Indications, cautions, evidence level, dosage guidance
```

**Built-in Database**:
- 20+ common Ayurvedic herbs (ashwagandha, triphala, tulsi, etc.)
- No external API required; fully functional offline
- Optional: Configure `AYURVEDA_API_URL` for custom sources

---

## 🗄️ Database Schema

### Collections

#### `health_metrics`
Stores user-logged vital signs and fitness data.

```json
{
  "_id": ObjectId,
  "metric_name": "blood_pressure_systolic",
  "metric_value": 130,
  "unit": "mmHg",
  "recorded_at": "2025-04-12T10:30:00.000Z",
  "recorded_at_dt": "ISO8601 DateTime"
}
```

**Index**: `recorded_at_dt DESC`

#### `medications`
Active and completed medication schedules.

```json
{
  "_id": ObjectId,
  "name": "Aspirin",
  "dosage": "500 mg",
  "schedule_time": "09:00",
  "notes": "With breakfast",
  "active": true,
  "created_at": "ISO8601 DateTime"
}
```

**Index**: `active ASC, schedule_time ASC`

#### `health_goals`
User-defined health targets with deadlines.

```json
{
  "_id": ObjectId,
  "metric_name": "weight",
  "target_value": 70,
  "unit": "kg",
  "active": true,
  "created_at": "ISO8601 DateTime"
}
```

#### `nutrition_logs`
Meal records with macronutrient tracking.

```json
{
  "_id": ObjectId,
  "meal_date": "2025-04-12",
  "meal_type": "breakfast",
  "region": "South India",
  "food_item": "Idli with sambar",
  "calories": 250,
  "protein_g": 8,
  "carbs_g": 45,
  "fats_g": 2,
  "fiber_g": 3,
  "created_at": "ISO8601 DateTime"
}
```

**Indexes**: `meal_date DESC`, `region ASC`

#### `insurance_profiles`
Health insurance policy records.

```json
{
  "_id": ObjectId,
  "patient_name": "Amit Sharma",
  "insurer": "Star Health",
  "policy_number": "POL123456",
  "policy_type": "Family Floater",
  "sum_insured": 500000,
  "expiry_date": "2026-04-12",
  "network_hospitals": "Apollo, Fortis"
}
```

**Indexes**: `patient_name + policy_number UNIQUE`, `updated_at DESC`

#### `medical_history`
Timeline of diagnoses, treatments, and procedures.

```json
{
  "_id": ObjectId,
  "patient_name": "Amit Sharma",
  "condition_name": "Hypertension",
  "diagnosis_date": "2023-06-15",
  "medications": "Amlodipine",
  "allergies": "Penicillin",
  "procedures_done": "Angioplasty",
  "created_at": "ISO8601 DateTime"
}
```

#### `regional_preferences`
Patient-specific regional and consultation preferences.

```json
{
  "_id": ObjectId,
  "patient_name": "Amit Sharma",
  "state": "Karnataka",
  "city": "Bengaluru",
  "preferred_language": "Kannada",
  "diet_preference": "Vegetarian",
  "consultation_mode": "Teleconsultation",
  "max_budget_inr": 800
}
```

**Index**: `patient_name UNIQUE`

---

## ✅ Input Validation & Error Handling

### Comprehensive Validation

The app includes a dedicated **`src/validators.py`** module with strict input validation:

#### Health Metric Validation

```python
from src.validators import validate_health_metric, ValidationError

try:
    clean_name, value, unit, timestamp = validate_health_metric(
        metric_name="blood_pressure_systolic",
        metric_value="140",
        unit="mmHg"
    )
except ValidationError as e:
    print(f"Validation error: {e}")  # Detailed, user-friendly message
```

**Validates**:
- Metric name format (alphanumeric, underscores, spaces)
- Numeric value within physiological ranges
- Unit format and consistency
- Timestamp ISO format

#### Medication Validation

```python
from src.validators import validate_medication

validated_med = validate_medication(
    name="Aspirin",
    dosage="500 mg",
    schedule="twice daily",
    active=True
)
```

**Validates**:
- Medication name (2-50 chars, valid characters)
- Dosage format (clear, concise descriptions)
- Schedule clarity (e.g., "once daily", "every 12 hours")

#### Nutrition Log Validation

```python
from src.validators import validate_nutrition_log

validated_nutrition = validate_nutrition_log(
    meal_type="breakfast",
    calories="250",
    protein="8",
    carbs="45",
    fat="2",
    meal_date="2025-04-12"
)
```

**Validates**:
- Macro values within reasonable ranges (0-5000 cal, etc.)
- Macros don't exceed unrealistic totals
- Meal date not in future
- Region name validity (if provided)

#### Insurance Profile Validation

```python
from src.validators import validate_insurance_profile

validated_insurance = validate_insurance_profile(
    patient_name="Amit Sharma",
    policy_number="POL123456",
    provider="Star Health",
    policy_type="Family",
    coverage_limit="500000"
)
```

**Validates**:
- Patient name format
- Policy number format and uniqueness
- Provider name validity
- Coverage limit realistic range (1 to 100 million INR)

### Error Messages

All validation errors provide **specific, actionable feedback**:

| Error | Message | Fix |
|-------|---------|-----|
| Empty field | "Metric name is required and must be text." | Enter a valid name |
| Out of range | "Invalid value for blood_pressure: 300 is outside normal range (70-250)." | Verify reading or unit |
| Invalid format | "Policy number must be at least 3 characters." | Enter full policy number |
| Future date | "Meal date cannot be in the future." | Select today or past date |

### Error Handling in App

All Streamlit forms include **try-catch blocks** with user-friendly error display:

```python
try:
    validated_data = validate_medication(...)
    save_to_database(validated_data)
    st.success("✅ Medication saved successfully.")
except ValidationError as e:
    st.error(f"❌ Medication validation failed: {str(e)}")
except DatabaseError as e:
    st.error(f"❌ Database error: {str(e)}")
except Exception as e:
    st.error(f"❌ Unexpected error: {str(e)}")
```

### Database Error Handling

The **`src/database.py`** module includes comprehensive error handling:

```python
from src.database import DatabaseError, add_medication

try:
    add_medication(name, dosage, schedule, notes)
except DatabaseError as e:
    print(f"Failed to save medication: {e}")  # Clear error details
except Exception as e:
    print(f"Unexpected database error: {e}")
```

**Handles**:
- MongoDB connection failures
- Duplicate record detection (unique index violations)
- Invalid data types
- Timestamp parsing errors
- Network timeouts

---

## 📁 Project Structure

```
healthcare-ai-agent/
│
├── app.py                          # Main Streamlit application
│
├── src/
│   ├── __init__.py
│   ├── config.py                   # Environment variable loader
│   ├── database.py                 # MongoDB CRUD operations w/ error handling
│   ├── validators.py               # Input validation module
│   ├── health_parser.py            # Health metric parsing
│   ├── medication_interactions.py  # Drug interaction database
│   ├── medication.py               # Medication reminder logic
│   ├── indian_health.py            # Indian API integrations
│   ├── medical_lookup.py           # Curated medical information
│   ├── chatbot.py                  # LLM-powered health Q&A
│   ├── reporting.py                # Health report generation
│   └── data_io.py                  # Multi-format import/export
│
├── data/                           # Sample data directory
│
├── requirements.txt                # Python dependencies
├── .env.example                    # Example environment config
├── LICENSE                         # Project license
├── README.md                       # This file
│
├── WEEK1_STATUS.md                 # Week 1-2 feature checklist
├── WEEK3_4_STATUS.md               # Week 3-4 feature checklist
└── WEEK5_STATUS.md                 # Week 5-6 feature checklist (current)
```

---

## 📖 Usage Guide

### Health Metrics

1. **Record a Metric**: 
   - Go to "Health Metrics" section
   - Select metric type, enter value and unit
   - Click "Save Metric"
   - App validates ranges and saves to MongoDB

2. **Import Fitness Data**:
   - Prepare CSV/JSON/XML file with columns: `metric_name`, `metric_value`, `unit`, `recorded_at`
   - Upload file and click "Import"
   - App parses and validates each row
   - Failed rows are reported with specific reasons

3. **View Trends**:
   - Recent metrics display in table
   - Select metric from dropdown
   - Line chart shows recorded values over time

4. **Export Data**:
   - Click "Export Metrics" buttons
   - Download as CSV, JSON, or XML
   - Data includes all historic records

### Medications

1. **Add Medication**:
   - Enter medicine name, dosage, time, optional notes
   - Validation checks name format, dosage clarity
   - Saved to "Active Schedules" with time sorting

2. **Check Interactions**:
   - Active medications checked against known interaction pairs
   - Warnings displayed for ibuprofen+warfarin, aspirin+warfarin, metformin+alcohol, etc.

3. **Track Adherence**:
   - Click "Done" to mark medication as completed
   - Adherence report shows % of scheduled medications completed
   - Table displays all historical records

### Indian Health Features

1. **Search Medicines**:
   - Go to "Indian Health" section
   - Enter medicine name
   - View results from 1mg (or fallback data)

2. **Find Doctors**:
   - Set location and preferences
   - Search by specialty
   - Filter by:
     - Language
     - Budget
     - Consultation mode (in-person / teleconsultation)

3. **Log Meals**:
   - Select region, health goal, diet preference
   - Enter food item, quantity, macros
   - Receives region-specific dietary recommendations

4. **Manage Insurance**:
   - Enter policy details (patient name, insurer, policy number, amount)
   - Profile saved for filtering and reference

5. **Add Medical History**:
   - Record diagnoses, medications, allergies, procedures
   - Timeline view of all conditions

6. **Set Regional Preferences**:
   - Choose language, city, consultation mode
   - Specify doctor specialties and budget
   - Preferences used for doctor search filtering

---

## 🐛 Troubleshooting

### Common Issues

#### 1. MongoDB Connection Error

**Error**: `Failed to connect to MongoDB. Please ensure MongoDB is running...`

**Solution**:
```bash
# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Windows
net start MongoDB

# Verify connection
mongosh
> db.adminCommand('ping')
```

**For MongoDB Atlas**:
- Verify connection string in `.env`
- Check IP whitelist includes your IP (or 0.0.0.0 for development)
- Ensure credentials are URL-encoded (special chars → %XX)

#### 2. Validation Error on Save

**Error**: `Metric validation failed: Invalid value for blood_pressure: 300 is outside normal range (70-250).`

**Solution**:
- Verify the value and unit are correct
- Blood pressure range is typically 70-250 mmHg
- Weight should be 10-500 kg
- If value is legitimate, manually insert via MongoDB client

#### 3. API Key Error for LLM Features

**Error**: `GROQ_API_KEY is not configured`

**Solution**:
- Get free API key from [Groq Console](https://console.groq.com)
- Add to `.env`: `GROQ_API_KEY=your_key`
- Restart Streamlit app
- Or disable LLM: `USE_LLM=false` (app works without it)

#### 4. Streamlit Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
streamlit run app.py --server.port 8502  # Use different port
```

Or kill existing process:
```bash
# macOS/Linux
lsof -ti:8501 | xargs kill -9

# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

#### 5. Import File Parsing Error

**Error**: `File format error. Please ensure file contains valid metric data.`

**Solution**:
- Verify file format and column names
- Required columns for CSV: `metric_name`, `metric_value`, `unit`, `recorded_at`
- Dates must be ISO format: `2025-04-12T10:30:00Z`
- Check no special characters in metric names

#### 6. Unique Constraint Violation

**Error**: `E11000 duplicate key error. Policy number already exists.`

**Solution**:
- Use different policy number or patient name
- Or update existing profile instead of creating new one
- Clear duplicate via MongoDB client if needed

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### 1. Fork & Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write tests for new functionality
- Follow Python PEP 8 style guide
- Add docstrings to all functions
- Update README if adding features

### 3. Commit & Push

```bash
git add .
git commit -m "feat: brief description of changes"
git push origin feature/your-feature-name
```

### 4. Create Pull Request

- Link to any related issues
- Describe changes clearly
- Include before/after examples if applicable

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🎯 Roadmap

**In Development**:
- [ ] Advanced health analytics (ML-based trend prediction)
- [ ] Integration with fitness wearables (Apple Watch, Fitbit)
- [ ] Multi-user support with authentication
- [ ] Mobile app (React Native)
- [ ] Real-time health alerts (SMS/email notifications)
- [ ] Telemedicine integration with video consultation
- [ ] Medication refill reminders
- [ ] Pharmacogenomics-based drug interaction warnings

**Planned Features**:
- [ ] Family health dashboards
- [ ] Integration with electronic health records (EHR)
- [ ] Nutritionist consultation marketplace
- [ ] Insurance claim assistance
- [ ] Vaccine tracker for immunizations

---

## 🙏 Acknowledgments

- **MongoDB** for scalable document database
- **Streamlit** for rapid UI development
- **Groq** for fast LLM inference
- **1mg & Practo** for India health data APIs
- Healthcare practitioners for domain expertise

---

**Version**: 1.0.0  
**Last Updated**: April 12, 2025  
**Status**: Production Ready ✅

**Quick Links**:
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [PyMongo Guide](https://pymongo.readthedocs.io/)
- [LangChain Docs](https://docs.langchain.com/)
- [1mg API Docs](https://developers.1mg.com/)
- [Python PEP 8 Style Guide](https://pep8.org/)
