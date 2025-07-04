import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# Directory to save entrant card details (you can change it if necessary)
ENTRANT_CARD_DIRECTORY = r'D:\Python Projects\Confined Space Logbook\data\entrant_card_details'

# Make sure the directory exists
if not os.path.exists(ENTRANT_CARD_DIRECTORY):
    os.makedirs(ENTRANT_CARD_DIRECTORY)

# Placeholder to store the entrant card details (you can replace this with a database in a production system)
entrant_card_data = []

# Function to add entrant card details to the data list and save it to an Excel file
def add_entrant_card_details(name, role, due_date, card_issue_date, agency):
    global entrant_card_data
    entry = {
        "Name": name,
        "Role": role,
        "Due Date": due_date,
        "Card Issue Date": card_issue_date,
        "Agency": agency
    }
    entrant_card_data.append(entry)

    # Save the data to Excel after each submission
    save_entrant_card_data_to_excel()

# Function to save the entrant card details to an Excel file in the entrant card directory
def save_entrant_card_data_to_excel():
    if len(entrant_card_data) > 0:
        df = pd.DataFrame(entrant_card_data)
        file_path = os.path.join(ENTRANT_CARD_DIRECTORY, "entrant_card_details.xlsx")
        try:
            df.to_excel(file_path, index=False, engine="openpyxl")
            st.success(f"Entrant card data saved to {file_path}")
        except Exception as e:
            st.error(f"Error saving entrant card data: {e}")

# Function to handle the upload of an Excel file
def upload_entrant_card_data():
    uploaded_file = st.file_uploader("Upload Entrant Card Data (Excel or CSV)", type=["xlsx", "csv"])
    if uploaded_file is not None:
        try:
            # Read the uploaded file into a DataFrame
            if uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            
            st.success("File uploaded successfully!")
            # Display the uploaded data
            st.subheader("Uploaded Entrant Card Data:")
            st.dataframe(df)
            
            # Check if necessary columns exist
            required_columns = ["Name", "Role", "Due Date", "Card Issue Date", "Agency"]
            if all(col in df.columns for col in required_columns):
                # Store the uploaded data to the global data variable
                global entrant_card_data
                entrant_card_data = df.to_dict(orient='records')  # Convert to list of dictionaries
                save_entrant_card_data_to_excel()  # Save uploaded data to Excel
                st.success("Uploaded data has been successfully saved!")
            else:
                st.error(f"The uploaded file is missing the required columns: {', '.join(required_columns)}")
        except Exception as e:
            st.error(f"Error reading the file: {e}")

# Function to download the format template
def download_template():
    # Define the template columns
    template_columns = ["Name", "Role", "Due Date", "Card Issue Date", "Agency"]
    
    # Create an empty DataFrame with the correct column names
    df_template = pd.DataFrame(columns=template_columns)

    # Save the template DataFrame to a BytesIO object (in-memory)
    buffer = BytesIO()
    df_template.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)  # Move the pointer to the beginning of the BytesIO buffer

    # Create a download link for the Excel file
    st.download_button(
        label="Download Template (Excel)",
        data=buffer,
        file_name="entrant_card_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Function to display the entrant card details page
def show_entrant_card():
    st.title("Entrant Card Details")

    # File upload functionality
    upload_entrant_card_data()

    # Button to download the template
    download_template()

    # Form for collecting entrant card details
    with st.form(key='entrant_card_form'):
        st.header("Entrant Card Entry Form")

        # Input fields for the entrant card details
        name = st.text_input("Name")
        role = st.selectbox("Role", ["Entrant", "Attendant"])
        due_date = st.date_input("Due Date", datetime.today())
        card_issue_date = st.date_input("Card Issue Date", datetime.today())
        agency = st.text_input("Agency")

        # Submit button to add the data
        submit_button = st.form_submit_button("Submit Entrant Card Details")

        if submit_button:
            if not name or not agency:
                st.error("Please fill in all required fields (Name and Agency).")
            else:
                # Call the function to add the data and save it to Excel
                add_entrant_card_details(name, role, due_date, card_issue_date, agency)
                st.success("Entrant card details submitted successfully!")

    # Display the submitted entrant card data
    if len(entrant_card_data) > 0:
        st.subheader("Submitted Entrant Card Data:")
        df = pd.DataFrame(entrant_card_data)
        st.dataframe(df)

        # Option to download the entrant card data as Excel
        st.download_button(
            label="Download Entrant Card Data (Excel)",
            data=df.to_excel(index=False, engine="openpyxl"),  # Save as Excel
            file_name="entrant_card_details.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
