# 💊 MediVerifyNG – AI‑Powered Drug Verification (Streamlit App)

MediVerifyNG empowers users—especially in underserved or rural areas—to verify drug authenticity using NAFDAC numbers and report suspicious drugs. It works offline, is user‑friendly, and requires no technical skill.

---

## 📝 Features

- ✅ Verify drug details by entering its NAFDAC number
- ❌ Handle unverified or incorrectly typed inputs using fuzzy matching
- 📢 Allow users to report suspected fake drugs with optional comments/contact
- 🗄️ Store reports in a local SQLite database
- 🌍 Designed to work offline, with minimal reliance on internet access

---

## 🧠 Built With

| Component        | Language/Library                          |
|------------------|-------------------------------------------|
| Frontend         | Python / Streamlit                        |
| Data Handling    | pandas                                    |
| Text Processing  | fuzzywuzzy / Python‑Levenshtein           |
| Environment      | python‑dotenv                             |
| Storage          | SQLite (sqlite3)                        |
| Python Version   | 3.13 (fully compatible)               |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13 installed  
- Git and pip ready

### Installation & Setup

`bash
git clone https://github.com/treaby/MediVerifyNG.git
cd MediVerifyNG
python -m venv venv
.\venv\Scripts\activate       # (Windows)
source venv/bin/activate     # (Linux/Mac)
pip install -r requirements.txt