import pandas as pd
import streamlit as st

from src.chatbot import HealthChatbot
from src.config import get_groq_api_key, get_llm_provider, get_use_llm
from src.data_io import (
    export_metrics_to_csv,
    export_metrics_to_json,
    export_metrics_to_xml,
    parse_metrics_csv_text,
    parse_metrics_json_text,
    parse_metrics_xml_text,
)
from src.database import (
    add_medical_history_record,
    add_nutrition_log,
    add_health_metric,
    add_health_goal,
    add_medication,
    deactivate_health_goal,
    deactivate_medication,
    init_db,
    list_indian_medications,
    list_insurance_profiles,
    list_medical_history,
    list_nutrition_logs,
    list_regional_preferences,
    list_all_metrics,
    list_health_goals,
    list_medications,
    list_recent_metrics,
    upsert_insurance_profile,
    upsert_indian_medication,
    upsert_regional_preference,
)
from src.health_parser import parse_metric_input
from src.indian_health import IndianHealthService
from src.medical_lookup import get_medical_info
from src.medication_interactions import check_interactions
from src.medication import upcoming_reminders
from src.reporting import generate_health_report
from src.validators import (
    ValidationError,
    validate_medication,
    validate_nutrition_log,
    validate_insurance_profile,
    validate_medical_history,
    validate_regional_preference,
    validate_health_metric,
    validate_health_goal,
)

