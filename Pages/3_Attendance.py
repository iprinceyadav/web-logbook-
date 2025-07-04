import streamlit as st
import pandas as pd
from datetime import date
import os
import pathlib

st.title("Attendance Marking System")

# Use the provided CSV file
file_path = "E:\internship work\Zips\KFA GRT TF Logbook\data\processed\Database\\attendance_data.csv"

# Get the directory of mom.py
mom_file = os.path.join("data", "mom_records.csv")  # Path for future MoM records
att_file = "E:\\internship work\\Zips\\KFA GRT TF Logbook\\data\\processed\\Database\\attendance_records.csv"  # Attendance records remain as before

if not os.path.exists(file_path):
    st.error(f"File {file_path} not found. Please make sure it exists in the app directory.")
    st.stop()

# Read the data
try:
    df = pd.read_csv(file_path)
except Exception as e:
    st.error(f"Error reading CSV file: {e}")
    st.stop()

# Rename Department column to Team Name for consistency
if "Department" in df.columns:
    df = df.rename(columns={"Department": "Team Name"})

# Check required columns
if not {"Team Name", "Name"}.issubset(df.columns):
    st.error("CSV file must have 'Team Name' and 'Name' columns.")
    st.stop()

# Tabs for Attendance, Add Member, and MoM
attendance_tab, add_member_tab ,view_record_tab= st.tabs(["Mark Attendance", "Add Member","View Record" ])

with attendance_tab:
    teams = df["Team Name"].unique()
    selected_team = st.selectbox("Select Team Name", teams)
    names = df[df["Team Name"] == selected_team]["Name"].tolist()
    st.write(f"Mark attendance for {selected_team}:")
    attendance = {}
    for name in names:
        present = st.checkbox(name, key=name, value=True)  # Checked by default
        attendance[name] = present
    if st.button("Submit Attendance"):
        today = date.today().isoformat()
        present_names = [name for name, is_present in attendance.items() if is_present]
        absent_names = [name for name, is_present in attendance.items() if not is_present]
        records = []
        if present_names:
            records.append({
                "Date": today,
                "Team Name": selected_team,
                "Names": ", ".join(present_names),
                "Status": "Present"
            })
        if absent_names:
            records.append({
                "Date": today,
                "Team Name": selected_team,
                "Names": ", ".join(absent_names),
                "Status": "Absent"
            })
        att_df = pd.DataFrame(records)
        columns = ["Date", "Team Name", "Names", "Status"]
        if os.path.exists(att_file):
            old_att = pd.read_csv(att_file)
            att_df = pd.concat([old_att, att_df], ignore_index=True)
            att_df = att_df[columns]
        else:
            att_df = att_df[columns]
        att_df.to_csv(att_file, index=False)
        st.success("Attendance saved!")
        st.write("Today's Attendance:")
        st.dataframe(att_df)

with add_member_tab:
    st.subheader("📝 View & Edit Attendance Master Table")

    # Ensure 'Password' column exists
    if "Password" not in df.columns:
        df["Password"] = ""

    st.markdown("You can edit the Team Name, Name, or Password directly in the table below:")

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",  # Allows adding/removing rows
        use_container_width=True,
        key="attendance_editor"
    )

    if st.button("💾 Save Changes to Attendance Master"):
        try:
            edited_df.to_csv(file_path, index=False)
            st.success("✅ Changes saved to attendance master file.")
        except Exception as e:
            st.error(f"❌ Failed to save changes: {e}")


with view_record_tab:
    st.subheader("📋 View Attendance Records")

    # Inject custom CSS to force wider column widths
    st.markdown("""
        <style>
        .dataframe th, .dataframe td {
            white-space: nowrap;
        }
        .stDataFrame div[data-testid="stHorizontalBlock"] {
            overflow-x: auto;
        }
        </style>
    """, unsafe_allow_html=True)

    if os.path.exists(att_file):
        att_df = pd.read_csv(att_file)
        if not att_df.empty:
            st.dataframe(att_df, use_container_width=True, height=600)
        else:
            st.info("No attendance records found.")
    else:
        st.info("Attendance records file does not exist. Please mark attendance first.")