import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- File Path ---
MEETING_PATH = os.path.join("data", "processed", "Database", "Meeting_Table.csv")

# --- Load Data ---
def load_meeting_data():
    try:
        df = pd.read_csv(MEETING_PATH)
    except Exception:
        df = pd.DataFrame(columns=["Team Name", "Audit Level", "Point of discussion", "Severity (High/Low)", "Responsibility", "Target date", "Status (Done/Pending)", "Remarks"])
    return df

# --- Dashboard ---
st.set_page_config(page_title="📊 Analytical Dashboard", layout="wide")
st.title("📈 Interactive Analytical Dashboard")  # Removed duplicate main heading

# Load data
df_meeting = load_meeting_data()

# --- Display all three charts: bar chart on left, two pie charts stacked on right ---
col1, col2 = st.columns([2, 1])

# 1. Team Name-wise Meeting Count Bar Graph
with col1:
    if not df_meeting.empty and "Team Name" in df_meeting.columns:
        team_counts = df_meeting["Team Name"].value_counts().reset_index()
        team_counts.columns = ["Team Name", "Meeting Count"]
        fig1 = px.bar(team_counts, x="Team Name", y="Meeting Count",title="Team Name-wise Meeting Count", color="Team Name")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("No meeting data or 'Team Name' column not found.")

# 2 & 3. Pie Charts stacked vertically
with col2:
    # Status Pie Chart
    if not df_meeting.empty and "Status (Done/Pending)" in df_meeting.columns:
        status_counts = df_meeting["Status (Done/Pending)"].value_counts().reset_index()
        status_counts.columns = ["Status (Done/Pending)", "Count"]
        fig2 = px.pie(status_counts, names="Status (Done/Pending)", values="Count",title="Meeting Status Distribution", height=300)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No meeting data or 'Status (Done/Pending)' column not found.")
    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)  # Small gap
    # Severity Pie Chart for Pending Meetings
    if not df_meeting.empty and "Status (Done/Pending)" in df_meeting.columns and "Severity (High/Low)" in df_meeting.columns:
        pending_meetings = df_meeting[df_meeting["Status (Done/Pending)"].str.lower() == "pending"]
        if not pending_meetings.empty:
            severity_counts = pending_meetings["Severity (High/Low)"].value_counts().reset_index()
            severity_counts.columns = ["Severity (High/Low)", "Count"]
            fig3 = px.pie(severity_counts, names="Severity (High/Low)", values="Count",title="Severity Distribution for Pending Meetings", height=300)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No pending meetings found.")
    else:
        st.warning("No meeting data or required columns ('Status (Done/Pending)', 'Severity (High/Low)') not found.")

# --- Team Name & Year Filter for FY Person-wise Responsibility Count ---
st.markdown('<span style="font-size:15px;font-weight:600;">Person-wise Responsibility Count</span>', unsafe_allow_html=True)
if not df_meeting.empty and "Team Name" in df_meeting.columns and "Target date" in df_meeting.columns and "Responsibility" in df_meeting.columns:
    df_meeting["Target date"] = pd.to_datetime(df_meeting["Target date"], errors="coerce")
    df_meeting = df_meeting.dropna(subset=["Target date"])  # Remove rows with invalid dates
    df_meeting["Year"] = df_meeting["Target date"].apply(lambda x: x.year if x.month >= 4 else x.year - 1)
    df_meeting["FY"] = df_meeting["Year"].astype(str) + "-" + (df_meeting["Year"]+1).astype(str)

    team_options = sorted(df_meeting["Team Name"].dropna().unique())
    fy_options = sorted(df_meeting["FY"].unique(), reverse=True)

    filter_col1, filter_col2 = st.columns([1,1])
    with filter_col1:
        st.markdown('<span style="font-size:13px;font-weight:500;">Team Name</span>', unsafe_allow_html=True)
        selected_team = st.selectbox(" ", team_options, key="team_select", label_visibility="collapsed")
    with filter_col2:
        st.markdown('<span style="font-size:13px;font-weight:500;">Financial Year (April-March)</span>', unsafe_allow_html=True)
        selected_fy = st.selectbox(" ", fy_options, key="fy_select", label_visibility="collapsed")

    filtered = df_meeting[(df_meeting["Team Name"] == selected_team) & (df_meeting["FY"] == selected_fy)]

    # Group by Responsibility, count occurrences
    resp_counts = filtered["Responsibility"].value_counts().reset_index()
    resp_counts.columns = ["Responsibility", "Count"]

    fig_fy = px.bar(resp_counts, x="Responsibility", y="Count", title=f"Person-wise Responsibility Count for {selected_team} ({selected_fy})")
    st.plotly_chart(fig_fy, use_container_width=True)
else:
    st.info("Meeting data, Team Name, Responsibility, or Target date column not found.")

