# pages/attendance.py
import streamlit as st
import pandas as pd
import os

def show_attendance():
    st.title("Attendance Page")

    # Form to collect attendance
    with st.form(key='attendance_form'):
        st.header("Attendance Entry")
        
        name = st.text_input("Name")
        attendance = st.selectbox("Attendance", ["Present", "Absent"])
        date = st.date_input("Date", pd.to_datetime("today"))

        submit_button = st.form_submit_button("Submit Attendance")
        if submit_button:
            st.success(f"Attendance submitted for {name}")
            # Save to DataFrame or file
            attendance_data = pd.DataFrame([[name, attendance, date]], columns=["Name", "Attendance", "Date"])
            file_path = "attendance_data.xlsx"
            if os.path.exists(file_path):
                existing_data = pd.read_excel(file_path)
                attendance_data = pd.concat([existing_data, attendance_data], ignore_index=True)
            attendance_data.to_excel(file_path, index=False)
    
    # Download option
    st.subheader("Download Attendance Format")
    st.download_button("Download Attendance Format", "attendance_format.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Upload option
    st.subheader("Upload Attendance Data")
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
    if uploaded_file:
        data = pd.read_excel(uploaded_file)
        st.write(data)

# Run the function in main
if __name__ == "__main__":
    show_attendance()
