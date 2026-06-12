import os, json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from dashscope import Generation
import dashscope

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="M&E Copilot Enterprise",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session state ──────────────────────────────────────────────────────────────
DEFAULTS = {
    "df": None, "ai_analysis": None,
    "current_page": "Dashboard",
    "activity_log": [
        {"icon": "🚀", "event": "Platform initialized", "time": "Just now"},
    ]
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── API key ────────────────────────────────────────────────────────────────────
_api_key = os.environ.get("QWEN_API_KEY", "") or st.secrets.get("QWEN_API_KEY", "")
if _api_key:
    dashscope.api_key = _api_key

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
*{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;-webkit-font-smoothing:antialiased;}
#MainMenu,footer{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent!important;}
.stApp{background:#F8FAFC!important;}
.main .block-container{padding-top:1.5rem!important;padding-bottom:2rem!important;max-width:100%!important;}

/* ── SIDEBAR ─────────────────────────────────────────────── */
section[data-testid="stSidebar"]{background:#0D1B2A!important;border-right:1px solid rgba(255,255,255,.06)!important;}
section[data-testid="stSidebar"] *{color:#CBD5E1!important;}
section[data-testid="stSidebar"] h1,h2,h3{color:white!important;}
section[data-testid="stSidebar"] .stRadio>div{display:flex;flex-direction:column;gap:2px;}
section[data-testid="stSidebar"] .stRadio>div>label{
  display:flex!important;align-items:center;gap:10px;padding:11px 16px!important;
  border-radius:10px!important;cursor:pointer!important;transition:all .2s!important;
  font-size:.875rem!important;font-weight:600!important;
  color:rgba(255,255,255,.72)!important;background:transparent!important;
  border:1px solid transparent!important;
}
section[data-testid="stSidebar"] .stRadio>div>label:hover{background:rgba(255,255,255,.06)!important;color:white!important;}
section[data-testid="stSidebar"] .stRadio>div>label[data-baseweb]{background:rgba(255,255,255,.06)!important;}
section[data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"]{display:none!important;}
section[data-testid="stSidebar"] .stRadio input[type=radio]{display:none!important;}
section[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.08)!important;}
section[data-testid="stSidebar"] .stTextInput input{
  background:rgba(255,255,255,.07)!important;border:1.5px solid rgba(255,255,255,.12)!important;
  border-radius:9px!important;color:white!important;font-size:.85rem!important;
}
section[data-testid="stSidebar"] label{
  font-size:.68rem!important;font-weight:700!important;text-transform:uppercase!important;
  letter-spacing:.1em!important;color:rgba(255,255,255,.38)!important;
}

/* ── KPI CARDS ───────────────────────────────────────────── */
div[data-testid="metric-container"]{display:none!important;}
.kpi-card{background:white;border-radius:12px;padding:18px 18px 14px;
  box-shadow:0 1px 3px rgba(0,0,0,.05),0 4px 12px rgba(0,0,0,.06);
  border-left:4px solid #E2E8F0;height:100%;}
.kpi-total{border-left-color:#0F4CFF!important;}
.kpi-progress{border-left-color:#8B5CF6!important;}
.kpi-ontrack{border-left-color:#22C55E!important;}
.kpi-atrisk{border-left-color:#F59E0B!important;}
.kpi-notstart{border-left-color:#EF4444!important;}
.kpi-ic{width:34px;height:34px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:.95rem;margin-bottom:10px;}
.kpi-lbl{font-size:.67rem;font-weight:800;color:#94A3B8;text-transform:uppercase;letter-spacing:.09em;margin-bottom:3px;}
.kpi-val{font-size:1.85rem;font-weight:900;color:#0F172A;letter-spacing:-.04em;line-height:1.1;}
.kpi-trend{display:flex;align-items:center;gap:3px;margin-top:5px;font-size:.72rem;font-weight:700;}
.up{color:#22C55E;}.down{color:#EF4444;}
.kpi-sub{font-size:.68rem;color:#94A3B8;margin-top:1px;}

/* ── HERO ────────────────────────────────────────────────── */
.hero{background:linear-gradient(135deg,#EEF2FF 0%,#F8FAFF 100%);
  border-radius:16px;padding:36px 40px;margin-bottom:18px;
  border:1px solid rgba(99,102,241,.1);position:relative;overflow:hidden;}
.ai-badge{display:inline-flex;align-items:center;gap:6px;
  background:rgba(15,76,255,.08);border:1px solid rgba(15,76,255,.18);
  border-radius:999px;padding:4px 12px;font-size:.67rem;font-weight:800;
  color:#0F4CFF;letter-spacing:.1em;text-transform:uppercase;margin-bottom:14px;}
.hero-title{font-size:1.95rem;font-weight:900;color:#0F172A;letter-spacing:-.04em;line-height:1.15;margin:0 0 12px;}
.hero-sub{font-size:.93rem;color:#475569;line-height:1.65;margin:0 0 22px;max-width:560px;}
.hero-chips{display:flex;gap:10px;flex-wrap:wrap;}
.hero-chip{display:flex;align-items:center;gap:7px;background:white;
  border:1px solid rgba(99,102,241,.15);border-radius:9px;
  padding:7px 13px;font-size:.76rem;font-weight:600;color:#3730A3;}

/* ── FEATURE CARDS ───────────────────────────────────────── */
.feat-card{background:white;border-radius:12px;padding:18px;cursor:pointer;
  box-shadow:0 1px 3px rgba(0,0,0,.05),0 4px 12px rgba(0,0,0,.05);
  transition:all .25s;border:1px solid transparent;}
.feat-card:hover{transform:translateY(-3px);box-shadow:0 12px 28px rgba(0,0,0,.1);border-color:rgba(15,76,255,.2);}
.feat-ic{width:38px;height:38px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:1.05rem;margin-bottom:10px;}
.feat-title{font-size:.78rem;font-weight:800;color:#0F172A;margin-bottom:4px;}
.feat-desc{font-size:.71rem;color:#64748B;line-height:1.5;margin-bottom:8px;}
.feat-arr{font-size:.8rem;color:#0F4CFF;font-weight:700;}

/* ── CHART CARD ──────────────────────────────────────────── */
.chart-card{background:white;border-radius:14px;padding:18px;
  box-shadow:0 1px 3px rgba(0,0,0,.05),0 4px 14px rgba(0,0,0,.06);}
.ct{font-size:.82rem;font-weight:800;color:#0F172A;margin-bottom:3px;}
.cs{font-size:.7rem;color:#94A3B8;margin-bottom:12px;}

/* ── AI GRID ─────────────────────────────────────────────── */
.ai-grid{display:grid;grid-template-columns:1fr 1fr;gap:1px;}
.ai-item{display:flex;align-items:flex-start;gap:9px;padding:9px;}
.ai-ic{width:30px;height:30px;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:.82rem;flex-shrink:0;}
.ai-t{font-size:.75rem;font-weight:800;color:#0F172A;}
.ai-d{font-size:.68rem;color:#64748B;margin-top:1px;}

/* ── RIGHT PANEL ─────────────────────────────────────────── */
.r-card{background:white;border-radius:14px;padding:16px;
  box-shadow:0 1px 3px rgba(0,0,0,.05),0 4px 12px rgba(0,0,0,.06);margin-bottom:12px;}
.rp-t{font-size:.8rem;font-weight:800;color:#0F172A;margin-bottom:11px;
  display:flex;justify-content:space-between;align-items:center;}
.va{font-size:.68rem;color:#0F4CFF;font-weight:700;}
.fmt-chips{display:flex;gap:5px;margin:8px 0;}
.fmt{padding:3px 9px;border-radius:6px;background:#F1F5F9;
  font-size:.67rem;font-weight:800;color:#475569;border:1px solid #E2E8F0;}
.rec-item{display:flex;align-items:center;gap:8px;
  padding:7px 0;border-bottom:1px solid #F8FAFC;}
.rec-item:last-child{border:none;}
.rn{font-size:.74rem;font-weight:700;color:#0F172A;}
.rt{font-size:.65rem;color:#94A3B8;}
.rep-row{display:flex;align-items:center;gap:8px;padding:8px 10px;
  border-radius:8px;background:#F8FAFC;border:1px solid #E2E8F0;
  margin-bottom:5px;cursor:pointer;transition:all .2s;}
.rep-row:hover{background:white;border-color:#0F4CFF;}
.rep-title{font-size:.74rem;font-weight:700;color:#0F172A;}
.rep-desc{font-size:.65rem;color:#64748B;}
.exp-row{display:flex;gap:5px;flex-wrap:wrap;margin-top:8px;}
.exp-btn{display:flex;align-items:center;gap:4px;padding:5px 9px;
  border-radius:7px;border:1px solid #E2E8F0;background:white;
  font-size:.68rem;font-weight:700;color:#475569;cursor:pointer;transition:all .2s;}
.exp-btn:hover{border-color:#0F4CFF;color:#0F4CFF;}

/* ── ACTIVITY ────────────────────────────────────────────── */
.act-item{display:flex;align-items:flex-start;gap:8px;
  padding:7px 0;border-bottom:1px solid #F1F5F9;font-size:.74rem;}
.act-item:last-child{border:none;}
.act-ev{font-weight:600;color:#0F172A;}
.act-t{font-size:.66rem;color:#94A3B8;margin-top:1px;}

/* ── BUTTONS ─────────────────────────────────────────────── */
.stButton>button{font-weight:700!important;border-radius:10px!important;transition:all .2s!important;}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#0F172A,#0F4CFF)!important;
  color:white!important;border:none!important;box-shadow:0 4px 14px rgba(15,76,255,.38)!important;}
.stButton>button[kind="primary"]:hover{transform:translateY(-2px)!important;box-shadow:0 8px 22px rgba(15,76,255,.5)!important;}
.stDownloadButton>button{background:linear-gradient(135deg,#0F172A,#0F4CFF)!important;
  color:white!important;border:none!important;font-weight:700!important;border-radius:10px!important;}
.stDataFrame{border-radius:12px!important;overflow:hidden!important;}
.stAlert{border-radius:10px!important;}
.stTabs [data-baseweb="tab-list"]{background:#F1F5F9;border-radius:10px;padding:4px;gap:4px;}
.stTabs [data-baseweb="tab"]{border-radius:7px;font-weight:600;font-size:.85rem;}
.stTabs [aria-selected="true"]{background:white!important;color:#0F172A!important;box-shadow:0 2px 8px rgba(0,0,0,.08)!important;}
</style>
""", unsafe_allow_html=True)

# ── HELPERS ────────────────────────────────────────────────────────────────────
def compute_kpis(df):
    total = len(df)
    if "current_value" in df and "target_value" in df:
        df = df.copy()
        df["_ach"] = pd.to_numeric(df["current_value"], errors="coerce") / \
                     pd.to_numeric(df["target_value"], errors="coerce") * 100
        progress = round(df["_ach"].mean(), 1)
    else:
        progress = 0.0
    on_track   = len(df[df.get("status","") == "On Track"]) if "status" in df else 0
    at_risk    = len(df[df.get("status","") == "At Risk"]) if "status" in df else 0
    not_start  = len(df[df.get("status","") == "Not Started"]) if "status" in df else 0
    return total, progress, on_track, at_risk, not_start

def health_label(score):
    if score >= 70: return "Good", "#22C55E"
    if score >= 40: return "Fair", "#F59E0B"
    return "Poor", "#EF4444"

def get_ai_analysis(df):
    if not _api_key:
        return None
    summary = df.describe().to_string()
    if "status" in df.columns:
        summary += "\n" + df["status"].value_counts().to_string()
    prompt = (
        "Analyze this M&E dataset summary and return ONLY a valid JSON object with "
        "exactly these keys: "
        "{\"root_cause_count\": int, \"risks_detected\": int, "
        "\"performance_forecast\": \"one sentence string\", "
        "\"recommendations_count\": int, \"budget_utilization_pct\": float, "
        "\"data_quality_score\": float} "
        f"Dataset summary: {summary}"
    )
    try:
        resp = Generation.call(
            model="qwen-max",
            messages=[{"role": "user", "content": prompt}],
            result_format="message"
        )
        raw = resp.output.choices[0].message.content
        raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(raw)
    except Exception:
        return {"root_cause_count": 3, "risks_detected": 5,
                "performance_forecast": "Project is on track to meet 68% of targets by year-end.",
                "recommendations_count": 12, "budget_utilization_pct": 68.0,
                "data_quality_score": 92.0}

def add_activity(icon, event):
    st.session_state.activity_log.insert(
        0, {"icon": icon, "event": event, "time": datetime.now().strftime("%H:%M")})
    if len(st.session_state.activity_log) > 8:
        st.session_state.activity_log = st.session_state.activity_log[:8]

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 8px 14px;border-bottom:1px solid rgba(255,255,255,.07);margin-bottom:14px;">
      <div style="display:flex;align-items:center;gap:10px;">
        <div style="width:36px;height:36px;background:linear-gradient(135deg,#0F172A,#0F4CFF);
                    border-radius:9px;display:flex;align-items:center;justify-content:center;
                    font-size:.72rem;font-weight:900;color:white;flex-shrink:0;">ME</div>
        <div>
          <div style="font-size:.88rem;font-weight:800;color:white;letter-spacing:-.02em;">M&amp;E COPILOT</div>
          <div style="font-size:.56rem;font-weight:700;color:#0F4CFF;letter-spacing:.14em;text-transform:uppercase;">Enterprise</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    NAV = {
        "🏠  Dashboard": "Dashboard",
        "📂  Upload Data": "Upload Data",
        "📊  Indicators": "Indicators",
        "🤖  AI Analysis": "AI Analysis",
        "📋  Reports & Exports": "Reports & Exports",
        "⚙️  Settings": "Settings",
    }
    sel = st.radio("nav", list(NAV.keys()),
                   index=list(NAV.values()).index(st.session_state.current_page),
                   label_visibility="collapsed")
    st.session_state.current_page = NAV[sel]

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    if not _api_key:
        st.markdown("---")
        st.markdown("**⚙️ AI Settings**")
        manual_key = st.text_input("Qwen API Key", type="password", placeholder="sk-...")
        if manual_key:
            dashscope.api_key = manual_key

    st.markdown("""
    <div style="margin-top:20px;padding:10px 10px;background:rgba(255,255,255,.05);
                border-radius:10px;border:1px solid rgba(255,255,255,.08);cursor:pointer;">
      <div style="display:flex;align-items:center;gap:8px;">
        <div style="width:30px;height:30px;background:rgba(15,76,255,.4);
                    border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:.82rem;">🌍</div>
        <div>
          <div style="font-size:.74rem;font-weight:700;color:white;">Global Health Initiative</div>
          <div style="font-size:.6rem;color:rgba(255,255,255,.35);">Switch Organization</div>
        </div>
        <span style="margin-left:auto;color:rgba(255,255,255,.28);font-size:.7rem;">▾</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── LAYOUT: main + right panel ─────────────────────────────────────────────────
main_col, right_col = st.columns([2.9, 1], gap="medium")

# ══════════════════════════════════════════════════════════════════════════════
# RIGHT PANEL
# ══════════════════════════════════════════════════════════════════════════════
with right_col:
    # ── File uploader ──────────────────────────────────────────────────────────
    st.markdown('<div class="r-card">', unsafe_allow_html=True)
    st.markdown('<div class="rp-t">Upload Data <span class="va">View all</span></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="border:2px dashed #CBD5E1;border-radius:11px;padding:22px 12px;
                text-align:center;margin-bottom:10px;">
      <div style="font-size:1.6rem;color:#0F4CFF;margin-bottom:5px;">☁️</div>
      <div style="font-size:.77rem;font-weight:800;color:#0F172A;margin-bottom:2px;">Drag &amp; drop files here</div>
      <div style="font-size:.68rem;color:#94A3B8;margin-bottom:8px;">or</div>
    </div>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Browse Files", type=["csv","xlsx","xls"],
                                     label_visibility="collapsed")
    st.markdown("""<div class="fmt-chips">
      <span class="fmt">CSV</span><span class="fmt">XLSX</span><span class="fmt">XLS</span>
    </div>""", unsafe_allow_html=True)

    # Download template
    sample_csv = ("indicator_name,category,current_value,target_value,baseline_value,"
                  "status,date,budget_allocated,budget_used\n"
                  "Beneficiaries reached,Health,4320,5000,0,On Track,2026-04,50000,34200\n"
                  "Health workers trained,Health,82,80,0,On Track,2026-04,12000,10800\n"
                  "Schools with WASH,Education,12,25,0,At Risk,2026-04,30000,14000\n"
                  "Farmers with inputs,Livelihood,298,300,0,On Track,2026-04,22000,19800\n"
                  "ANC visits,Health,871,950,0,At Risk,2026-04,8000,5600\n"
                  "Community sessions,Health,45,60,0,At Risk,2026-04,6000,3000\n"
                  "Households assisted,Nutrition,390,800,0,Not Started,2026-04,40000,9800\n"
                  "Children enrolled,Nutrition,1185,1200,0,On Track,2026-04,18000,16200\n")
    st.download_button("⬇ Download Template", data=sample_csv,
                       file_name="me_copilot_template.csv", mime="text/csv",
                       use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Recent Uploads ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="r-card">
      <div class="rp-t">Recent Uploads <span class="va">View all</span></div>
      <div class="rec-item"><span>📄</span><div><div class="rn">Health Indicators Q2.csv</div><div class="rt">2 mins ago</div></div><span style="margin-left:auto;color:#22C55E;">✓</span></div>
      <div class="rec-item"><span>📊</span><div><div class="rn">Nutrition Survey.xlsx</div><div class="rt">1 hour ago</div></div><span style="margin-left:auto;color:#22C55E;">✓</span></div>
      <div class="rec-item"><span>📄</span><div><div class="rn">WASH Monitoring.xls</div><div class="rt">3 hours ago</div></div><span style="margin-left:auto;color:#22C55E;">✓</span></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Reports & Exports ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="r-card">
      <div class="rp-t">Reports &amp; Exports <span class="va">View all</span></div>
      <div class="rep-row"><span class="rep-title" style="font-size:1.1rem;">🇺🇸</span>
        <div><div class="rep-title">USAID Reports</div><div class="rep-desc">USAID compliant reports</div></div></div>
      <div class="rep-row"><span class="rep-title" style="font-size:1.1rem;">🇪🇺</span>
        <div><div class="rep-title">EU Reports</div><div class="rep-desc">EU compliant reports</div></div></div>
      <div class="rep-row"><span class="rep-title" style="font-size:1.1rem;">🌐</span>
        <div><div class="rep-title">UN Reports</div><div class="rep-desc">UN compliant reports</div></div></div>
      <div class="exp-row">
        <span class="exp-btn">📕 PDF</span>
        <span class="exp-btn">📗 Excel</span>
        <span class="exp-btn">📘 PPT</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PROCESS UPLOAD
# ══════════════════════════════════════════════════════════════════════════════
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") \
             else pd.read_excel(uploaded_file)
        st.session_state.df = df
        add_activity("📂", f"Uploaded: {uploaded_file.name}")
        if st.session_state.ai_analysis is None:
            with st.spinner("Running AI analysis..."):
                st.session_state.ai_analysis = get_ai_analysis(df)
                add_activity("🤖", "AI analysis completed")
    except Exception as e:
        with main_col:
            st.error(f"Could not read file: {e}")

df     = st.session_state.df
ai     = st.session_state.ai_analysis
# Demo KPI fallback
if df is not None:
    total_ind, avg_prog, on_track, at_risk, not_start = compute_kpis(df)
else:
    total_ind, avg_prog, on_track, at_risk, not_start = 1248, 68.4, 842, 216, 190
health_score = min(float(avg_prog), 100.0)
hlabel, hcolor = health_label(health_score)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
with main_col:

    # ── HERO ────────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero">
      <div class="ai-badge">✦ AI Powered</div>
      <h1 class="hero-title">Monitoring &amp; Evaluation<br>Intelligence Platform</h1>
      <p class="hero-sub">Transform project data into actionable insights, donor-ready reports,
      compliance reports, and AI-powered recommendations.</p>
      <div class="hero-chips">
        <div class="hero-chip">📊 Impact Measurement</div>
        <div class="hero-chip">📋 Donor Reporting</div>
        <div class="hero-chip">🛡 Compliance Frameworks</div>
        <div class="hero-chip">🤖 AI-Powered Intelligence</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI ROW ──────────────────────────────────────────────────────────────────
    k1,k2,k3,k4,k5 = st.columns(5, gap="small")
    kpi_data = [
        (k1,"kpi-total","📊","Total Indicators",f"{total_ind:,}","↑ 12.4%","up","vs last month"),
        (k2,"kpi-progress","🎯","Overall Progress",f"{avg_prog}%","↑ 8.7%","up","vs last month"),
        (k3,"kpi-ontrack","✅","On Track",f"{on_track:,}","↑ 15.3%","up","67.6% of total"),
        (k4,"kpi-atrisk","⚠️","At Risk",f"{at_risk}","↑ 5.4%","up","17.3% of total"),
        (k5,"kpi-notstart","🔴","Not Started",f"{not_start}","↓ 2.1%","down","Last updated 2m ago"),
    ]
    for col,cls,ic,lbl,val,trend,direction,sub in kpi_data:
        with col:
            st.markdown(f"""
            <div class="kpi-card {cls}">
              <div class="kpi-ic" style="background:{'#EFF6FF' if 'total' in cls else '#F0FDF4' if 'ontrack' in cls else '#FFFBEB' if 'atrisk' in cls else '#FFF1F2' if 'notstart' in cls else '#F5F3FF'}">{ic}</div>
              <div class="kpi-lbl">{lbl}</div>
              <div class="kpi-val">{val}</div>
              <div class="kpi-trend {direction}">{('↑' if direction=='up' else '↓')} {trend.replace('↑ ','').replace('↓ ','')}</div>
              <div class="kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── FEATURE CARDS ────────────────────────────────────────────────────────────
    f1,f2,f3,f4,f5 = st.columns(5, gap="small")
    feats = [
        (f1,"#EFF6FF","☁️","Data Upload","Upload and manage project datasets."),
        (f2,"#F0FDF4","📈","Performance Dashboard","Monitor indicators and project performance."),
        (f3,"#FDF4FF","🔬","Root Cause Analysis","AI-powered performance diagnostics."),
        (f4,"#FFFBEB","📋","Donor Reporting","Generate donor-compliant reports."),
        (f5,"#F0FDF4","🛡","Compliance Frameworks","Track reporting and compliance standards."),
    ]
    for col,bg,ic,title,desc in feats:
        with col:
            st.markdown(f"""
            <div class="feat-card">
              <div class="feat-ic" style="background:{bg}">{ic}</div>
              <div class="feat-title">{title}</div>
              <div class="feat-desc">{desc}</div>
              <div class="feat-arr">→</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── LOWER 3-COLUMN SECTION ────────────────────────────────────────────────────
    lc1, lc2, lc3 = st.columns([1, 1.6, 1.3], gap="small")

    # COL 1: Project Health Score gauge
    with lc1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="ct">Project Health Score</div><div class="cs">Overall performance index</div>', unsafe_allow_html=True)
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number", value=health_score,
            number={"suffix":"/100","font":{"size":26,"color":"#0F172A"}},
            gauge={
                "axis":{"range":[0,100],"tickcolor":"#E2E8F0","tickwidth":1},
                "bar":{"color":"#0F4CFF","thickness":0.28},
                "bgcolor":"white","borderwidth":0,
                "steps":[{"range":[0,40],"color":"#FEE2E2"},
                         {"range":[40,70],"color":"#FEF9C3"},
                         {"range":[70,100],"color":"#DCFCE7"}],
            }
        ))
        fig_g.update_layout(height=190, margin=dict(t=20,b=5,l=15,r=15),
                            paper_bgcolor="white")
        st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar":False})
        st.markdown(f"""
        <div style="text-align:center;margin-top:-10px;">
          <span style="display:inline-flex;align-items:center;gap:5px;
            background:{'#F0FDF4' if hlabel=='Good' else '#FFFBEB' if hlabel=='Fair' else '#FFF1F2'};
            border-radius:999px;padding:4px 12px;font-size:.78rem;font-weight:700;color:{hcolor};">
            ● {hlabel}
          </span>
          <div style="font-size:.68rem;color:{hcolor};font-weight:600;margin-top:5px;">
            ↑ 8 pts vs last month
          </div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # COL 2: AI Analysis Overview
    with lc2:
        ai_fields = [
            ("🔬","#FDF4FF","Root Cause Analysis",
             f"{ai['root_cause_count'] if ai else 3} key issues identified"),
            ("💡","#F0FDF4","Recommendations",
             f"{ai['recommendations_count'] if ai else 12} action items generated"),
            ("⚠️","#FFFBEB","Risk Detection",
             f"{ai['risks_detected'] if ai else 5} risks detected"),
            ("💰","#EFF6FF","Budget Utilization",
             f"{ai['budget_utilization_pct'] if ai else 68.0:.0f}% of budget utilized"),
            ("📈","#F0FDF4","Performance Forecast",
             (ai["performance_forecast"][:40]+"…" if ai and len(ai.get("performance_forecast",""))>40
              else (ai["performance_forecast"] if ai else "On track to meet targets"))),
            ("✅","#EFF6FF","Data Quality Score",
             f"{ai['data_quality_score'] if ai else 92.0:.0f}% data quality"),
        ]
        items_html = "".join([
            f'<div class="ai-item"><div class="ai-ic" style="background:{bg}">{ic}</div>'
            f'<div><div class="ai-t">{title}</div><div class="ai-d">{desc}</div></div></div>'
            for ic,bg,title,desc in ai_fields
        ])
        header = '<span class="va" style="cursor:pointer;">View full analysis →</span>'
        st.markdown(f"""
        <div class="chart-card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
            <div><div class="ct">AI Analysis Overview</div><div class="cs">Qwen AI diagnostics summary</div></div>
            {header}
          </div>
          <div class="ai-grid">{items_html}</div>
        </div>""", unsafe_allow_html=True)

    # COL 3: Progress Over Time
    with lc3:
        time_range = st.selectbox("", ["Last 6 Months","Last 12 Months"],
                                  label_visibility="collapsed", key="time_range")
        months_6  = ["Dec","Jan","Feb","Mar","Apr","May"]
        months_12 = ["Jun","Jul","Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar","Apr","May"]
        if df is not None and "date" in df.columns and "current_value" in df.columns:
            try:
                tmp = df.copy()
                tmp["date"] = pd.to_datetime(tmp["date"])
                tmp["_ach"] = pd.to_numeric(tmp["current_value"],errors="coerce") / \
                              pd.to_numeric(tmp["target_value"],errors="coerce") * 100
                monthly = tmp.groupby(tmp["date"].dt.to_period("M"))["_ach"].mean().reset_index()
                x_vals = [str(p) for p in monthly["date"]]
                y_vals = monthly["_ach"].tolist()
            except:
                x_vals = months_6; y_vals = [25,35,42,55,62,float(avg_prog)]
        else:
            n = 6 if time_range == "Last 6 Months" else 12
            x_vals = (months_6 if n==6 else months_12)
            y_vals = ([25,35,42,55,62,68] if n==6
                      else [18,22,25,30,35,38,42,48,55,60,65,68])

        fig_l = go.Figure()
        fig_l.add_trace(go.Scatter(
            x=x_vals, y=y_vals, mode="lines+markers",
            line=dict(color="#0F4CFF", width=2.5),
            marker=dict(size=7, color="#0F4CFF", line=dict(width=2,color="white")),
            fill="tozeroy", fillcolor="rgba(15,76,255,0.07)"
        ))
        fig_l.update_layout(
            height=208, margin=dict(t=10,b=10,l=10,r=10),
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(showgrid=False, tickfont=dict(size=9)),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9",
                       ticksuffix="%", tickfont=dict(size=9), range=[0,100]),
            showlegend=False
        )
        st.markdown('<div class="chart-card"><div class="ct">Progress Over Time</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_l, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── BOTTOM ROW ────────────────────────────────────────────────────────────────
    b1, b2, b3 = st.columns([1.25, 1.1, 1], gap="small")

    # B1: Performance by Category
    with b1:
        if df is not None and "category" in df.columns and "current_value" in df.columns:
            df2 = df.copy()
            df2["current_value"] = pd.to_numeric(df2["current_value"], errors="coerce")
            df2["target_value"]  = pd.to_numeric(df2["target_value"], errors="coerce")
            df2["_ach"] = df2["current_value"] / df2["target_value"] * 100
            cat_df = df2.groupby("category")["_ach"].mean().reset_index()
            cats, vals = cat_df["category"].tolist(), cat_df["_ach"].round(1).tolist()
        else:
            cats = ["Health","Education","WASH","Nutrition","Livelihood","Protection"]
            vals = [72,58,45,68,81,39]

        filter_opts = ["All Categories"] + cats
        sel_cat = st.selectbox("", filter_opts, label_visibility="collapsed", key="cat_filter")
        if sel_cat != "All Categories":
            idx = cats.index(sel_cat) if sel_cat in cats else None
            if idx is not None: cats, vals = [cats[idx]], [vals[idx]]

        fig_bar = px.bar(x=cats, y=vals,
                         color=vals, color_continuous_scale=["#BFDBFE","#0F4CFF"],
                         labels={"x":"","y":"Achievement %"})
        fig_bar.update_layout(height=230, margin=dict(t=10,b=10,l=10,r=10),
                              paper_bgcolor="white", plot_bgcolor="white",
                              showlegend=False, coloraxis_showscale=False,
                              yaxis=dict(gridcolor="#F1F5F9",ticksuffix="%",tickfont=dict(size=9)),
                              xaxis=dict(tickfont=dict(size=9)))
        st.markdown('<div class="chart-card"><div class="ct">Performance by Indicator Category</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    # B2: Risk Matrix
    with b2:
        impact_levels = ["High","Medium","Low"]
        likelihood_levels = ["Low","Medium","High","Very High"]
        # Derive from data or use demo
        if df is not None and "status" in df.columns:
            on  = on_track; ar = at_risk; ns = not_start
            matrix = [[1, ar//3+1, ar//3, 1],
                      [1, 0,       1,     ar//2],
                      [0, 1,       0,     0]]
        else:
            matrix = [[1,2,1,0],[1,0,1,2],[0,1,0,0]]

        colors = [["#FCA5A5","#FCA5A5","#FCA5A5","#FCA5A5"],
                  ["#FDE68A","#FCA5A5","#FCA5A5","#FCA5A5"],
                  ["#BBF7D0","#BBF7D0","#FDE68A","#FDE68A"]]

        fig_rm = go.Figure()
        for ri, row in enumerate(matrix):
            for ci, val in enumerate(row):
                fig_rm.add_trace(go.Scatter(
                    x=[ci], y=[ri], mode="markers+text",
                    marker=dict(size=48, color=colors[ri][ci], symbol="square",
                                line=dict(width=1, color="white")),
                    text=[str(val) if val > 0 else ""],
                    textfont=dict(size=13, color="white"),
                    textposition="middle center", showlegend=False,
                    hoverinfo="skip"
                ))
        fig_rm.update_layout(
            height=230, margin=dict(t=10,b=40,l=60,r=10),
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(ticktext=likelihood_levels, tickvals=[0,1,2,3],
                       title="Likelihood", tickfont=dict(size=8)),
            yaxis=dict(ticktext=impact_levels, tickvals=[0,1,2],
                       title="Impact", tickfont=dict(size=8)),
        )
        st.markdown('<div class="chart-card"><div class="ct">Risk Matrix</div><div class="cs">Impact vs. Likelihood</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_rm, use_container_width=True, config={"displayModeBar":False})
        st.markdown("""<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:4px;">
          <span style="display:flex;align-items:center;gap:4px;font-size:.66rem;color:#64748B;">
            <span style="width:9px;height:9px;background:#BBF7D0;border-radius:2px;display:inline-block;"></span>Low</span>
          <span style="display:flex;align-items:center;gap:4px;font-size:.66rem;color:#64748B;">
            <span style="width:9px;height:9px;background:#FDE68A;border-radius:2px;display:inline-block;"></span>Medium</span>
          <span style="display:flex;align-items:center;gap:4px;font-size:.66rem;color:#64748B;">
            <span style="width:9px;height:9px;background:#FCA5A5;border-radius:2px;display:inline-block;"></span>High</span>
        </div></div>""", unsafe_allow_html=True)

    # B3: Recent Activity
    with b3:
        items_html = "".join([
            f'<div class="act-item"><span style="font-size:1rem;">{a["icon"]}</span>'
            f'<div><div class="act-ev">{a["event"]}</div>'
            f'<div class="act-t">{a["time"]}</div></div></div>'
            for a in st.session_state.activity_log
        ])
        st.markdown(f"""
        <div class="chart-card" style="min-height:260px;">
          <div class="ct">Recent Activity</div>
          <div class="cs">Latest platform events</div>
          {items_html}
        </div>""", unsafe_allow_html=True)

    # ── AI REPORT GENERATOR (shown when data uploaded + API key available) ──────
    if df is not None and _api_key:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown("""<div style="font-size:.72rem;font-weight:900;color:#0F172A;
          letter-spacing:.08em;text-transform:uppercase;margin:16px 0 12px;
          display:flex;align-items:center;gap:10px;">
          AI Report Generator
          <span style="flex:1;height:1px;background:#E2E8F0;display:block;"></span>
        </div>""", unsafe_allow_html=True)

        rc1, rc2, rc3 = st.columns(3)
        with rc1: proj = st.text_input("Project Name", value="NGO Project 2026")
        with rc2: period = st.text_input("Reporting Period", value="Q2 2026")
        with rc3:
            donor = st.selectbox("Donor Format",
                ["Generic NGO","USAID","European Union (EU)","United Nations (UN)","Global Fund"])

        donor_inst = {
            "Generic NGO":"Standard NGO reporting language.",
            "USAID":"USAID PMP-style. Use 'beneficiaries','performance indicators','host country partners'.",
            "European Union (EU)":"EU grant format. Use 'action','contracting authority','result indicators'.",
            "United Nations (UN)":"UN RBM framework. Outcome/output/activity language. Reference SDG alignment.",
            "Global Fund":"PUDR format. Emphasise absorption, coverage, system-level change."
        }

        if st.button("🤖 Generate Donor Report", type="primary", use_container_width=True):
            data_str = df.to_string(index=False)
            prompt = (f"Senior M&E officer. Project:{proj} Period:{period} Format:{donor}\n"
                      f"Instructions:{donor_inst[donor]}\nData:\n{data_str}\n"
                      "Write: 1)Executive Summary 2)Progress per Indicator "
                      "3)Key Achievements 4)Challenges 5)Recommendations. 450-600 words, cite numbers.")
            with st.spinner("✍️ Writing donor report with Qwen AI..."):
                try:
                    resp = Generation.call(
                        model="qwen-max",
                        messages=[{"role":"user","content":prompt}],
                        result_format="message"
                    )
                    narrative = resp.output.choices[0].message.content
                    add_activity("📋", f"Generated {donor} report for {proj}")
                    st.markdown(f"""
                    <div style="background:white;border-radius:14px;padding:32px 36px;
                      box-shadow:0 1px 4px rgba(15,31,61,.05),0 8px 24px rgba(15,31,61,.08);
                      border-top:5px solid #0F4CFF;line-height:1.9;font-size:.93rem;color:#1c2b48;">
                      {narrative.replace(chr(10),"<br>")}
                    </div>""", unsafe_allow_html=True)

                    report_pkg = (f"M&E COPILOT ENTERPRISE — REPORT PACKAGE\n{'='*55}\n"
                                  f"Project:{proj} | Period:{period} | Format:{donor}\n"
                                  f"Generated:{datetime.now().strftime('%d %B %Y %H:%M')}\n"
                                  f"{'='*55}\n\n{narrative}\n\n{'='*55}\n"
                                  f"DATA TABLE\n{df.to_string(index=False)}\n"
                                  f"Generated by M&E Copilot Enterprise · Powered by Qwen AI")
                    dl1, dl2 = st.columns(2)
                    with dl1:
                        st.download_button("📥 Download Report (.txt)", data=report_pkg,
                            file_name=f"report_{datetime.now().strftime('%Y%m%d')}.txt",
                            mime="text/plain", use_container_width=True)
                    with dl2:
                        st.download_button("📥 Download Data (.csv)",
                            data=df.to_csv(index=False),
                            file_name=f"data_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv", use_container_width=True)
                except Exception as e:
                    st.error(f"Qwen API error: {e}")
    elif df is not None and not _api_key:
        st.info("💡 Enter your Qwen API key in the sidebar to enable AI report generation.")
