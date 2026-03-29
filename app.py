import pandas as pd
import streamlit as st

from src.chatbot import HealthChatbot
from src.data_io import (
    export_metrics_to_csv,
    export_metrics_to_json,
    export_metrics_to_xml,
    parse_metrics_csv_text,
    parse_metrics_json_text,
    parse_metrics_xml_text,
)
from src.database import (
    add_health_metric,
    add_health_goal,
    add_medication,
    deactivate_health_goal,
    deactivate_medication,
    init_db,
    list_indian_medications,
    list_all_metrics,
    list_health_goals,
    list_medications,
    list_recent_metrics,
    upsert_indian_medication,
)
from src.health_parser import parse_metric_input
from src.indian_health import IndianHealthService
from src.medication_interactions import check_interactions
from src.medication import upcoming_reminders
from src.reporting import generate_health_report

st.set_page_config(page_title="Healthcare AI Agent - Track A", layout="wide")

init_db()
chatbot = HealthChatbot()
indian_health = IndianHealthService()

st.title("Healthcare Monitoring AI Agent (Track A)")
st.caption(
    "Week 3-4 implementation: medication + fitness workflow, interactions, goals, reports, and multi-format data support"
)

medications = list_medications(active_only=True)
alerts = upcoming_reminders(medications, window_minutes=60)
if alerts:
    for alert in alerts:
        st.warning(f"Reminder: {alert}")
else:
    st.info("No medication reminders in the next hour.")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "Health Chat",
        "Medication Scheduler",
        "Health Metrics",
        "Goals & Progress",
        "Reports",
        "Indian Health",
    ]
)

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

    st.markdown("### Medication Interaction Check")
    names = [item["name"] for item in medications if item.get("name")]
    if names:
        findings = check_interactions(names)
        if findings:
            for warning in findings:
                st.warning(warning)
        else:
            st.success("No known interaction pairs found in the current list.")
    else:
        st.info("Add medications to run interaction checks.")

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

    st.markdown("### Import Fitness Data (CSV/JSON/XML)")
    uploaded_file = st.file_uploader("Upload fitness data file", type=["csv", "json", "xml"])
    if uploaded_file is not None:
        import_clicked = st.button("Import Uploaded File", type="primary")
        if import_clicked:
            try:
                payload = uploaded_file.read().decode("utf-8")
                parsed_metrics: list[dict] = []
                if uploaded_file.name.endswith(".csv"):
                    parsed_metrics = parse_metrics_csv_text(payload)
                elif uploaded_file.name.endswith(".json"):
                    parsed_metrics = parse_metrics_json_text(payload)
                elif uploaded_file.name.endswith(".xml"):
                    parsed_metrics = parse_metrics_xml_text(payload)

                for item in parsed_metrics:
                    add_health_metric(
                        str(item["metric_name"]),
                        float(item["metric_value"]),
                        str(item["unit"]),
                        str(item["recorded_at"]),
                    )

                if parsed_metrics:
                    st.success(f"Imported {len(parsed_metrics)} fitness records.")
                    st.rerun()
                else:
                    st.info("No rows found in uploaded file.")
            except Exception as error:
                st.error(f"Could not import file. Please check file format. Details: {error}")

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

        st.markdown("### Export Metrics")
        all_metrics = list_all_metrics()
        csv_data = export_metrics_to_csv(all_metrics)
        json_data = export_metrics_to_json(all_metrics)
        xml_data = export_metrics_to_xml(all_metrics)

        c1, c2, c3 = st.columns(3)
        c1.download_button(
            "Download CSV",
            data=csv_data,
            file_name="health_metrics_export.csv",
            mime="text/csv",
        )
        c2.download_button(
            "Download JSON",
            data=json_data,
            file_name="health_metrics_export.json",
            mime="application/json",
        )
        c3.download_button(
            "Download XML",
            data=xml_data,
            file_name="health_metrics_export.xml",
            mime="application/xml",
        )
    else:
        st.info("No metrics logged yet.")