st.set_page_config(page_title="Healthcare AI Agent - Track A", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --app-bg: #f4f7fb;
        --surface: #ffffff;
        --ink: #1f2937;
        --muted: #5b6675;
        --line: #d8e1eb;
        --brand: #1f4e79;
        --brand-soft: #eaf2fa;
    }
    .stApp {
        background: var(--app-bg);
    }
    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.4rem;
        max-width: 1200px;
    }
    h1, h2, h3, h4 {
        letter-spacing: 0.1px;
        color: var(--ink);
    }
    .app-header {
        background: linear-gradient(135deg, #ffffff 0%, #f6f9fc 100%);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.9rem;
    }
    .app-title {
        font-size: 1.45rem;
        font-weight: 700;
        color: var(--ink);
        margin-bottom: 0.2rem;
    }
    .app-subtitle {
        font-size: 0.92rem;
        color: var(--muted);
        margin: 0;
    }
    .status-badge {
        display: inline-block;
        color: var(--brand);
        background: var(--brand-soft);
        border: 1px solid #c8dff5;
        border-radius: 999px;
        padding: 0.3rem 0.65rem;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .formal-card {
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 0.7rem 0.95rem;
        background: var(--surface);
        margin-bottom: 0.8rem;
    }
    .section-title {
        font-size: 1.15rem;
        font-weight: 650;
        color: var(--ink);
        margin-bottom: 0.3rem;
    }
    .section-note {
        color: var(--muted);
        font-size: 0.88rem;
        margin-bottom: 0.35rem;
    }
    .sidebar-note {
        font-size: 0.86rem;
        color: #334e68;
        line-height: 1.4;
    }
    [data-testid="stSidebar"] {
        background: #eef3f8;
    }
    .stButton > button {
        border-radius: 8px;
        border: 1px solid #bdd1e6;
    }
    .app-footer {
        margin-top: 1.2rem;
        border-top: 1px solid var(--line);
        color: var(--muted);
        font-size: 0.82rem;
        padding-top: 0.7rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

init_db()
indian_health = IndianHealthService()

if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = get_llm_provider()
if "use_llm" not in st.session_state:
    st.session_state.use_llm = get_use_llm()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def build_chatbot() -> HealthChatbot:
    return HealthChatbot(
        provider="groq",
        groq_api_key=get_groq_api_key() or None,
        use_llm=bool(st.session_state.get("use_llm") or get_groq_api_key()),
    )


def is_groq_ready() -> bool:
    return bool(get_groq_api_key())

st.markdown(
    """
    <div class="app-header">
        <div class="app-title">Healthcare Monitoring AI Agent</div>
        <p class="app-subtitle">Professional health tracking dashboard for medication, metrics, goals, reports, and Indian health workflows.</p>
        <span class="status-badge">Track A • Production UI</span>
    </div>
    """,
    unsafe_allow_html=True,
)

medications = list_medications(active_only=True)
all_medications = list_medications(active_only=False)
alerts = upcoming_reminders(medications, window_minutes=60)

with st.sidebar:
    st.header("Navigation Panel")
    selected_section = st.radio(
        "Select Workspace",
        [
            "Health Dashboard",
            "Chatbot Panel",
            "Medication Scheduler",
            "Health Metrics",
            "Goals & Progress",
            "Reports",
            "Indian Health",
        ],
        index=0,
    )

    st.divider()
    st.subheader("Quick Snapshot")
    st.metric("Active Medications", len(medications))
    st.metric("Active Goals", len(list_health_goals(active_only=True)))
    st.metric("Health Logs", len(list_all_metrics()))

    st.divider()
    st.subheader("Reminder Window")
    if alerts:
        for alert in alerts[:5]:
            st.warning(alert)
    else:
        st.success("No reminders due in the next hour")

    st.divider()
    st.markdown("<div class='sidebar-note'>Educational assistant only. Always consult licensed medical professionals for diagnosis and treatment.</div>", unsafe_allow_html=True)

st.markdown(f"<div class='formal-card'><b>Current Section:</b> {selected_section}</div>", unsafe_allow_html=True)

if selected_section == "Health Dashboard":
    st.markdown("<div class='section-title'>Health Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-note'>Overview of key health indicators, engagement, and evidence-backed information lookup.</div>", unsafe_allow_html=True)
    all_metrics_dashboard = list_all_metrics()
    metrics_df = pd.DataFrame(all_metrics_dashboard, columns=["metric_name", "metric_value", "unit", "recorded_at"])

    total_metrics = len(all_metrics_dashboard)
    total_active_medications = len(medications)
    total_goals = len(list_health_goals(active_only=True))
    adherence_rate = 0.0
    if all_medications:
        completed = len([item for item in all_medications if int(item.get("active", 1)) == 0])
        adherence_rate = (completed / len(all_medications)) * 100

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Health Logs", total_metrics)
    m2.metric("Active Medications", total_active_medications)
    m3.metric("Active Goals", total_goals)
    m4.metric("Medication Adherence", f"{adherence_rate:.1f}%")

    if not metrics_df.empty:
        metrics_df["recorded_at"] = pd.to_datetime(metrics_df["recorded_at"], errors="coerce")
        metrics_df = metrics_df.dropna(subset=["recorded_at"])
        trend_df = metrics_df.sort_values("recorded_at")

        st.markdown("### Comprehensive Metrics Visualization")
        c1, c2 = st.columns(2)
        with c1:
            avg_by_metric = (
                trend_df.groupby("metric_name", as_index=False)["metric_value"].mean().rename(columns={"metric_value": "avg_value"})
            )
            st.caption("Average values by metric")
            st.bar_chart(avg_by_metric.set_index("metric_name")["avg_value"])

        with c2:
            latest_by_metric = trend_df.sort_values("recorded_at").groupby("metric_name", as_index=False).tail(1)
            latest_table = latest_by_metric[["metric_name", "metric_value", "unit", "recorded_at"]].sort_values("metric_name")
            st.caption("Latest recorded values")
            st.dataframe(latest_table, use_container_width=True)

    st.divider()
    st.markdown("### Health Assistant")
    question = st.text_input("Ask a health-related question", placeholder="How can I track my steps better?")
    if st.button("Get Guidance", type="primary"):
        response = build_chatbot().answer(question)
        st.write(response)

    st.divider()
    st.markdown("### Medical Information Lookup")
    lookup_topic = st.text_input("Search medical topic", placeholder="hypertension")
    if st.button("Lookup Medical Info"):
        if not lookup_topic.strip():
            st.error("Please enter a topic to look up.")
        else:
            info = get_medical_info(lookup_topic)
            st.markdown(f"**{info.get('title', 'Medical Topic')}**")
            st.write(info.get("summary", ""))

            guidance = info.get("guidance", [])
            if guidance:
                st.markdown("Recommended actions:")
                for item in guidance:
                    st.write(f"- {item}")

            citations = info.get("citations", [])
            if citations:
                st.markdown("Reliable source citations:")
                for source in citations:
                    st.write(f"- {source}")

if selected_section == "Chatbot Panel":
    st.markdown("<div class='section-title'>Chatbot Panel</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-note'>Dedicated conversational workspace for safe health guidance, reminders, and quick follow-up questions.</div>", unsafe_allow_html=True)

    chat_col, settings_col = st.columns([2.2, 1])

    with settings_col:
        st.markdown("### Model Settings")
        if is_groq_ready():
            st.success("Groq API connected")
        else:
            st.warning("Add GROQ_API_KEY to .env to enable live answers")
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

        st.divider()
        st.markdown("### Quick Prompts")
        quick_prompts = [
            "How can I improve medication adherence?",
            "What should I track for daily wellness?",
            "When should I seek urgent medical help?",
        ]
        for prompt_text in quick_prompts:
            if st.button(prompt_text, key=f"quick_{prompt_text}"):
                st.session_state.chat_history.append({"role": "user", "content": prompt_text})
                st.rerun()

    with chat_col:
        st.markdown("### Conversation")
        st.caption("Use the panel to ask health-related questions. The assistant keeps responses brief and non-diagnostic.")

        for entry in st.session_state.chat_history:
            with st.chat_message(entry["role"]):
                st.markdown(entry["content"])

        prompt = st.chat_input("Ask about medications, metrics, reminders, or general wellness")
        if prompt:
            chatbot = build_chatbot()
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                response = chatbot.answer(prompt)
                st.markdown(response)

            st.session_state.chat_history.append({"role": "assistant", "content": response})

if selected_section == "Medication Scheduler":
    st.markdown("<div class='section-title'>Medication Scheduler</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-note'>Create medication plans, track completion, and review interaction/adherence insights.</div>", unsafe_allow_html=True)
    with st.form("medication_form"):
        c1, c2 = st.columns(2)
        med_name = c1.text_input("Medicine name")
        dosage = c2.text_input("Dosage", placeholder="500 mg")
        c3, c4 = st.columns(2)
        schedule = c3.time_input("Schedule time")
        notes = c4.text_input("Notes (optional)")
        submitted = st.form_submit_button("Add Medication", type="primary")

    if submitted:
        try:
            if not med_name.strip() or not dosage.strip():
                st.error("Medicine name and dosage are required.")
            else:
                validated_med = validate_medication(
                    name=med_name,
                    dosage=dosage,
                    schedule=schedule.strftime("%H:%M"),
                    active=True
                )
                add_medication(
                    validated_med["name"],
                    validated_med["dosage"],
                    validated_med["schedule"],
                    notes.strip()
                )
                st.success("✅ Medication schedule added successfully.")
                st.rerun()
        except ValidationError as e:
            st.error(f"❌ Medication validation failed: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error adding medication: {str(e)}")

    st.divider()
    st.markdown("### Active Schedules")
    for medication in medications:
        cols = st.columns([4, 2, 2, 1])
        cols[0].write(f"**{medication['name']}** ({medication['dosage']})")
        cols[1].write(medication["schedule_time"])
        cols[2].write(medication["notes"] or "-")
        if cols[3].button("Done", key=f"done_{medication['id']}"):
            deactivate_medication(medication["id"])
            st.rerun()

    st.divider()
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

    st.divider()
    st.markdown("### Adherence Report")
    if all_medications:
        medication_df = pd.DataFrame(all_medications)
        medication_df["status"] = medication_df["active"].apply(lambda value: "Active" if int(value) == 1 else "Completed")
        completed_count = int((medication_df["status"] == "Completed").sum())
        adherence_pct = (completed_count / len(medication_df)) * 100 if len(medication_df) else 0.0

        st.progress(min(adherence_pct / 100.0, 1.0), text=f"Adherence (completed schedules): {adherence_pct:.1f}%")
        st.dataframe(
            medication_df[["name", "dosage", "schedule_time", "notes", "status", "created_at"]],
            use_container_width=True,
        )
    else:
        st.info("No medication records available for adherence reporting.")

if selected_section == "Health Metrics":
    st.markdown("<div class='section-title'>Health Metrics</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-note'>Capture structured health records, visualize trends, and manage multi-format imports/exports.</div>", unsafe_allow_html=True)
    with st.form("metric_form"):
        c1, c2, c3 = st.columns([2, 1, 2])
        metric_name = c1.selectbox("Metric", ["steps", "heart_rate", "weight", "sleep_hours", "water_intake"])
        metric_value = c2.text_input("Value", placeholder="6500")
        unit = c3.text_input("Unit", placeholder="steps / bpm / kg / hours / liters")
        metric_submit = st.form_submit_button("Save Metric", type="primary")

    if metric_submit:
        try:
            clean_name, value, clean_unit, timestamp = validate_health_metric(metric_name, metric_value, unit)
            add_health_metric(clean_name, value, clean_unit, timestamp)
            st.success("✅ Health metric saved successfully.")
            st.rerun()
        except ValidationError as error:
            st.error(f"❌ Metric validation failed: {str(error)}")
        except ValueError as error:
            st.error(f"❌ Invalid metric value: {str(error)}")
        except Exception as error:
            st.error(f"❌ Error saving health metric: {str(error)}")

    st.divider()
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
                    try:
                        add_health_metric(
                            str(item["metric_name"]),
                            float(item["metric_value"]),
                            str(item["unit"]),
                            str(item["recorded_at"]),
                        )
                    except (ValidationError, ValueError) as e:
                        st.warning(f"Skipped row: {str(e)}")
                        continue

                if parsed_metrics:
                    st.success(f"✅ Imported {len(parsed_metrics)} fitness records successfully.")
                    st.rerun()
                else:
                    st.info("No rows found in uploaded file.")
            except ValueError as error:
                st.error(f"❌ File format error. Please ensure file contains valid metric data. Details: {str(error)}")
            except Exception as error:
                st.error(f"❌ Could not import file. Details: {str(error)}")

    records = list_recent_metrics(limit=50)
    if records:
        dataframe = pd.DataFrame(records, columns=["metric_name", "metric_value", "unit", "recorded_at"])
        st.dataframe(dataframe, use_container_width=True)

        st.divider()
        st.markdown("### Recent Trend")
        metric_filter = st.selectbox("Choose metric", sorted(dataframe["metric_name"].unique()))
        filtered = dataframe[dataframe["metric_name"] == metric_filter].copy()
        filtered["recorded_at"] = pd.to_datetime(filtered["recorded_at"])
        filtered = filtered.sort_values("recorded_at")
        st.line_chart(filtered.set_index("recorded_at")["metric_value"])

        st.divider()
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

if selected_section == "Goals & Progress":
    st.markdown("<div class='section-title'>Goals and Progress Monitoring</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-note'>Define measurable targets and monitor achievement across latest, daily, or monthly views.</div>", unsafe_allow_html=True)
    progress_mode = st.radio(
        "Progress Mode",
        ["Latest", "Daily", "Monthly"],
        horizontal=True,
        help="Latest uses the most recent value. Daily and Monthly use summed values for the selected period.",
    )

    with st.form("goal_form"):
        c1, c2, c3 = st.columns([2, 1, 2])
        goal_metric = c1.selectbox(
            "Goal Metric",
            ["steps", "heart_rate", "weight", "sleep_hours", "water_intake"],
        )
        goal_target = c2.number_input("Target Value", min_value=0.0, step=1.0, format="%.2f")
        goal_unit = c3.text_input("Unit", placeholder="steps / bpm / kg / hours / liters")
        goal_submit = st.form_submit_button("Add Goal", type="primary")

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
        progress_rows: list[dict] = []
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
            progress_rows.append(
                {
                    "metric_name": metric_name,
                    "current_value": round(current_value, 2),
                    "target_value": round(target_value, 2),
                    "unit": goal["unit"],
                    "progress_percent": round(progress * 100, 1),
                }
            )
            if cols[3].button("Close", key=f"goal_close_{goal['id']}"):
                deactivate_health_goal(goal["id"])
                st.rerun()

        if progress_rows:
            progress_df = pd.DataFrame(progress_rows)
            st.markdown("### Progress Monitoring Snapshot")
            st.dataframe(progress_df, use_container_width=True)
    else:
        st.info("No active goals yet.")

if selected_section == "Reports":
    st.markdown("<div class='section-title'>Reports and Exports</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-note'>Generate comprehensive reports and export medication and fitness datasets.</div>", unsafe_allow_html=True)
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

    st.divider()
    st.markdown("### Export: Medication History")
    if all_medications:
        meds_export_df = pd.DataFrame(all_medications)
        meds_export_df["status"] = meds_export_df["active"].apply(lambda value: "Active" if int(value) == 1 else "Completed")
        med_csv = meds_export_df.to_csv(index=False)
        st.download_button(
            "Download Medication History (CSV)",
            data=med_csv,
            file_name="medication_history.csv",
            mime="text/csv",
        )
    else:
        st.info("No medication history available for export.")

    st.markdown("### Export: Fitness Data (Latest 100)")
    fitness_rows = list_recent_metrics(limit=100)
    if fitness_rows:
        fit_csv = pd.DataFrame(fitness_rows).to_csv(index=False)
        st.download_button(
            "Download Fitness Data (CSV)",
            data=fit_csv,
            file_name="fitness_data_latest_100.csv",
            mime="text/csv",
        )

if selected_section == "Indian Health":
    st.markdown("<div class='section-title'>Indian Personal Health Assistant</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-note'>Unified interface for medicine lookup, regional doctors, nutrition planning, insurance, and history records.</div>", unsafe_allow_html=True)

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

    st.divider()
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

    st.divider()
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

    st.divider()
    st.markdown("### Indian Medication Database")
    db_search = st.text_input("Search stored Indian medications", placeholder="Paracetamol")
    stored_records = list_indian_medications(search=db_search, source="", limit=50)
    if stored_records:
        st.dataframe(pd.DataFrame(stored_records), use_container_width=True)
    else:
        st.info("No Indian medication records stored yet.")

    st.divider()
    st.markdown("### Indian Dietary Recommendations and Nutrition Tracking")
    with st.form("indian_diet_form"):
        c1, c2, c3 = st.columns(3)
        diet_region = c1.selectbox(
            "Region",
            ["North India", "South India", "West India", "East India", "Central India"],
        )
        health_goal = c2.selectbox(
            "Health Goal",
            ["General Wellness", "Weight Loss", "Diabetes Management", "Heart Health", "Muscle Gain"],
        )
        diet_preference = c3.selectbox(
            "Diet Preference",
            ["Balanced", "Vegetarian", "Non-Vegetarian", "Jain", "Vegan"],
        )
        r1, r2, r3 = st.columns(3)
        meal_type = r1.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        food_item = r2.text_input("Food Item", placeholder="e.g., Idli with sambar")
        quantity = r3.text_input("Quantity", placeholder="e.g., 2 pieces")
        n1, n2, n3, n4, n5 = st.columns(5)
        calories = n1.number_input("Calories", min_value=0.0, value=250.0, step=10.0)
        protein_g = n2.number_input("Protein (g)", min_value=0.0, value=8.0, step=1.0)
        carbs_g = n3.number_input("Carbs (g)", min_value=0.0, value=30.0, step=1.0)
        fats_g = n4.number_input("Fats (g)", min_value=0.0, value=6.0, step=1.0)
        fiber_g = n5.number_input("Fiber (g)", min_value=0.0, value=3.0, step=0.5)
        nutrition_notes = st.text_input("Notes", placeholder="Post-workout meal")
        diet_submit = st.form_submit_button("Save Meal and Get Recommendations", type="primary")

    if diet_submit:
        try:
            if not food_item.strip():
                st.error("Food item is required.")
            else:
                # Validate nutrition data
                validated_nutrition = validate_nutrition_log(
                    meal_type=meal_type,
                    calories=str(calories),
                    protein=str(protein_g),
                    carbs=str(carbs_g),
                    fat=str(fats_g),
                    meal_date=pd.Timestamp.utcnow().date().isoformat(),
                    region=diet_region
                )
                
                add_nutrition_log(
                    meal_date=validated_nutrition["meal_date"],
                    meal_type=validated_nutrition["meal_type"],
                    region=validated_nutrition["region"],
                    food_item=food_item.strip(),
                    quantity=quantity.strip(),
                    calories=validated_nutrition["calories"],
                    protein_g=validated_nutrition["protein"],
                    carbs_g=validated_nutrition["carbs"],
                    fats_g=validated_nutrition["fat"],
                    fiber_g=float(fiber_g),
                    notes=nutrition_notes.strip(),
                )
                st.success("✅ Nutrition log saved successfully.")

                try:
                    recommendation = indian_health.get_indian_dietary_recommendations(
                        region=diet_region,
                        health_goal=health_goal,
                        diet_preference=diet_preference,
                    )
                    st.markdown("#### Recommended Foods")
                    st.write(", ".join(recommendation.get("recommended_foods", [])) or "No recommendations available.")
                    st.caption("Limit: " + ", ".join(recommendation.get("avoid_or_limit", [])))
                    st.info(recommendation.get("hydration_tip", ""))
                    st.caption(recommendation.get("disclaimer", ""))
                except Exception as rec_error:
                    st.warning(f"Could not fetch recommendations: {str(rec_error)}")
        except ValidationError as e:
            st.error(f"❌ Nutrition data validation failed: {str(e)}")
        except ValueError as e:
            st.error(f"❌ Invalid nutrition value: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error saving nutrition log: {str(e)}")

    nutrition_region_filter = st.text_input("Filter nutrition logs by region", placeholder="South")
    nutrition_logs = list_nutrition_logs(patient_region=nutrition_region_filter, limit=100)
    if nutrition_logs:
        st.dataframe(pd.DataFrame(nutrition_logs), use_container_width=True)

    st.divider()
    st.markdown("### Indian Health Insurance and Medical History")
    with st.form("insurance_form"):
        i1, i2, i3 = st.columns(3)
        patient_name = i1.text_input("Patient Name", placeholder="Amit Sharma")
        insurer = i2.text_input("Insurer", placeholder="Star Health")
        policy_number = i3.text_input("Policy Number", placeholder="POL123456")
        i4, i5, i6, i7 = st.columns(4)
        policy_type = i4.selectbox("Policy Type", ["Individual", "Family Floater", "Senior Citizen", "Corporate"])
        sum_insured = i5.number_input("Sum Insured (INR)", min_value=0.0, value=500000.0, step=10000.0)
        expiry_date = i6.date_input("Policy Expiry Date")
        network_hospitals = i7.text_input("Network Hospitals", placeholder="Apollo, Fortis, Manipal")
        insurance_submit = st.form_submit_button("Save Insurance Profile", type="primary")

    if insurance_submit:
        try:
            if not patient_name.strip() or not insurer.strip() or not policy_number.strip():
                st.error("Patient name, insurer, and policy number are required.")
            else:
                validated_insurance = validate_insurance_profile(
                    patient_name=patient_name,
                    policy_number=policy_number,
                    provider=insurer,
                    policy_type=policy_type,
                    coverage_limit=str(sum_insured)
                )
                upsert_insurance_profile(
                    patient_name=validated_insurance["patient_name"],
                    insurer=validated_insurance["provider"],
                    policy_number=validated_insurance["policy_number"],
                    policy_type=validated_insurance["policy_type"],
                    sum_insured=validated_insurance["coverage_limit"],
                    expiry_date=expiry_date.isoformat(),
                    network_hospitals=network_hospitals.strip(),
                )
                st.success("✅ Insurance profile saved successfully.")
        except ValidationError as e:
            st.error(f"❌ Insurance validation failed: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error saving insurance profile: {str(e)}")

    with st.form("medical_history_form"):
        h1, h2, h3 = st.columns(3)
        mh_patient_name = h1.text_input("Patient Name (History)", placeholder="Amit Sharma")
        condition_name = h2.text_input("Condition", placeholder="Hypertension")
        diagnosis_date = h3.date_input("Diagnosis Date")
        h4, h5, h6 = st.columns(3)
        current_medications = h4.text_input("Current Medications", placeholder="Amlodipine")
        allergies = h5.text_input("Allergies", placeholder="Penicillin")
        procedures_done = h6.text_input("Procedures", placeholder="Angioplasty")
        history_notes = st.text_input("Notes", placeholder="Regular BP monitoring")
        history_submit = st.form_submit_button("Add Medical History Record", type="primary")

    if history_submit:
        try:
            if not mh_patient_name.strip() or not condition_name.strip():
                st.error("Patient name and condition are required.")
            else:
                validated_history = validate_medical_history(
                    condition=condition_name,
                    diagnosis_date=diagnosis_date.isoformat(),
                    treatment=current_medications.strip()
                )
                add_medical_history_record(
                    patient_name=mh_patient_name.strip(),
                    condition_name=validated_history["condition"],
                    diagnosis_date=validated_history["diagnosis_date"],
                    medications=current_medications.strip(),
                    allergies=allergies.strip(),
                    procedures_done=procedures_done.strip(),
                    notes=history_notes.strip(),
                )
                st.success("✅ Medical history record saved successfully.")
        except ValidationError as e:
            st.error(f"❌ Medical history validation failed: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error saving medical history: {str(e)}")

    patient_filter = st.text_input("Filter insurance/history by patient", placeholder="Amit")
    insurance_rows = list_insurance_profiles(patient_name=patient_filter, limit=50)
    history_rows = list_medical_history(patient_name=patient_filter, limit=100)
    if insurance_rows:
        st.markdown("#### Insurance Profiles")
        st.dataframe(pd.DataFrame(insurance_rows), use_container_width=True)
    if history_rows:
        st.markdown("#### Medical History")
        st.dataframe(pd.DataFrame(history_rows), use_container_width=True)

    st.divider()
    st.markdown("### Regional Health Preferences and Local Doctor Networks")
    with st.form("regional_pref_form"):
        p1, p2, p3 = st.columns(3)
        rp_patient = p1.text_input("Patient Name (Preferences)", placeholder="Amit Sharma")
        rp_state = p2.text_input("State", placeholder="Karnataka")
        rp_city = p3.text_input("City", placeholder="Bengaluru")
        p4, p5, p6, p7 = st.columns(4)
        rp_language = p4.selectbox(
            "Preferred Language",
            ["English", "Hindi", "Kannada", "Tamil", "Telugu", "Malayalam", "Marathi", "Bengali"],
        )
        rp_diet = p5.selectbox("Diet Preference", ["Balanced", "Vegetarian", "Non-Vegetarian", "Jain", "Vegan"])
        rp_mode = p6.selectbox("Consultation Mode", ["In-person", "Teleconsultation", "Either"])
        rp_budget = p7.number_input("Max Consultation Budget (INR)", min_value=0.0, value=800.0, step=50.0)
        rp_specialties = st.text_input("Preferred Specialties", placeholder="General Physician, Diabetologist")
        pref_submit = st.form_submit_button("Save Regional Preferences", type="primary")

    if pref_submit:
        try:
            if not rp_patient.strip():
                st.error("Patient name is required.")
            else:
                validated_pref = validate_regional_preference(
                    region=rp_state.strip() or "Not specified",
                    preferred_language=rp_language,
                    preferred_doctor_type=""
                )
                upsert_regional_preference(
                    patient_name=rp_patient.strip(),
                    state=rp_state.strip(),
                    city=rp_city.strip(),
                    preferred_language=validated_pref["preferred_language"],
                    diet_preference=rp_diet,
                    consultation_mode=rp_mode,
                    max_budget_inr=float(rp_budget),
                    preferred_specialties=rp_specialties.strip(),
                )
                st.success("✅ Regional preferences saved successfully.")
        except ValidationError as e:
            st.error(f"❌ Regional preference validation failed: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error saving regional preferences: {str(e)}")

    specialty_query = st.text_input("Search specialty in local network", placeholder="General Physician")
    try:
        local_doctors = indian_health.get_local_doctor_network(
            city=rp_city,
            state=rp_state,
            specialty=specialty_query,
            preferred_language=rp_language,
            max_fee_inr=float(rp_budget),
        )
        practo_local = indian_health.search_practo_doctors(rp_city, specialty_query or "General Physician", limit=5)
    except Exception as e:
        st.error(f"❌ Error fetching doctor networks: {str(e)}")
        local_doctors = []
        practo_local = []

    if local_doctors:
        st.markdown("#### Local Doctor Network")
        st.dataframe(pd.DataFrame(local_doctors), use_container_width=True)
    else:
        st.info("No local doctor network entries match current filters.")

    if practo_local:
        st.markdown("#### Practo Results for Region")
        st.dataframe(pd.DataFrame(practo_local), use_container_width=True)

    pref_filter = st.text_input("Filter saved preferences by patient", placeholder="Amit")
    pref_rows = list_regional_preferences(patient_name=pref_filter, limit=50)
    if pref_rows:
        st.markdown("#### Saved Regional Preferences")
        st.dataframe(pd.DataFrame(pref_rows), use_container_width=True)

st.markdown(
    """
    <div class="app-footer">
        Healthcare Monitoring AI Agent • Track A • Streamlit Professional Interface
    </div>
    """,
    unsafe_allow_html=True,
)
