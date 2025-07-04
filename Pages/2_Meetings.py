import streamlit as st
import pandas as pd
import os
from datetime import date
import pathlib
import numpy as np

# Paths
meeting_path = r"E:\internship work\Zips\KFA GRT TF Logbook\data\processed\Database\Meeting_Table.csv"
attendance_data_path = r"E:\internship work\Zips\KFA GRT TF Logbook\data\processed\Database\attendance_data.csv"

# MoM CSV path (in script directory)
mom_file = str(pathlib.Path(__file__).parent.resolve() / "data/mom_records.csv")

# Load Data
try:
    meetings_df = pd.read_csv(meeting_path)
except FileNotFoundError:
    meetings_df = pd.DataFrame(columns=["Team Name", "Audit Level", "Point of discussion", "Severity (High/Low)", "Responsibility", "Target date", "Status (Done/Pending)", "Remarks"])

try:
    attendance_df = pd.read_csv(attendance_data_path)
    team_names = attendance_df["Team Name"].dropna().unique().tolist()
except FileNotFoundError:
    attendance_df = pd.DataFrame(columns=["Team Name", "Name"])
    team_names = []

# Page Config
st.set_page_config(page_title="Meetings Tracker", layout="wide")
st.title("📅 Meetings Tracker")

# --- Function to Add New Meeting ---
def add_meeting():
    st.subheader("➕ Add New Meeting")

    col0, col1, col2, col3 = st.columns(4)
    with col0:
        team_name = st.selectbox("Team Name", team_names)
        audit_level = st.selectbox("Audit Level", ["L1 audit", "L2 audit", "L3 audit", "Monthly"])
    with col1:
        point_of_discussion = st.text_area("Point of discussion")
        severity = st.selectbox("Severity (High/Low)", ["High", "Low"])
    with col2:
        # Filter names for selected team
        responsibility_names = attendance_df[attendance_df["Team Name"] == team_name]["Name"].dropna().unique().tolist()
        responsibility = st.selectbox("Responsibility", responsibility_names)
        target_date = st.date_input("Target date")
    with col3:
        status = st.selectbox("Status (Done/Pending)", ["Done", "Pending"])
        remarks = st.text_area("Remarks")

    if st.button("Save Meeting"):
        new_meeting = pd.DataFrame({
            "Team Name": [team_name],
            "Audit Level": [audit_level],
            "Point of discussion": [point_of_discussion],
            "Severity (High/Low)": [severity],
            "Responsibility": [responsibility],
            "Target date": [target_date],
            "Status (Done/Pending)": [status],
            "Remarks": [remarks]
        })
        updated_meetings_df = pd.concat([meetings_df, new_meeting], ignore_index=True)
        updated_meetings_df.to_csv(meeting_path, index=False)
        st.success(f"✅ Meeting added successfully!")

# --- Function to View Meetings ---
def view_meetings():
    st.subheader("📋 View Meetings")
    status_filter = st.selectbox("Filter by Status", ["All", "Done", "Pending"])
    if status_filter != "All":
        filtered_meetings = meetings_df[meetings_df["Status (Done/Pending)"] == status_filter]
    else:
        filtered_meetings = meetings_df
    st.dataframe(filtered_meetings)

# --- MoM Section ---
st.header("Minutes of Meeting (MoM)")
mom_mode = st.radio("Select MoM Mode", ["Single Point", "Multiple Point"])

if mom_mode == "Single Point":
    meeting_tab, view_tab = st.tabs(["Add New Meeting", "View Meetings"])
    with meeting_tab:
        add_meeting()
    with view_tab:
        view_meetings()
else:
    st.subheader("Edit Meeting Data (Multiple Point)")
    # Show meetings_df as editable table
    editable_meetings = st.data_editor(
        meetings_df,
        num_rows="dynamic",
        use_container_width=True,
        key="meeting_multi_editor"
    )
    if st.button("Save Changes to Meetings"):
        editable_meetings.to_csv(meeting_path, index=False)
        st.success("Meeting records updated!")

# Robust date handling
for col in ["Target date"]:
    if col in meetings_df.columns:
        # Try to parse dates, set errors to NaT, then convert to string in YYYY-MM-DD or empty
        meetings_df[col] = pd.to_datetime(meetings_df[col], errors='coerce').dt.strftime('%Y-%m-%d')
        meetings_df[col] = meetings_df[col].replace('NaT', '')