with tab4:
    st.subheader("Health Goals and Progress")
    progress_mode = st.radio(
        "Progress Mode",
        ["Latest", "Daily", "Monthly"],
        horizontal=True,
        help="Latest uses the most recent value. Daily and Monthly use summed values for the selected period.",
    )

    with st.form("goal_form"):
        goal_metric = st.selectbox(
            "Goal Metric",
            ["steps", "heart_rate", "weight", "sleep_hours", "water_intake"],
        )
        goal_target = st.number_input("Target Value", min_value=0.0, step=1.0, format="%.2f")
        goal_unit = st.text_input("Unit", placeholder="steps / bpm / kg / hours / liters")
        goal_submit = st.form_submit_button("Add Goal")

    if goal_submit:
        if goal_target > 0 and goal_unit.strip():
            add_health_goal(goal_metric.strip().lower(), float(goal_target), goal_unit.strip())
            st.success("Goal added.")
            st.rerun()
        else:
            st.error("Target value must be > 0 and unit is required.")

    goals = list_health_goals(active_only=True)
    metrics = list_all_metrics()
    metric_df = pd.DataFrame(metrics, columns=["metric_name", "metric_value", "unit", "recorded_at"])
    if not metric_df.empty:
        metric_df["recorded_at"] = pd.to_datetime(metric_df["recorded_at"], errors="coerce")
        metric_df = metric_df.dropna(subset=["recorded_at"])
        metric_df = metric_df.sort_values("recorded_at", ascending=False)

    if goals:
        for goal in goals:
            metric_name = goal["metric_name"]
            target_value = float(goal["target_value"])

            current_value = 0.0
            if not metric_df.empty:
                per_metric = metric_df[metric_df["metric_name"] == metric_name].copy()
                if not per_metric.empty:
                    if progress_mode == "Latest":
                        current_value = float(per_metric.iloc[0]["metric_value"])
                    elif progress_mode == "Daily":
                        today = pd.Timestamp.utcnow().date()
                        today_rows = per_metric[per_metric["recorded_at"].dt.date == today]
                        current_value = float(today_rows["metric_value"].sum()) if not today_rows.empty else 0.0
                    elif progress_mode == "Monthly":
                        now = pd.Timestamp.utcnow()
                        month_rows = per_metric[
                            (per_metric["recorded_at"].dt.year == now.year)
                            & (per_metric["recorded_at"].dt.month == now.month)
                        ]
                        current_value = float(month_rows["metric_value"].sum()) if not month_rows.empty else 0.0

            progress = min(current_value / target_value, 1.0) if target_value > 0 else 0.0

            cols = st.columns([3, 3, 2, 1])
            cols[0].write(f"**{metric_name}**")
            cols[1].progress(progress, text=f"{current_value:.2f}/{target_value:.2f} {goal['unit']}")
            cols[2].write(f"{progress * 100:.1f}%")
            if cols[3].button("Close", key=f"goal_close_{goal['id']}"):
                deactivate_health_goal(goal["id"])
                st.rerun()
    else:
        st.info("No active goals yet.")

with tab5:
    st.subheader("Health Report")
    report_progress_mode = st.radio(
        "Goal Progress Mode (Report)",
        ["Latest", "Daily", "Monthly"],
        horizontal=True,
    )
    all_metrics = list_all_metrics()
    active_goals = list_health_goals(active_only=True)
    report_text = generate_health_report(
        all_metrics,
        medications,
        active_goals,
        progress_mode=report_progress_mode,
    )
    st.text_area("Generated report", value=report_text, height=360)
    st.download_button(
        "Download Report",
        data=report_text,
        file_name="health_report.txt",
        mime="text/plain",
    )

