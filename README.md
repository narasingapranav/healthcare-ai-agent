# 🏥 Healthcare Monitoring AI Agent

An AI-powered personal health assistant that helps users track medications, monitor schedules, and manage basic health data using MongoDB and Streamlit.

---

## 🚀 Project Overview

This project is part of an 8-week Healthcare AI Development track.

The system allows users to:
- Add and manage medications
- Store structured health data
- Receive time-based reminders
- Persist data using MongoDB
- Access a clean dashboard built with Streamlit

---

## 🛠️ Tech Stack

- Python
- Streamlit
- MongoDB
- PyMongo
- dotenv

---

## 📂 Project Structure

```
healthcare-ai-agent/
|
|-- app.py
|-- db.py
|-- medication_service.py
|-- models.py
|-- requirements.txt
|-- .env (not pushed)
`-- README.md
```

---

## ⚙️ Features (Week 1)

✅ Add medication  
✅ Store medication in MongoDB  
✅ View all medications  
✅ Delete medications  
✅ Time-based reminder alerts  
✅ Structured health data parsing  

---

## ⚙️ Features (Week 3-4)

✅ Fitness + medication management workflow in one app  
✅ Health metric visualization with trend charts  
✅ Medication interaction checking (known pair warnings)  
✅ Health report generation and download  
✅ Multi-format health data support (JSON, CSV, XML import/export)  
✅ Health goal setting and progress tracking  
✅ Indian Personal Health Assistant tab  
✅ 1mg medicine search integration (configurable API endpoint + offline-safe fallback)  
✅ Practo doctor search integration (configurable API endpoint + offline-safe fallback)  
✅ Ayurvedic medicine information integration  
✅ MongoDB-backed Indian medication database

---

## ⚙️ Features (Week 5-6: Domain Specialization - Option A1)

✅ MongoDB database for Indian medication and domain records  
✅ Indian dietary recommendations based on region, goal, and diet preference  
✅ Nutrition tracking (meal logs with macro fields)  
✅ Indian health insurance profile management  
✅ Medical history timeline records  
✅ Regional health preference capture (language, city/state, budget, mode)  
✅ Local doctor network filtering + Practo regional lookup

---

## 🧠 Architecture

- **Database Layer** -> `db.py`
- **Data Model Layer** -> `models.py`
- **Business Logic Layer** -> `medication_service.py`
- **Frontend/UI Layer** -> `app.py`

This layered design ensures scalability for future upgrades like:
- Fitness data integration
- AI chatbot
- Nutrition tracking
- Health analytics dashboard

---

## 🗄️ Database

MongoDB collection: `medications`

Example stored document:

```json
{
	"_id": ObjectId("..."),
	"name": "Paracetamol",
	"dosage": "500mg",
	"time": "09:00:00",
	"frequency": "Daily",
	"start_date": "2026-03-01",
	"end_date": "2026-03-10",
	"created_at": "2026-03-01T..."
}
```

---

## ▶️ How to Run Locally

1. Clone repository:

```bash
git clone https://github.com/yourusername/healthcare-ai-agent.git
cd healthcare-ai-agent
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` file:

```
MONGO_URI=mongodb://127.0.0.1:27017/
MONGODB_URI=mongodb://127.0.0.1:27017/
MONGODB_DB_NAME=healthcare_agent

# Optional Indian platform integrations
ONE_MG_API_URL=
ONE_MG_API_KEY=
PRACTO_API_URL=
PRACTO_API_KEY=
AYURVEDA_API_URL=
AYURVEDA_API_KEY=
```

4. Run application:

```bash
streamlit run app.py
```

5. (Optional) Import health metrics from file in app:

- CSV columns: `metric_name, metric_value, unit, recorded_at`
- JSON format: list of metric objects with same keys
- XML format:

```xml
<metrics>
	<metric>
		<metric_name>steps</metric_name>
		<metric_value>8200</metric_value>
		<unit>steps</unit>
		<recorded_at>2026-03-22T08:00:00</recorded_at>
	</metric>
</metrics>
```

---

## ☁️ Deployment

This project can be deployed using:
- Streamlit Community Cloud
- MongoDB Atlas (Cloud Database)

---

## ⚠️ Disclaimer

This application is for educational purposes only.  
It does not replace professional medical advice.

---

## 📌 Future Improvements

- User authentication
- Cloud database integration
- AI health chatbot
- Fitness data integration (Google Fit / Fitbit)
- Nutrition tracking
- Health analytics dashboard

---

## 👨‍💻 Author

Developed as part of Healthcare AI Agent Development Project.
