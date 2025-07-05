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
    meetings_df = pd.DataFrame(columns=["Team Name", "Point of discussion", "Severity (High/Low)", "Responsibility", "Target date", "Status (Done/Pending)", "Remarks"])

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
    
    with st.container():
        # First row: Team Name, Responsibility
        row1_col1, row1_col2 = st.columns([1.5, 1.5])
        with row1_col1:
            team_name = st.selectbox("Team Name", team_names)
        with row1_col2:
            responsibility_names = attendance_df[attendance_df["Team Name"] == team_name]["Name"].dropna().unique().tolist()
            responsibility = st.selectbox("Responsibility", responsibility_names)

        # Second row: Point of Discussion, Remarks
        row2_col1, row2_col2 = st.columns([2, 2])
        with row2_col1:
            point_of_discussion = st.text_area("Point of discussion")
        with row2_col2:
            remarks = st.text_area("Remarks")

        # Third row: Severity, Target Date, Status
        row3_col1, row3_col2, row3_col3 = st.columns([1, 1, 1])
        with row3_col1:
            severity = st.selectbox("Severity (High/Low)", ["High", "Low"])
        with row3_col2:
            target_date = st.date_input("Target date")
        with row3_col3:
            status = st.selectbox("Status (Done/Pending)", ["Done", "Pending"])

        if st.button("Save Meeting"):
            new_meeting = pd.DataFrame({
                "Team Name": [team_name],
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
    st.markdown("</div>", unsafe_allow_html=True)

# --- Function to View Meetings ---
def view_meetings():
    st.subheader("📋 View Meetings")
    status_filter = st.selectbox("Filter by Status", ["All", "Done", "Pending"])
    if status_filter != "All":
        filtered_meetings = meetings_df[meetings_df["Status (Done/Pending)"] == status_filter].copy()
    else:
        filtered_meetings = meetings_df.copy()

    # Editable Status column (Done/Pending) for each row
    if not filtered_meetings.empty:
        # Add header row
        header_cols = st.columns([2,2,1.5,2,2,2,2])
        header_cols[0].markdown('**Team Name**')
        header_cols[1].markdown('**Point of discussion**')
        header_cols[2].markdown('**Severity (High/Low)**')
        header_cols[3].markdown('**Responsibility**')
        header_cols[4].markdown('**Target date**')
        header_cols[5].markdown('**Status (Done/Pending)**')
        header_cols[6].markdown('**Remarks**')
        edited_status = []
        for idx, row in filtered_meetings.iterrows():
            cols = st.columns([2,2,1.5,2,2,2,2])
            cols[0].write(row["Team Name"])
            cols[1].write(row["Point of discussion"])
            cols[2].write(row["Severity (High/Low)"])
            cols[3].write(row["Responsibility"])
            cols[4].write(row["Target date"])
            # Editable dropdown for status, no label
            new_status = cols[5].selectbox(" ", ["Done", "Pending"], index=0 if row["Status (Done/Pending)"]=="Done" else 1, key=f"status_{idx}", label_visibility="collapsed")
            edited_status.append(new_status)
            cols[6].write(row["Remarks"])
        if st.button("Save Status Changes"):
            filtered_meetings["Status (Done/Pending)"] = edited_status
            # Update the main DataFrame and save
            for idx, new_stat in zip(filtered_meetings.index, edited_status):
                meetings_df.at[idx, "Status (Done/Pending)"] = new_stat
            meetings_df.to_csv(meeting_path, index=False)
            st.success("Status updated!")
    else:
        st.info("No meetings found for the selected filter.")

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
