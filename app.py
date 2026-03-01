import streamlit as st
from medication_service import add_medication, get_all_medications, delete_medication
from datetime import datetime

st.set_page_config(page_title="Healthcare AI Agent", page_icon="🏥")

st.title("🏥 Healthcare Monitoring AI Agent")

menu = st.sidebar.selectbox("Navigation", ["Add Medication", "View Medications"])

# ---------------- ADD MEDICATION ---------------- #

if menu == "Add Medication":

    st.subheader("➕ Add New Medication")

    name = st.text_input("Medicine Name")
    dosage = st.text_input("Dosage (e.g., 500mg)")
    time = st.time_input("Time to Take")
    frequency = st.selectbox("Frequency", ["Daily", "Weekly"])
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    if st.button("Save Medication"):
        if name and dosage:
            add_medication(name, dosage, str(time), frequency, start_date, end_date)
            st.success("Medication added successfully!")
        else:
            st.error("Please fill all required fields.")

# ---------------- VIEW MEDICATIONS ---------------- #

elif menu == "View Medications":

    st.subheader("📋 Your Medications")

    medications = get_all_medications()

    if not medications:
        st.info("No medications added yet.")

    for med in medications:
        col1, col2 = st.columns([4, 1])

        with col1:
            st.write(
                f"💊 **{med['name']}** | {med['dosage']} | {med['time']} | {med['frequency']}"
            )

        with col2:
            if st.button("Delete", key=str(med["_id"])):
                delete_medication(str(med["_id"]))
                st.rerun()


# ---------------- REMINDER LOGIC ---------------- #

current_time = datetime.now().strftime("%H:%M:%S")

for med in get_all_medications():
    if med["time"] == current_time:
        st.warning(f"⏰ Time to take {med['name']} - {med['dosage']}")