# --- Stacked Bar Chart: Pending Responsibility Count for Selected Person (Stacked by Severity, by Due Date) ---
st.markdown('<span style="font-size:15px;font-weight:600;">Pending Responsibility Count for Selected Person by Due Date (Stacked by Severity)</span>', unsafe_allow_html=True)
if not df_meeting.empty and "Target date" in df_meeting.columns and "Severity (High/Low)" in df_meeting.columns and "Responsibility" in df_meeting.columns and "Team Name" in df_meeting.columns:
    # Use the same selected_team and selected_fy as above
    person_options = sorted(filtered["Responsibility"].dropna().unique())
    if person_options:
        selected_person = st.selectbox("Select Responsible Person", person_options, key="pending_person_select")
        pending_df = filtered[(filtered["Responsibility"] == selected_person) & (filtered["Target date"] > pd.Timestamp(pd.Timestamp.now().date()))].copy()
        pending_df["Target date"] = pd.to_datetime(pending_df["Target date"], errors="coerce")
        pending_df = pending_df.dropna(subset=["Target date"])  # Remove rows with invalid dates
        pending_df["TargetDateStr"] = pending_df["Target date"].dt.strftime("%Y-%m-%d")
        # Group by due date and severity for this person
        stacked_counts = pending_df.groupby(["TargetDateStr", "Severity (High/Low)"]).size().reset_index(name="Count")
        stacked_counts = stacked_counts.sort_values(["TargetDateStr", "Severity (High/Low)"])
        import plotly.express as px
        severity_color_map = {"Low": "#7ec8e3", "High": "#003366"}  # Low: light blue, High: dark blue
        fig_stacked = px.bar(
            stacked_counts,
            x="TargetDateStr",
            y="Count",
            color="Severity (High/Low)",
            barmode="stack",
            title=f"Pending Responsibility Count for {selected_person} by Due Date ({selected_team}, {selected_fy}) (Stacked by Severity)",
            color_discrete_map=severity_color_map
        )
        fig_stacked.update_xaxes(title="Pending Due Date")
        st.plotly_chart(fig_stacked, use_container_width=True)
    else:
        st.info("No responsible persons found for the selected team and year.")
else:
    st.info("No pending responsibilities with valid target dates, severity, or person found for stacked chart.")

# --- Attendance Present Count by Member (Team & Year) ---
import datetime
ATTENDANCE_RECORDS_PATH = os.path.join("data", "processed", "Database", "attendance_records.csv")

st.markdown('<span style="font-size:15px;font-weight:600;">Attendance Present Count by Member</span>', unsafe_allow_html=True)
try:
    att_df = pd.read_csv(ATTENDANCE_RECORDS_PATH)
except Exception:
    att_df = pd.DataFrame(columns=["Date", "Team Name", "Names", "Status"])

if not att_df.empty and "Team Name" in att_df.columns and "Date" in att_df.columns and "Names" in att_df.columns and "Status" in att_df.columns:
    att_df["Date"] = pd.to_datetime(att_df["Date"], errors="coerce")
    att_df = att_df.dropna(subset=["Date"])  # Remove rows with invalid dates
    att_df["Year"] = att_df["Date"].apply(lambda x: x.year if x.month >= 4 else x.year - 1)
    att_df["FY"] = att_df["Year"].astype(str) + "-" + (att_df["Year"]+1).astype(str)

    team_options_att = sorted(att_df["Team Name"].dropna().unique())
    fy_options_att = sorted(att_df["FY"].unique(), reverse=True)

    filter_col1_att, filter_col2_att = st.columns([1,1])
    with filter_col1_att:
        st.markdown('<span style="font-size:13px;font-weight:500;">Team Name</span>', unsafe_allow_html=True)
        selected_team_att = st.selectbox(" ", team_options_att, key="team_select_att", label_visibility="collapsed")
    with filter_col2_att:
        st.markdown('<span style="font-size:13px;font-weight:500;">Financial Year (April-March)</span>', unsafe_allow_html=True)
        selected_fy_att = st.selectbox(" ", fy_options_att, key="fy_select_att", label_visibility="collapsed")

    filtered_att = att_df[(att_df["Team Name"] == selected_team_att) & (att_df["FY"] == selected_fy_att) & (att_df["Status"].str.lower() == "present")]

    # Explode the 'Names' column to get one row per present member
    filtered_att = filtered_att.copy()
    filtered_att["Names"] = filtered_att["Names"].str.split(",")
    exploded_att = filtered_att.explode("Names")
    exploded_att["Names"] = exploded_att["Names"].str.strip()
    present_counts = exploded_att["Names"].value_counts().reset_index()
    present_counts.columns = ["Member Name", "Present Count"]

    fig_present = px.bar(present_counts, x="Member Name", y="Present Count", title=f"Present Count by Member for {selected_team_att} ({selected_fy_att})")
    st.plotly_chart(fig_present, use_container_width=True)
else:
    st.info("Attendance records, Team Name, Date, or Names column not found for attendance present count graph.")

# --- Footer ---
st.markdown("---")
st.write("© 2025 Analytical Dashboard. Developed by Prince :(")

