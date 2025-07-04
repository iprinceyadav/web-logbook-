import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Directory to save training details (you can change it if necessary)
TRAINING_DIRECTORY = r'D:\Python Projects\Confined Space Logbook\data\training_details'

# Make sure the training directory exists
if not os.path.exists(TRAINING_DIRECTORY):
    os.makedirs(TRAINING_DIRECTORY)

# Placeholder to store the training data (you can replace this with a database in a production system)
training_data = []

# Function to add training details to the data list and save it to an Excel file
def add_training_details(name, training_date, due_date, department_area, certificate_image):
    global training_data
    entry = {
        "Name": name,
        "Training Date": training_date,
        "Due Date": due_date,
        "Department Area": department_area,
        "Certificate Image": certificate_image
    }
    training_data.append(entry)

    # Save the data to Excel after each submission
    save_training_data_to_excel()

# Function to save the training data to an Excel file in the training directory
def save_training_data_to_excel():
    if len(training_data) > 0:
        df = pd.DataFrame(training_data)
        file_path = os.path.join(TRAINING_DIRECTORY, "training_details.xlsx")
        try:
            df.to_excel(file_path, index=False)
            st.success(f"Training data saved to {file_path}")
        except Exception as e:
            st.error(f"Error saving training data: {e}")

# Function to display the training details page
def show_training_details():
    st.title("Training Details")

    # Form for collecting training details
    with st.form(key='training_form'):
        st.header("Training Entry Form")

        # Input fields for the training details
        name = st.text_input("Name")
        training_date = st.date_input("Training Date", datetime.today())
        due_date = st.date_input("Due Date", datetime.today())
        department_area = st.selectbox("Department Area", ["HR", "Engineering", "Operations", "Other"])

        # File uploader for the training certificate
        certificate_image = st.file_uploader("Upload Training Certificate", type=["jpg", "jpeg", "png", "pdf"])

        # Submit button to add the data
        submit_button = st.form_submit_button("Submit Training Details")

        if submit_button:
            if not name or not certificate_image:
                st.error("Please fill in all required fields (Name and Certificate).")
            else:
                # Call the function to add the data and save it to Excel
                add_training_details(name, training_date, due_date, department_area, certificate_image)
                st.success("Training details submitted successfully!")

    # Display the submitted training data
    if len(training_data) > 0:
        st.subheader("Submitted Training Data:")
        df = pd.DataFrame(training_data)
        st.dataframe(df)

    # Option to download the training data as Excel
    if len(training_data) > 0:
        st.download_button(
            label="Download Training Data",
            data=df.to_excel(index=False),
            file_name="training_details.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
