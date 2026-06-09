# 📊 M&E Copilot
**AI-powered Monitoring & Evaluation Assistant for NGOs**

Built for the Global AI Hackathon Series with Qwen Cloud  
By Falluck Malenga — Blantyre, Malawi

---

## What It Does
Upload your project data (CSV or Excel) and M&E Copilot will:
- Calculate achievement rates for every indicator
- Flag indicators that are On Track / At Risk / Off Track
- Generate charts and a KPI dashboard automatically
- Write a professional donor report narrative using Qwen AI
- Let you download the full report in seconds

---

## Setup (Local)

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/me-copilot.git
cd me-copilot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

### 4. Open in browser
Go to: `http://localhost:8501`

---

## Get Your Qwen API Key
1. Go to [dashscope.aliyuncs.com](https://dashscope.aliyuncs.com)
2. Sign up / Log in
3. Navigate to API Keys
4. Create a new key and paste it in the app sidebar

---

## Deploy on Streamlit Cloud (Free)
1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set main file path: `app.py`
5. Click Deploy

---

## Data Format
Your CSV or Excel file should have at minimum:
| Indicator | Target | Actual |
|-----------|--------|--------|
| Beneficiaries reached | 5000 | 4320 |
| Health workers trained | 80 | 82 |

Column names can be anything — you map them inside the app.

A sample dataset (`sample_data.csv`) is included for testing.

---

## Tech Stack
- Python
- Streamlit
- Pandas
- Plotly
- Qwen Cloud API (via OpenAI-compatible SDK)
- OpenPyXL

---

## Hackathon
Global AI Hackathon Series with Qwen Cloud — Devpost 2026
