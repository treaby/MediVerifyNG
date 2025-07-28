import streamlit as st
import pandas as pd
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load drug database
@st.cache_data
def load_drug_data():
    return pd.read_csv("data/drugs.csv")

df = load_drug_data()

# Streamlit UI
st.title("💊 MediVerifyNG - AI Drug Verification App")
st.write("Instantly verify the authenticity of drugs using AI.")

# User inputs
drug_name = st.text_input("Drug Name:")
manufacturer = st.text_input("Manufacturer:")
nafdac_number = st.text_input("NAFDAC Number:")

if st.button("Verify Drug"):
    if not drug_name or not manufacturer or not nafdac_number:
        st.warning("Please fill in all fields.")
    else:
        # Search in local dataset
        match = df[
            (df['drug_name'].str.lower() == drug_name.lower()) &
            (df['manufacturer'].str.lower() == manufacturer.lower()) &
            (df['nafdac_number'] == nafdac_number)
        ]

        # Prepare prompt for OpenAI
        records = df.to_dict(orient='records')
        prompt = f"""
You are an AI drug verification assistant.

Check if this drug:
- Name: {drug_name}
- Manufacturer: {manufacturer}
- NAFDAC Number: {nafdac_number}

...matches any of these known verified drugs:

{records}

If found, respond ✅ Verified + reason.
If not found, respond ❌ Unverified + risk explanation + recommend contacting NAFDAC.
"""

        try:
           # Simulated AI logic (no OpenAI API required)
           if match.empty:
            result = "❌ Unverified — Drug not found in database. This may indicate a counterfeit or unregistered drug. Please contact NAFDAC for confirmation."
            st.error(result)
           else:
            result = "✅ Verified — This drug matches a verified entry. Always ensure packaging is sealed and from a registered pharmacy."
            st.success(result)

            st.markdown("🧠 *AI-powered logic simulated locally for demonstration purposes*")

        except Exception as e:
            st.error(f"Error: {e}")