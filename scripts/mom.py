# pages/mom.py
import streamlit as st
import pandas as pd
import os

def show_mom():
    st.title("MOM (Minutes of Meeting) Page")

    # Form to collect MOM
    with st.form(key='mom_form'):
        st.header("MOM Entry")
        
        point = st.text_input("Point of Discussion")
        responsibilities = st.text_input("Responsibilities")
        status = st.selectbox("Status", ["Completed", "Pending"])
        mom_date = st.date_input("MOM Date", pd.to_datetime("today"))
        severity = st.selectbox("Severity", ["Low", "Medium", "High"])
        target_date = st.date_input("Target Date", pd.to_datetime("today"))
        
        submit_button = st.form_submit_button("Submit MOM")
        if submit_button:
            st.success(f"MOM submitted for {point}")
            # Save to DataFrame or file
            mom_data = pd.DataFrame([[point, responsibilities, status, mom_date, severity, target_date]],
                                    columns=["Point of Discussion", "Responsibilities", "Status", "MOM Date", "Severity", "Target Date"])
            file_path = "mom_data.xlsx"
            if os.path.exists(file_path):
                existing_data = pd.read_excel(file_path)
                mom_data = pd.concat([existing_data, mom_data], ignore_index=True)
            mom_data.to_excel(file_path, index=False)
    
    # Download option
    st.subheader("Download MOM Format")
    st.download_button("Download MOM Format", "mom_format.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Upload option
    st.subheader("Upload MOM Data")
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
    if uploaded_file:
        data = pd.read_excel(uploaded_file)
        st.write(data)

# Run the function in main
if __name__ == "__main__":
    show_mom()