with tab6:
    st.subheader("Indian Personal Health Assistant")

    st.markdown("### 1mg Medicine Search")
    search_query = st.text_input("Search medicine on 1mg", placeholder="Paracetamol")
    medicine_limit = st.slider("Max results", min_value=1, max_value=20, value=5)
    if st.button("Search 1mg", key="search_1mg"):
        if not search_query.strip():
            st.error("Please enter a medicine name to search.")
        else:
            med_results = indian_health.search_1mg_medicines(search_query.strip(), limit=medicine_limit)
            if med_results:
                for index, item in enumerate(med_results):
                    st.markdown(f"**{item.get('name', 'Unknown')}**")
                    st.caption(
                        f"Manufacturer: {item.get('manufacturer', '-') or '-'} | "
                        f"Price (INR): {item.get('price_inr') if item.get('price_inr') is not None else '-'}"
                    )
                    st.write(item.get("uses", "No usage information available."))

                    if item.get("url"):
                        st.markdown(f"[Product Link]({item['url']})")

                    if st.button("Save to Indian Medication DB", key=f"save_indian_med_{index}"):
                        upsert_indian_medication(
                            source="1mg",
                            name=str(item.get("name", "")),
                            manufacturer=str(item.get("manufacturer", "")),
                            price_inr=item.get("price_inr"),
                            uses=str(item.get("uses", "")),
                            product_url=str(item.get("url", "")),
                            raw_payload=item.get("raw") if isinstance(item.get("raw"), dict) else {},
                        )
                        st.success(f"Saved {item.get('name', 'medicine')} to MongoDB.")
            else:
                st.info("No medicine results found.")

    st.markdown("### Practo Doctor Finder")
    practo_city = st.text_input("City", placeholder="Bengaluru")
    practo_specialty = st.text_input("Specialty", placeholder="General Physician")
    practo_limit = st.slider("Max doctors", min_value=1, max_value=20, value=5)
    if st.button("Search Practo", key="search_practo"):
        doctors = indian_health.search_practo_doctors(practo_city, practo_specialty, limit=practo_limit)
        if doctors:
            for doctor in doctors:
                st.markdown(f"**{doctor.get('name', 'Unknown Doctor')}**")
                st.caption(
                    f"{doctor.get('specialty', '-') or '-'} | "
                    f"{doctor.get('city', '-') or '-'} | "
                    f"Experience: {doctor.get('experience_years', 0)} years | "
                    f"Fee (INR): {doctor.get('consultation_fee_inr') if doctor.get('consultation_fee_inr') is not None else '-'}"
                )
                clinic_name = doctor.get("clinic", "")
                if clinic_name:
                    st.write(f"Clinic: {clinic_name}")
                if doctor.get("url"):
                    st.markdown(f"[Profile Link]({doctor['url']})")
        else:
            st.info("No doctor results found.")

    st.markdown("### Ayurvedic Medicine Info")
    ayurvedic_remedy = st.text_input("Enter Ayurvedic remedy", placeholder="Ashwagandha")
    if st.button("Get Ayurvedic Info", key="ayurveda_info"):
        info = indian_health.get_ayurvedic_info(ayurvedic_remedy)
        if info:
            st.markdown(f"**{info.get('name', 'Unknown Remedy')}**")
            st.write(info.get("uses", "No usage information available."))

            forms = info.get("common_forms", [])
            if forms:
                st.write("Common forms: " + ", ".join(str(item) for item in forms))

            cautions = info.get("cautions", [])
            if cautions:
                st.warning("Cautions: " + " | ".join(str(item) for item in cautions))

            evidence_note = info.get("evidence_note", "")
            if evidence_note:
                st.caption(f"Evidence note: {evidence_note}")
        else:
            st.info("No Ayurvedic information found for the provided remedy.")

    st.markdown("### Indian Medication Database (MongoDB)")
    db_search = st.text_input("Search stored Indian medications", placeholder="Paracetamol")
    stored_records = list_indian_medications(search=db_search, source="", limit=50)
    if stored_records:
        st.dataframe(pd.DataFrame(stored_records), use_container_width=True)
    else:
        st.info("No Indian medication records stored yet.")
