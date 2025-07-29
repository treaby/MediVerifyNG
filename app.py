import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sqlite3
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# --- CONFIGURATION --- #
DATABASE_NAME = 'mediverify.db'
DRUGS_CSV_PATH = 'data/drugs.csv'

# --- DATABASE SETUP --- #
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

# --- DATA LOADING --- #
@st.cache_data
def load_drug_data(file_path):
    try:
        df = pd.read_csv(file_path)
        df['nafdac_number'] = df['nafdac_number'].astype(str).str.strip().str.upper()
        return df
    except FileNotFoundError:
        st.error(f"❌ '{file_path}' not found.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Failed loading drug data: {e}")
        st.stop()

# --- UI LAYOUT --- #
st.set_page_config(page_title="MediVerifyNG", page_icon="💊", layout="centered")

st.markdown("""
<div style='text-align:center;'>
    <h1 style='color:#0066CC;'>💊 MediVerifyNG</h1>
    <p style='font-size:18px;'>Verify a drug by NAFDAC number and report suspicious entries.</p>
</div>
""", unsafe_allow_html=True)

# --- INIT APP --- #
init_db()
df_drugs = load_drug_data(DRUGS_CSV_PATH)

# --- FORM INPUT --- #
with st.form("verify_form"):
    nafdac_input = st.text_input("🔎 Enter NAFDAC Number").strip().upper()
    submitted = st.form_submit_button("Verify Drug")

# --- LOGIC --- #
if submitted and nafdac_input:
    match = df_drugs[df_drugs["nafdac_number"] == nafdac_input]

    if not match.empty:
        drug = match.iloc[0]
        status = str(drug['status']).strip().upper()

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
            st.error(f"❌ Drug Not Verified – Status: {status}")
            st.warning("⚠️ This drug is *not verified* by NAFDAC.")
    else:
        st.error("❌ Drug Not Verified – NAFDAC Number Not Found.")
        st.warning("⚠️ This drug has been *unverified* by NAFDAC.")

        # --- FUZZY SUGGESTIONS --- #
        all_nafdac = df_drugs['nafdac_number'].tolist()
        suggestions = process.extract(nafdac_input, all_nafdac, scorer=fuzz.ratio, limit=5)
        matches = [s[0] for s in suggestions if s[1] > 80]

        if matches:
            st.info("💡 Did you mean:")
            for m in matches:
                st.write(f"🔹 {m}")

    # --- REPORT FORM --- #
    with st.expander("📢 Report This Drug"):
        reason = st.text_area("📝 Why do you think this is fake?")
        contact = st.text_input("📞 (Optional) Contact Info")

        if st.button("Submit Report"):
            try:
                with sqlite3.connect(DATABASE_NAME) as conn:
                    conn.execute("""
                        INSERT INTO reports (nafdac_number, reason, contact, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (nafdac_input, reason, contact, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                st.success("✅ Report submitted. Thank you for helping protect public health.")
            except Exception as e:
                st.error(f"❗ Could not save report: {e}")
                st.info("Please check database permissions or try again later.")