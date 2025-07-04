import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Set the layout to wide to maximize table width
st.set_page_config(layout="wide")

st.title("Equipment Management")

tab1, tab2 = st.tabs(["Analytics", "Equipment Details"])

with tab2:
    st.header("Equipment Data Editor")
    # Define path to CSV
    csv_path = r"E:\internship work\Zips\KFA GRT TF Logbook\data\processed\Database\equipment_data.csv"

    # Load data
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["SN", "Equipment name", "Previous Test date", "Test date ", "Due date"])

    # Convert date columns to datetime for compatibility with DateColumn
    for col in ["Previous Test date", "Test date ", "Due date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Column configuration
    column_config = {
        "SN": st.column_config.Column(disabled=True),
        "Equipment name": st.column_config.Column(disabled=True),
        "Previous Test date": st.column_config.DateColumn("Previous Test date", format="YYYY-MM-DD", help="Enter the date in YYYY-MM-DD format (e.g., 2024-07-01)"),
        "Test date ": st.column_config.DateColumn("Test date", format="YYYY-MM-DD", help="Enter the date in YYYY-MM-DD format (e.g., 2024-07-01)"),
        "Due date": st.column_config.DateColumn("Due date", format="YYYY-MM-DD", help="Enter the date in YYYY-MM-DD format (e.g., 2024-07-01)")
    }

    st.info("For 'Previous Test date', 'Test date', and 'Due date', enter the date in DD-MM-YYYY format (e.g., 01-07-2025). and Save the Changes to update.")

    # Save button in top right
    save_col1, save_col2 = st.columns([8,1])
    with save_col2:
        save_clicked = st.button("Save Changes", key="save_changes_top")

    # Display editable table
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key="equipment_editor",
        column_config=column_config,
        height=700  # Adjust height for larger table display
    )

    # Save logic
    if save_clicked:
        # Convert date columns to string in YYYY-MM-DD before saving
        for col in ["Previous Test date", "Test date ", "Due date"]:
            if col in edited_df.columns:
                edited_df[col] = pd.to_datetime(edited_df[col], errors='coerce').dt.strftime('%Y-%m-%d')
                edited_df[col] = edited_df[col].replace('NaT', '')
        edited_df.to_csv(csv_path, index=False)
        st.success("Equipment data updated!")

with tab1:
    st.header("Equipment Analytics")
    csv_path = r"E:\internship work\Zips\KFA GRT TF Logbook\data\processed\Database\equipment_data.csv"
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["SN", "Equipment name", "Previous Test date", "Test date ", "Due date"])

    # Only keep rows with valid due dates
    df["Due date"] = pd.to_datetime(df["Due date"], errors='coerce')
    df = df.dropna(subset=["Due date"])

    if not df.empty:
        import plotly.express as px
        col1, col2 = st.columns(2)
        with col1:
            # --- Month-Year Bar Chart ---
            df["MonthYear"] = df["Due date"].dt.strftime("%b %Y")
            monthyear_counts = df["MonthYear"].value_counts().sort_index()
            monthyear_df = pd.DataFrame({"MonthYear": monthyear_counts.index, "Equipment Count": monthyear_counts.values})
            fig = px.bar(monthyear_df, x="MonthYear", y="Equipment Count", title="Month-Year wise Equipment Due Count", text=monthyear_df['Equipment Count'], color="Equipment Count", color_continuous_scale="YlGnBu")
            fig.update_traces(textfont_size=40, texttemplate='%{text:.0f}')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            # --- Urgent/Incoming/Expired Bar Chart ---
            today = pd.Timestamp(datetime.now().date())
            df["DaysToDue"] = (df["Due date"] - today).dt.days
            def due_category(days):
                if days < 0:
                    return "Expired"
                elif days <= 10:
                    return "Urgent"
                else:
                    return "Incoming"
            df["DueCategory"] = df["DaysToDue"].apply(due_category)
            cat_counts = df["DueCategory"].value_counts().reindex(["Urgent", "Incoming", "Expired"], fill_value=0)
            cat_df = pd.DataFrame({"Category": cat_counts.index, "Equipment Count": cat_counts.values})
            color_map = {"Incoming": "green", "Urgent": "orange", "Expired": "red"}
            fig2 = px.bar(cat_df, x="Category", y="Equipment Count", title="Equipment Due Status (Urgent / Incoming / Expired)", text=cat_df['Equipment Count'], color="Category", color_discrete_map=color_map)
            fig2.update_traces(textfont_size=40, texttemplate='%{text:.0f}')
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No equipment with valid due dates found for analytics.")
