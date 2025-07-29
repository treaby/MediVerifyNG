import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os
from fuzzywuzzy import fuzz, process

# --- Configuration --- #
DATABASE_NAME = 'mediverify.db'
DRUGS_CSV_PATH = 'data/drugs.csv'

# --- Initialize DB --- #
def init_db():
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nafdac_number TEXT NOT NULL,
                reason TEXT,
                contact TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()

# --- Cached Drug Data Loader --- #
@st.cache_data
def load_drug_data(path):
    df = pd.read_csv(path)
    df['nafdac_number'] = df['nafdac_number'].astype(str).str.strip().str.upper()
    return df

# --- UI Configuration --- #
st.set_page_config(page_title="MediVerifyNG", page_icon="💊", layout="centered")
st.markdown("""
    <div style='text-align: center;'>
        <h1 style='color: #0066CC;'>💊 MediVerifyNG</h1>
        <p style='font-size: 18px;'>AI-Enhanced Drug Verification using NAFDAC Numbers</p>
    </div>
""", unsafe_allow_html=True)

# --- Initialize --- #
init_db()
df_drugs = load_drug_data(DRUGS_CSV_PATH)

# --- Input Form --- #
with st.form("verify_form"):
    nafdac_input = st.text_input("🔎 Enter NAFDAC Number").strip().upper()
    submitted = st.form_submit_button("Verify Drug")

# --- Verification Logic --- #
if submitted and nafdac_input:
    match = df_drugs[df_drugs["nafdac_number"] == nafdac_input]

    if not match.empty:
        drug = match.iloc[0]
        status = drug['status'].upper()
        if status == 'VERIFIED':
            st.success("✅ Drug Verified Successfully")
            st.markdown(f"""
                <div style='background-color:#F0F8FF;padding:15px;border-radius:10px;'>
                    <h4>🧪 Drug Details</h4>
                    <ul>
                        <li><strong>Name:</strong> {drug['drug_name']}</li>
                        <li><strong>Manufacturer:</strong> {drug['manufacturer']}</li>
                        <li><strong>NAFDAC No:</strong> {drug['nafdac_number']}</li>
                        <li><strong>Status:</strong> {drug['status']}</li>
                    </ul>
                    <p>✅ This drug has been <strong>verified</strong> by NAFDAC.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Drug Not Verified.")
            st.warning("⚠️ This drug has been *unverified* using NAFDAC records.")

            with st.expander("📢 Report This Drug"):
                reason = st.text_area("📝 Why do you think this is fake?")
                contact = st.text_input("📞 (Optional) Contact Info")
                if st.button("Submit Report"):
                    with sqlite3.connect(DATABASE_NAME) as conn:
                        conn.execute("""
                            INSERT INTO reports (nafdac_number, reason, contact, timestamp)
                            VALUES (?, ?, ?, ?)
                        """, (nafdac_input, reason, contact, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()
                    st.success("✅ Report submitted successfully.")
    else:
        all_nafdac = df_drugs['nafdac_number'].tolist()
        fuzzy_matches = process.extract(nafdac_input, all_nafdac, scorer=fuzz.ratio, limit=5)
        suggestions = [m[0] for m in fuzzy_matches if m[1] > 80]

        st.error("❌ Drug Not Verified – NAFDAC Number Not Found.")
        if suggestions:
            st.warning("🔍 Did you mean one of these?")
            for s in suggestions:
                st.write(f"• {s}")
        with st.expander("📢 Report This Drug"):
            reason = st.text_area("📝 Why do you think this is fake?")
            contact = st.text_input("📞 (Optional) Contact Info")
            if st.button("Submit Report"):
                with sqlite3.connect(DATABASE_NAME) as conn:
                    conn.execute("""
                        INSERT INTO reports (nafdac_number, reason, contact, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (nafdac_input, reason, contact, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                st.success("✅ Report submitted successfully.")