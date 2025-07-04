import streamlit as st
import pandas as pd
import os
import base64
from datetime import date
from pathlib import Path
import urllib.parse

# Constants
CSV_FILE = "data/processed/Database/entrant_attendant_data.csv"
UPLOAD_DIR = "certificates"

st.set_page_config(page_title="Entrant Attendant Card Form", layout="wide")
st.title("Entrant Attendant Card Management")

# Ensure upload directory exists
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# Load existing data
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=[
        "SN", "Name", "Role", "Training date", "Due date", "Agency", "Certificate File Name", "Certificate Link"
    ])

# Tabs
tab1, tab2, tab_analytics = st.tabs(["➕ Add Entry", "📋 View Records", "📊 Analytics"])

# ========== Analytics Tab ==========
with tab_analytics:
    st.subheader("Month-wise Training Due Date Count")
    if not df.empty and "Due date" in df.columns:
        df["Due date"] = pd.to_datetime(df["Due date"], errors="coerce")
        df_valid = df.dropna(subset=["Due date"])
        if not df_valid.empty:
            df_valid["MonthYear"] = df_valid["Due date"].dt.strftime("%b %Y")
            monthyear_counts = df_valid["MonthYear"].value_counts().sort_index()
            monthyear_df = pd.DataFrame({"MonthYear": monthyear_counts.index, "Due Count": monthyear_counts.values})
            import plotly.express as px
            fig = px.bar(monthyear_df, x="MonthYear", y="Due Count", title="Month-wise Training Due Date Count", text=monthyear_df['Due Count'], color="Due Count", color_continuous_scale="Blues")
            fig.update_traces(textfont_size=20, texttemplate='%{text:.0f}')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No valid due dates found for analytics.")
    else:
        st.info("No data or 'Due date' column not found.")

# ========== Tab 1 ==========
with tab1:
    st.subheader("Add a New Entrant/Attendant Record")

    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name")
        with col2:
            role = st.selectbox("Role", ["Entrant", "Attendant"])

        col3, col4 = st.columns(2)
        with col3:
            training_date = st.date_input("Training Date", value=date.today())
        with col4:
            due_date = st.date_input("Due Date", value=date.today())

        agency = st.text_input("Agency")
        training_cert = st.file_uploader("Upload Training Certificate (PDF/Image)", type=["pdf", "png", "jpg", "jpeg"])

        submitted = st.form_submit_button("Submit Entry")

        if submitted:
            if name and training_cert:
                # Auto-generated SN
                new_sn = len(df) + 1

                # Clean and create custom filename
                extension = os.path.splitext(training_cert.name)[-1]
                safe_name = name.replace(" ", "_")
                safe_role = role.replace(" ", "_")
                safe_agency = agency.replace(" ", "_")
                safe_due = str(due_date).replace("-", "")  # Format as YYYYMMDD
                new_filename = f"{safe_name}_{safe_role}_{safe_due}_{safe_agency}{extension}"

                # Save file
                cert_path = os.path.join(UPLOAD_DIR, new_filename)
                with open(cert_path, "wb") as f:
                    f.write(training_cert.read())

                # Prepare data
                cert_link = f"{UPLOAD_DIR}/{urllib.parse.quote(new_filename)}"
                new_row = pd.DataFrame([{
                    "SN": new_sn,
                    "Name": name,
                    "Role": role,
                    "Training date": training_date,
                    "Due date": due_date,
                    "Agency": agency,
                    "Certificate File Name": new_filename,
                    "Certificate Link": cert_link
                }])

                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(CSV_FILE, index=False)
                st.success(f"Entry added with SN: {new_sn}")
            else:
                st.error("Please complete all required fields and upload a certificate.")

# ========== Tab 2 ==========
with tab2:
    st.subheader("📋 Previously Saved Records")

    if df.empty:
        st.info("No records found.")
    else:
        # Ensure 'Certificate Link' exists
        if "Certificate Link" not in df.columns:
            df["Certificate Link"] = df["Certificate File Name"].apply(
                lambda x: os.path.join(UPLOAD_DIR, x).replace("\\", "/") if pd.notna(x) else ""
            )

        st.markdown("### All Entries")

        # Display headers
        header_cols = st.columns([1, 2, 2, 2, 2, 2, 3])
        header_cols[0].markdown("**SN**")
        header_cols[1].markdown("**Name**")
        header_cols[2].markdown("**Role**")
        header_cols[3].markdown("**Training Date**")
        header_cols[4].markdown("**Due Date**")
        header_cols[5].markdown("**Agency**")
        header_cols[6].markdown("**Download Certificate**")

        # Show each row in a horizontal layout
        for i, row in df.iterrows():
            cols = st.columns([1, 2, 2, 2, 2, 2, 3])
            cols[0].write(row["SN"])
            cols[1].write(row["Name"])
            cols[2].write(row["Role"])
            cols[3].write(row["Training date"])
            cols[4].write(row["Due date"])
            cols[5].write(row["Agency"])

            cert_path = row["Certificate Link"]
            # Only check if cert_path is a valid string and not NaN/float
            if isinstance(cert_path, str) and cert_path and os.path.exists(cert_path):
                with open(cert_path, "rb") as file:
                    file_data = file.read()
                    file_name = os.path.basename(cert_path)
                    cols[6].download_button(
                        label="📄 Click here to download",
                        data=file_data,
                        file_name=file_name,
                        mime="application/octet-stream",
                        key=f"download_{i}"
                    )
            else:
                cols[6].warning("File not found")

        # Allow downloading the full CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download All Entries CSV", csv, "entrant_attendant_data.csv", "text/csv")