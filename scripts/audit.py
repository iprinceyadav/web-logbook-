# pages/audit.py
import streamlit as st
import pandas as pd
import os

def show_audit():
    st.title("Audit Page")

    # Form to collect audit data
    with st.form(key='audit_form'):
        st.header("Audit Entry")
        
        point = st.text_input("Point of Discussion")
        audit_type = st.selectbox("Audit Type", ["L1", "L2", "L3", "Monthly"])
        responsibilities = st.text_input("Responsibilities")
        status = st.selectbox("Status", ["Completed", "Pending"])
        audit_date = st.date_input("Audit Date", pd.to_datetime("today"))
        severity = st.selectbox("Severity", ["Low", "Medium", "High"])
        target_date = st.date_input("Target Date", pd.to_datetime("today"))
        department = st.text_input("Department")
        area = st.text_input("Area")
        
        submit_button = st.form_submit_button("Submit Audit")
        if submit_button:
            st.success(f"Audit submitted for {point}")
            # Save to DataFrame or file
            audit_data = pd.DataFrame([[point, audit_type, responsibilities, status, audit_date, severity, target_date, department, area]],
                                      columns=["Point of Discussion", "Audit Type", "Responsibilities", "Status", "Audit Date", "Severity", "Target Date", "Department", "Area"])
            file_path = "audit_data.xlsx"
            if os.path.exists(file_path):
                existing_data = pd.read_excel(file_path)
                audit_data = pd.concat([existing_data, audit_data], ignore_index=True)
            audit_data.to_excel(file_path, index=False)
    
    # Download option
    st.subheader("Download Audit Format")
    st.download_button("Download Audit Format", "audit_format.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Upload option
    st.subheader("Upload Audit Data")
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
    if uploaded_file:
        data = pd.read_excel(uploaded_file)
        st.write(data)

# Run the function in main
if __name__ == "__main__":
    show_audit()
