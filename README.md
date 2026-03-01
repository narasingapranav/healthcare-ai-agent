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
│
├── app.py
├── db.py
├── medication_service.py
├── models.py
├── requirements.txt
├── .env (not pushed)
└── README.md
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

## 🧠 Architecture

- **Database Layer** → `db.py`
- **Data Model Layer** → `models.py`
- **Business Logic Layer** → `medication_service.py`
- **Frontend/UI Layer** → `app.py`

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
```

4. Run application:

```bash
streamlit run app.py
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