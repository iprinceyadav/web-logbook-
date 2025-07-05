import streamlit as st
import pandas as pd
import os
from datetime import date

CSV_FILE = "data/processed/Database/audit_data.csv"
AUDIT_LEVELS = ["L1", "L2", "L3", "Monthly Audit"]

st.set_page_config(page_title="Audit Entry & Records", layout="wide")
st.title("Audit Entry & Records")

# Load data
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=[
        "Audit Level", "Point", "Area", "Department", "Responsibility", "Target date", "Status (Done/Pending)", "Remarks"
    ])

# --- Tabs: Add Audit Entry, L1, L2, L3, Monthly ---
tab_add, tab_l1, tab_l2, tab_l3, tab_monthly = st.tabs(["Add Audit Entry", "L1 Audit", "L2 Audit", "L3 Audit", "Monthly Audit"])

# --- Audit Entry Form in Add Audit Entry Tab ---
with tab_add:
    st.header("Add New Audit Entry")
    with st.form("audit_entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            audit_level = st.selectbox("Audit Level", AUDIT_LEVELS)
            point = st.text_area("Point")
            area = st.text_input("Area")
            department = st.text_input("Department")
        with col2:
            target_date = st.date_input("Target date", value=date.today())
            status = st.selectbox("Status (Done/Pending)", ["Done", "Pending"])
            remarks = st.text_area("Remarks")
            responsibility = st.text_input("Responsibility")
        submitted = st.form_submit_button("Submit Entry")
        if submitted:
            new_row = pd.DataFrame([{
                "Audit Level": audit_level,
                "Point": point,
                "Area": area,
                "Department": department,
                "Responsibility": responsibility,
                "Target date": target_date,
                "Status (Done/Pending)": status,
                "Remarks": remarks
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)
            st.success("Audit entry added!")

# --- Tabs to Show Data by Audit Level ---
def show_audit_table(audit_level):
    filtered = df[df["Audit Level"] == audit_level]
    if not filtered.empty:
        st.dataframe(filtered, use_container_width=True)
    else:
        st.info(f"No records found for {audit_level}.")

with tab_l1:
    show_audit_table("L1")
with tab_l2:
    show_audit_table("L2")
with tab_l3:
    show_audit_table("L3")
with tab_monthly:
    show_audit_table("Monthly Audit")
