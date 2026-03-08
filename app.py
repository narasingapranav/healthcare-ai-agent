import pandas as pd
import streamlit as st

from src.chatbot import HealthChatbot
from src.database import (
    add_health_metric,
    add_medication,
    deactivate_medication,
    init_db,
    list_medications,
    list_recent_metrics,
)
from src.health_parser import parse_metric_input
from src.medication import upcoming_reminders

st.set_page_config(page_title="Healthcare AI Agent - Track A", layout="wide")

init_db()
chatbot = HealthChatbot()

st.title("Healthcare Monitoring AI Agent (Track A)")
st.caption("Week 1 implementation: medication scheduler, health metrics, and basic health chatbot")

medications = list_medications(active_only=True)
alerts = upcoming_reminders(medications, window_minutes=60)
if alerts:
    for alert in alerts:
        st.warning(f"Reminder: {alert}")
else:
    st.info("No medication reminders in the next hour.")

tab1, tab2, tab3 = st.tabs(["Health Chat", "Medication Scheduler", "Health Metrics"])

with tab1:
    st.subheader("Basic Health Chatbot")
    question = st.text_input("Ask a health-related question", placeholder="How can I track my steps better?")
    if st.button("Get Guidance", type="primary"):
        response = chatbot.answer(question)
        st.write(response)

with tab2:
    st.subheader("Medication Reminder Setup")
    with st.form("medication_form"):
        med_name = st.text_input("Medicine name")
        dosage = st.text_input("Dosage", placeholder="500 mg")
        schedule = st.time_input("Schedule time")
        notes = st.text_input("Notes (optional)")
        submitted = st.form_submit_button("Add Medication")

    if submitted:
        if med_name.strip() and dosage.strip():
            add_medication(med_name.strip(), dosage.strip(), schedule.strftime("%H:%M"), notes.strip())
            st.success("Medication schedule added.")
            st.rerun()
        else:
            st.error("Medicine name and dosage are required.")

    st.markdown("### Active Schedules")
    for medication in medications:
        cols = st.columns([4, 2, 2, 1])
        cols[0].write(f"**{medication['name']}** ({medication['dosage']})")
        cols[1].write(medication["schedule_time"])
        cols[2].write(medication["notes"] or "-")
        if cols[3].button("Done", key=f"done_{medication['id']}"):
            deactivate_medication(medication["id"])
            st.rerun()

with tab3:
    st.subheader("Health Metrics Logger")
    with st.form("metric_form"):
        metric_name = st.selectbox("Metric", ["steps", "heart_rate", "weight", "sleep_hours", "water_intake"])
        metric_value = st.text_input("Value", placeholder="e.g., 6500")
        unit = st.text_input("Unit", placeholder="steps / bpm / kg / hours / liters")
        metric_submit = st.form_submit_button("Save Metric")

    if metric_submit:
        try:
            clean_name, value, clean_unit, timestamp = parse_metric_input(metric_name, metric_value, unit)
            add_health_metric(clean_name, value, clean_unit, timestamp)
            st.success("Health metric saved.")
            st.rerun()
        except ValueError as error:
            st.error(str(error))

    records = list_recent_metrics(limit=50)
    if records:
        dataframe = pd.DataFrame(records, columns=["metric_name", "metric_value", "unit", "recorded_at"])
        st.dataframe(dataframe, use_container_width=True)

        st.markdown("### Recent Trend")
        metric_filter = st.selectbox("Choose metric", sorted(dataframe["metric_name"].unique()))
        filtered = dataframe[dataframe["metric_name"] == metric_filter].copy()
        filtered["recorded_at"] = pd.to_datetime(filtered["recorded_at"])
        filtered = filtered.sort_values("recorded_at")
        st.line_chart(filtered.set_index("recorded_at")["metric_value"])
    else:
        st.info("No metrics logged yet.")
