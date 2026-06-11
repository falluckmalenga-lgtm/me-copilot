import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
from datetime import datetime

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="M&E Copilot Enterprise",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Session state ──────────────────────────────────────────────────────────────
for key, val in {
    "page": "dashboard", "df": None,
    "analysis_df": None, "narrative": "",
    "rca_text": "", "forecast_text": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── FULL ENTERPRISE CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
*{font-family:'Inter',system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased;box-sizing:border-box;}
#MainMenu,footer,header[data-testid="stHeader"]{display:none!important;}
.stApp{background:#F8FAFC!important;}
section[data-testid="stSidebar"]{display:none!important;}
.main .block-container{padding:80px 0 40px 0!important;max-width:100%!important;}

/* ── HEADER ───────────────────────────────────────────────────────────────── */
.ent-header{
  position:fixed;top:0;left:0;right:0;height:72px;
  background:rgba(255,255,255,0.95);backdrop-filter:blur(20px);
  border-bottom:1px solid rgba(15,23,42,0.07);
  box-shadow:0 1px 20px rgba(15,23,42,0.06);
  z-index:1000;display:flex;align-items:center;
  justify-content:space-between;padding:0 28px;
}
.hdr-left{display:flex;align-items:center;gap:14px;}
.hamburger{
  width:40px;height:40px;border:none;background:transparent;
  border-radius:8px;cursor:pointer;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:5px;transition:background .2s;
}
.hamburger:hover{background:#F1F5F9;}
.hamburger span{display:block;width:20px;height:2px;background:#0F172A;border-radius:2px;}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none;}
.logo-mark{
  width:38px;height:38px;
  background:linear-gradient(135deg,#0F172A 0%,#0F4CFF 100%);
  border-radius:9px;display:flex;align-items:center;justify-content:center;
  font-size:0.8rem;font-weight:900;color:white;letter-spacing:-0.05em;
}
.logo-text .brand{font-size:0.95rem;font-weight:800;color:#0F172A;letter-spacing:-0.02em;line-height:1.1;}
.logo-text .sub{font-size:0.58rem;font-weight:700;color:#0F4CFF;letter-spacing:.14em;text-transform:uppercase;}
.hdr-right{display:flex;align-items:center;gap:8px;}
.hdr-icon{
  width:38px;height:38px;border:1px solid #E2E8F0;background:white;
  border-radius:9px;cursor:pointer;display:flex;align-items:center;
  justify-content:center;font-size:1rem;transition:all .2s;position:relative;
}
.hdr-icon:hover{background:#F8FAFC;border-color:#CBD5E1;}
.notif-dot{
  position:absolute;top:-3px;right:-3px;width:18px;height:18px;
  background:#0F4CFF;border-radius:50%;font-size:.6rem;color:white;
  display:flex;align-items:center;justify-content:center;font-weight:800;
  border:2px solid white;
}
.hdr-btn{
  height:38px;padding:0 14px;border:1px solid #E2E8F0;background:white;
  border-radius:9px;cursor:pointer;font-size:.78rem;font-weight:700;
  color:#475569;display:flex;align-items:center;gap:6px;transition:all .2s;
}
.hdr-btn:hover{background:#F8FAFC;border-color:#0F4CFF;color:#0F4CFF;}
.user-pill{
  display:flex;align-items:center;gap:8px;padding:4px 12px 4px 4px;
  border:1px solid #E2E8F0;border-radius:999px;cursor:pointer;
  background:white;transition:all .2s;
}
.user-pill:hover{background:#F8FAFC;}
.avatar{
  width:30px;height:30px;background:linear-gradient(135deg,#0F4CFF,#2563EB);
  border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:.72rem;font-weight:800;color:white;
}
.user-name{font-size:.78rem;font-weight:700;color:#0F172A;}
.user-role{font-size:.62rem;color:#94A3B8;}

/* ── NAV OVERLAY ──────────────────────────────────────────────────────────── */
.nav-overlay{
  position:fixed;inset:0;background:rgba(0,0,0,.45);
  z-index:1001;opacity:0;pointer-events:none;transition:opacity .3s;
}
.nav-overlay.open{opacity:1;pointer-events:all;}

/* ── NAV DRAWER ───────────────────────────────────────────────────────────── */
.nav-drawer{
  position:fixed;top:0;left:-320px;bottom:0;width:320px;
  background:linear-gradient(160deg,#071B3B 0%,#0d2960 55%,#0a2456 100%);
  z-index:1002;transition:left .3s cubic-bezier(.4,0,.2,1);
  display:flex;flex-direction:column;
  box-shadow:6px 0 40px rgba(0,0,0,.3);
}
.nav-drawer.open{left:0;}
.drawer-hdr{
  padding:20px 20px 16px;
  border-bottom:1px solid rgba(255,255,255,.07);
  display:flex;align-items:center;justify-content:space-between;
}
.drawer-logo{display:flex;align-items:center;gap:12px;}
.drawer-mark{
  width:44px;height:44px;border-radius:11px;
  background:rgba(255,255,255,.1);
  display:flex;align-items:center;justify-content:center;
  font-size:.85rem;font-weight:900;color:white;border:1px solid rgba(255,255,255,.15);
}
.drawer-brand{font-size:1rem;font-weight:800;color:white;letter-spacing:-.02em;}
.drawer-sub{font-size:.6rem;font-weight:700;color:#60A5FA;letter-spacing:.14em;text-transform:uppercase;}
.close-btn{
  width:32px;height:32px;border:none;border-radius:7px;
  background:rgba(255,255,255,.08);color:white;font-size:1.1rem;
  cursor:pointer;display:flex;align-items:center;justify-content:center;
  transition:background .2s;
}
.close-btn:hover{background:rgba(255,255,255,.18);}
.drawer-nav{padding:12px;flex:1;overflow-y:auto;}
.nav-section-lbl{
  font-size:.62rem;font-weight:800;color:rgba(255,255,255,.3);
  letter-spacing:.14em;text-transform:uppercase;padding:10px 12px 6px;
}
.nav-item{
  display:flex;align-items:center;gap:12px;padding:11px 14px;
  border-radius:10px;cursor:pointer;transition:all .2s;margin-bottom:2px;
  border:1px solid transparent;
}
.nav-item:hover{background:rgba(255,255,255,.07);}
.nav-item.active{
  background:rgba(15,76,255,.3);
  border-color:rgba(15,76,255,.45);
}
.nav-icon{font-size:1.05rem;width:22px;text-align:center;}
.nav-label{font-size:.86rem;font-weight:600;color:rgba(255,255,255,.8);}
.nav-item.active .nav-label{color:white;}
.drawer-footer{
  padding:14px;border-top:1px solid rgba(255,255,255,.07);
}
.org-pill{
  display:flex;align-items:center;gap:10px;padding:10px 12px;
  border-radius:10px;background:rgba(255,255,255,.05);
  border:1px solid rgba(255,255,255,.08);cursor:pointer;transition:all .2s;
}
.org-pill:hover{background:rgba(255,255,255,.09);}
.org-icon{
  width:34px;height:34px;border-radius:8px;
  background:rgba(15,76,255,.4);display:flex;align-items:center;
  justify-content:center;font-size:.9rem;
}
.org-name{font-size:.8rem;font-weight:700;color:white;}
.org-sub{font-size:.67rem;color:rgba(255,255,255,.4);}

/* ── CONTENT WRAPPER ──────────────────────────────────────────────────────── */
.ent-wrap{padding:28px 28px;}

/* ── AI BADGE ─────────────────────────────────────────────────────────────── */
.ai-badge{
  display:inline-flex;align-items:center;gap:6px;
  background:linear-gradient(90deg,rgba(15,76,255,.08),rgba(37,99,235,.05));
  border:1px solid rgba(15,76,255,.18);border-radius:999px;
  padding:5px 14px;font-size:.68rem;font-weight:800;color:#0F4CFF;
  letter-spacing:.1em;text-transform:uppercase;margin-bottom:16px;
}

/* ── HERO ─────────────────────────────────────────────────────────────────── */
.hero{
  background:linear-gradient(130deg,#0F172A 0%,#0a2456 40%,#0F4CFF 100%);
  border-radius:20px;padding:44px 48px;margin-bottom:22px;
  position:relative;overflow:hidden;
  box-shadow:0 8px 40px rgba(15,76,255,.22);
}
.hero-orb1{
  position:absolute;top:-80px;right:120px;width:320px;height:320px;
  background:rgba(255,255,255,.03);border-radius:50%;
}
.hero-orb2{
  position:absolute;bottom:-100px;right:-50px;width:350px;height:350px;
  background:rgba(15,76,255,.12);border-radius:50%;
}
.hero-content{position:relative;z-index:1;max-width:600px;}
.hero-title{
  font-size:2.15rem;font-weight:900;color:white;letter-spacing:-.04em;
  line-height:1.1;margin:0 0 14px 0;
}
.hero-sub{font-size:.97rem;color:rgba(255,255,255,.6);line-height:1.65;margin:0 0 28px 0;}
.hero-feats{display:flex;gap:18px;flex-wrap:wrap;}
.hero-feat{
  display:flex;align-items:center;gap:8px;
  color:rgba(255,255,255,.75);font-size:.77rem;font-weight:600;
}
.hero-feat-ic{
  width:30px;height:30px;background:rgba(255,255,255,.1);
  border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:.85rem;
}

/* ── KPI GRID ─────────────────────────────────────────────────────────────── */
.kpi-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:22px;}
.kpi-card{
  background:white;border-radius:14px;padding:20px 20px 16px;
  box-shadow:0 1px 3px rgba(15,23,42,.05),0 4px 16px rgba(15,23,42,.06);
  transition:all .25s;position:relative;overflow:hidden;
}
.kpi-card:hover{transform:translateY(-2px);box-shadow:0 8px 28px rgba(15,23,42,.1);}
.kpi-ic{width:36px;height:36px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:1rem;margin-bottom:12px;}
.kpi-lbl{font-size:.67rem;font-weight:800;color:#94A3B8;text-transform:uppercase;letter-spacing:.09em;margin-bottom:4px;}
.kpi-val{font-size:1.9rem;font-weight:900;color:#0F172A;letter-spacing:-.04em;line-height:1.1;}
.kpi-trend{display:flex;align-items:center;gap:4px;margin-top:6px;font-size:.72rem;font-weight:700;}
.up{color:#22C55E;} .down{color:#EF4444;}
.kpi-sub{font-size:.68rem;color:#94A3B8;margin-top:2px;}

/* ── FEATURE CARDS ────────────────────────────────────────────────────────── */
.feat-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:22px;}
.feat-card{
  background:white;border-radius:14px;padding:20px;cursor:pointer;
  box-shadow:0 1px 3px rgba(15,23,42,.05),0 4px 12px rgba(15,23,42,.05);
  transition:all .3s;border:1px solid transparent;
}
.feat-card:hover{
  transform:translateY(-3px) scale(1.01);
  box-shadow:0 12px 32px rgba(15,23,42,.12);
  border-color:rgba(15,76,255,.18);
}
.feat-ic{width:42px;height:42px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.2rem;margin-bottom:12px;}
.feat-title{font-size:.8rem;font-weight:800;color:#0F172A;margin-bottom:5px;}
.feat-desc{font-size:.72rem;color:#64748B;line-height:1.5;margin-bottom:10px;}
.feat-arr{font-size:.85rem;color:#0F4CFF;font-weight:700;}

/* ── RIGHT PANEL ──────────────────────────────────────────────────────────── */
.r-panel-title{
  font-size:.83rem;font-weight:800;color:#0F172A;
  margin-bottom:14px;display:flex;justify-content:space-between;align-items:center;
}
.view-all{font-size:.7rem;color:#0F4CFF;font-weight:700;cursor:pointer;}
.upload-zone{
  border:2px dashed #CBD5E1;border-radius:12px;
  padding:26px 14px;text-align:center;transition:all .2s;
  cursor:pointer;margin-bottom:12px;
}
.upload-zone:hover{border-color:#0F4CFF;background:rgba(15,76,255,.02);}
.upload-ic{font-size:1.8rem;color:#0F4CFF;margin-bottom:6px;}
.upload-cta{font-size:.78rem;font-weight:800;color:#0F172A;margin-bottom:3px;}
.upload-sub{font-size:.68rem;color:#94A3B8;margin-bottom:10px;}
.fmt-chips{display:flex;gap:5px;justify-content:center;}
.fmt-chip{
  padding:3px 9px;border-radius:6px;background:#F1F5F9;
  font-size:.67rem;font-weight:800;color:#475569;border:1px solid #E2E8F0;
}
.dl-tpl{
  display:flex;align-items:center;justify-content:center;gap:6px;
  padding:9px;border-radius:9px;border:1px solid #E2E8F0;
  background:white;font-size:.76rem;font-weight:700;color:#475569;
  cursor:pointer;transition:all .2s;width:100%;margin-bottom:18px;
}
.dl-tpl:hover{border-color:#0F4CFF;color:#0F4CFF;background:#F8FBFF;}
.recent-item{
  display:flex;align-items:center;gap:9px;
  padding:8px 0;border-bottom:1px solid #F1F5F9;
}
.recent-item:last-child{border:none;}
.r-ic{font-size:1rem;}
.r-name{font-size:.76rem;font-weight:700;color:#0F172A;}
.r-time{font-size:.66rem;color:#94A3B8;}
.r-ok{margin-left:auto;color:#22C55E;font-size:.85rem;}
.report-item{
  display:flex;align-items:center;gap:9px;padding:9px 11px;
  border-radius:9px;background:#F8FAFC;border:1px solid #E2E8F0;
  cursor:pointer;transition:all .2s;margin-bottom:6px;
}
.report-item:hover{background:white;border-color:#0F4CFF;}
.rep-ic{font-size:1.2rem;}
.rep-title{font-size:.76rem;font-weight:800;color:#0F172A;}
.rep-desc{font-size:.66rem;color:#64748B;}
.export-chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px;}
.exp-chip{
  display:flex;align-items:center;gap:4px;padding:5px 10px;
  border-radius:8px;border:1px solid #E2E8F0;background:white;
  font-size:.7rem;font-weight:700;color:#475569;cursor:pointer;transition:all .2s;
}
.exp-chip:hover{border-color:#0F4CFF;color:#0F4CFF;}

/* ── SECTION TITLE ────────────────────────────────────────────────────────── */
.sec-title{
  font-size:.72rem;font-weight:900;color:#0F172A;letter-spacing:.08em;
  text-transform:uppercase;margin:0 0 14px 0;
  display:flex;align-items:center;gap:10px;
}
.sec-title::after{content:'';flex:1;height:1px;background:#E2E8F0;}

/* ── CHART CARD ───────────────────────────────────────────────────────────── */
.chart-card{
  background:white;border-radius:14px;padding:20px;
  box-shadow:0 1px 3px rgba(15,23,42,.05),0 4px 14px rgba(15,23,42,.06);
  margin-bottom:16px;
}
.chart-title{font-size:.83rem;font-weight:800;color:#0F172A;margin-bottom:2px;}
.chart-sub{font-size:.7rem;color:#94A3B8;margin-bottom:14px;}
.view-full{font-size:.7rem;color:#0F4CFF;font-weight:700;cursor:pointer;float:right;}

/* ── AI ANALYSIS GRID ─────────────────────────────────────────────────────── */
.ai-grid{display:grid;grid-template-columns:1fr 1fr;gap:2px;}
.ai-item{display:flex;align-items:flex-start;gap:9px;padding:10px;}
.ai-ic{width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:.85rem;flex-shrink:0;}
.ai-title{font-size:.76rem;font-weight:800;color:#0F172A;}
.ai-desc{font-size:.68rem;color:#64748B;margin-top:1px;}

/* ── RISK MATRIX ──────────────────────────────────────────────────────────── */
.risk-matrix{display:grid;grid-template-columns:repeat(3,1fr);gap:4px;margin-top:8px;}
.risk-cell{
  padding:12px;border-radius:8px;text-align:center;
  font-size:.7rem;font-weight:800;color:white;position:relative;
}
.risk-num{font-size:1.2rem;font-weight:900;display:block;}

/* ── BOTTOM CHARTS ────────────────────────────────────────────────────────── */
.bottom-grid{display:grid;grid-template-columns:1.2fr 1fr;gap:16px;margin-top:16px;}

/* ── WIDGETS ──────────────────────────────────────────────────────────────── */
.stButton>button{font-weight:700!important;font-size:.875rem!important;border-radius:10px!important;padding:11px 24px!important;transition:all .2s!important;border:none!important;}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#0F172A,#0F4CFF)!important;color:white!important;box-shadow:0 4px 16px rgba(15,76,255,.38)!important;}
.stButton>button[kind="primary"]:hover{transform:translateY(-2px)!important;box-shadow:0 8px 24px rgba(15,76,255,.5)!important;}
.stDownloadButton>button{background:linear-gradient(135deg,#0F172A,#0F4CFF)!important;color:white!important;border-radius:10px!important;font-weight:700!important;border:none!important;}
div[data-testid="metric-container"]{display:none!important;}
.stDataFrame{border-radius:12px!important;overflow:hidden!important;}
.stSelectbox>div>div,.stTextInput>div>input{border-radius:9px!important;border:1.5px solid #E2E8F0!important;}
.stAlert{border-radius:10px!important;}
.stFileUploader{border-radius:12px!important;}
.report-box{background:white;border-radius:14px;padding:32px 36px;box-shadow:0 1px 4px rgba(15,31,61,.05),0 8px 24px rgba(15,31,61,.08);border-top:4px solid #0F4CFF;line-height:1.9;font-size:.93rem;color:#1c2b48;}
</style>
""", unsafe_allow_html=True)

# ── HEADER + DRAWER HTML ───────────────────────────────────────────────────────
st.markdown("""
<!-- OVERLAY -->
<div class="nav-overlay" id="overlay" onclick="closeDrawer()"></div>

<!-- DRAWER -->
<div class="nav-drawer" id="drawer">
  <div class="drawer-hdr">
    <div class="drawer-logo">
      <div class="drawer-mark">ME</div>
      <div>
        <div class="drawer-brand">M&amp;E COPILOT</div>
        <div class="drawer-sub">Enterprise</div>
      </div>
    </div>
    <button class="close-btn" onclick="closeDrawer()">✕</button>
  </div>
  <div class="drawer-nav">
    <div class="nav-section-lbl">Main Menu</div>
    <div class="nav-item active" onclick="closeDrawer()"><span class="nav-icon">🏠</span><span class="nav-label">Dashboard</span></div>
    <div class="nav-item" onclick="closeDrawer()"><span class="nav-icon">📂</span><span class="nav-label">Upload Data</span></div>
    <div class="nav-item" onclick="closeDrawer()"><span class="nav-icon">📊</span><span class="nav-label">Indicators</span></div>
    <div class="nav-item" onclick="closeDrawer()"><span class="nav-icon">🤖</span><span class="nav-label">AI Analysis</span></div>
    <div class="nav-item" onclick="closeDrawer()"><span class="nav-icon">📋</span><span class="nav-label">Reports &amp; Exports</span></div>
    <div class="nav-section-lbl" style="margin-top:14px;">System</div>
    <div class="nav-item" onclick="closeDrawer()"><span class="nav-icon">⚙️</span><span class="nav-label">Settings</span></div>
  </div>
  <div class="drawer-footer">
    <div class="org-pill">
      <div class="org-icon">🌍</div>
      <div><div class="org-name">Global Health Initiative</div><div class="org-sub">Switch Organization</div></div>
      <span style="margin-left:auto;color:rgba(255,255,255,.4);font-size:.8rem;">▾</span>
    </div>
  </div>
</div>

<!-- STICKY HEADER -->
<div class="ent-header">
  <div class="hdr-left">
    <button class="hamburger" onclick="toggleDrawer()">
      <span></span><span></span><span></span>
    </button>
    <div class="logo">
      <div class="logo-mark">ME</div>
      <div class="logo-text">
        <div class="brand">M&amp;E COPILOT</div>
        <div class="sub">Enterprise</div>
      </div>
    </div>
  </div>
  <div class="hdr-right">
    <div class="hdr-icon">🔔<div class="notif-dot">8</div></div>
    <div class="hdr-icon">🌙</div>
    <button class="hdr-btn">⑂ Fork</button>
    <div class="user-pill">
      <div class="avatar">FM</div>
      <div>
        <div class="user-name">Falluck Malenga</div>
        <div class="user-role">Admin</div>
      </div>
      <span style="color:#94A3B8;font-size:.7rem;margin-left:4px;">▾</span>
    </div>
  </div>
</div>

<script>
function toggleDrawer(){
  document.getElementById('drawer').classList.toggle('open');
  document.getElementById('overlay').classList.toggle('open');
}
function closeDrawer(){
  document.getElementById('drawer').classList.remove('open');
  document.getElementById('overlay').classList.remove('open');
}
document.addEventListener('keydown',function(e){if(e.key==='Escape')closeDrawer();});
</script>
""", unsafe_allow_html=True)

# ── API KEY ────────────────────────────────────────────────────────────────────
api_key = st.secrets.get("QWEN_API_KEY", "")

# ── MAIN LAYOUT: content + right panel ────────────────────────────────────────
main_col, right_col = st.columns([2.85, 1], gap="medium")

with right_col:
    st.markdown('<div style="padding-top:8px;">', unsafe_allow_html=True)

    # ── Upload Panel ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="chart-card">
      <div class="r-panel-title">Upload Data <span class="view-all">View all</span></div>
      <div class="upload-zone">
        <div class="upload-ic">☁️</div>
        <div class="upload-cta">Drag &amp; drop files here</div>
        <div class="upload-sub">or</div>
        <div class="fmt-chips">
          <span class="fmt-chip">CSV</span>
          <span class="fmt-chip">XLSX</span>
          <span class="fmt-chip">XLS</span>
        </div>
      </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("", type=["csv","xlsx","xls"], label_visibility="collapsed")

    st.markdown("""
      <div class="dl-tpl">⬇ Download Template</div>
    </div>
    """, unsafe_allow_html=True)

    # Recent Uploads
    st.markdown("""
    <div class="chart-card" style="margin-top:14px;">
      <div class="r-panel-title">Recent Uploads <span class="view-all">View all</span></div>
      <div class="recent-item"><span class="r-ic">📄</span><div><div class="r-name">Health Indicators Q2.csv</div><div class="r-time">2 mins ago</div></div><span class="r-ok">✅</span></div>
      <div class="recent-item"><span class="r-ic">📊</span><div><div class="r-name">Nutrition Survey Data.xlsx</div><div class="r-time">1 hour ago</div></div><span class="r-ok">✅</span></div>
      <div class="recent-item"><span class="r-ic">📄</span><div><div class="r-name">WASH Monitoring Data.xls</div><div class="r-time">3 hours ago</div></div><span class="r-ok">✅</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Reports & Exports
    st.markdown("""
    <div class="chart-card" style="margin-top:14px;">
      <div class="r-panel-title">Reports &amp; Exports <span class="view-all">View all</span></div>
      <div class="report-item"><span class="rep-ic">🇺🇸</span><div><div class="rep-title">USAID Reports</div><div class="rep-desc">Generate USAID compliant reports</div></div></div>
      <div class="report-item"><span class="rep-ic">🇪🇺</span><div><div class="rep-title">EU Reports</div><div class="rep-desc">Generate EU compliant reports</div></div></div>
      <div class="report-item"><span class="rep-ic">🌐</span><div><div class="rep-title">UN Reports</div><div class="rep-desc">Generate UN compliant reports</div></div></div>
      <div class="export-chips">
        <span class="exp-chip">📕 PDF</span>
        <span class="exp-chip">📗 Excel</span>
        <span class="exp-chip">📘 PowerPoint</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # AI Settings (collapsed)
    if not api_key:
        with st.expander("⚙️ AI Settings"):
            api_key = st.text_input("Qwen API Key", type="password", placeholder="sk-...")
            model_choice = st.selectbox("Model", ["qwen-plus","qwen-turbo","qwen-max"])
    else:
        model_choice = "qwen-plus"
        st.success("✅ AI Ready")

    st.markdown('</div>', unsafe_allow_html=True)

# ── MAIN CONTENT ───────────────────────────────────────────────────────────────
with main_col:

    # ── Hero ───────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero">
      <div class="hero-orb1"></div><div class="hero-orb2"></div>
      <div class="hero-content">
        <div class="ai-badge">✦ AI Powered</div>
        <h1 class="hero-title">Monitoring &amp; Evaluation<br>Intelligence Platform</h1>
        <p class="hero-sub">Transform project data into actionable insights, donor-ready reports, compliance reports, and AI-powered recommendations.</p>
        <div class="hero-feats">
          <div class="hero-feat"><div class="hero-feat-ic">📊</div>Impact Measurement</div>
          <div class="hero-feat"><div class="hero-feat-ic">📋</div>Donor Reporting</div>
          <div class="hero-feat"><div class="hero-feat-ic">🛡</div>Compliance Frameworks</div>
          <div class="hero-feat"><div class="hero-feat-ic">🤖</div>AI-Powered Intelligence</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Process uploaded file ──────────────────────────────────────────────────
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            st.session_state.df = df
        except Exception as e:
            st.error(f"Could not read file: {e}")

    df = st.session_state.df

    # ── KPI Section ────────────────────────────────────────────────────────────
    if df is not None:
        cols = df.columns.tolist()
        num_cols = df.select_dtypes(include='number').columns.tolist()
        total_ind = len(df)
        on_track = at_risk = off_track = not_started = 0
        avg_prog = 0.0
        analysis_df = None

        if len(num_cols) >= 2:
            try:
                target_c = num_cols[0]; actual_c = num_cols[1]
                tmp = df.copy()
                tmp["_ach"] = (pd.to_numeric(tmp[actual_c], errors="coerce") /
                               pd.to_numeric(tmp[target_c], errors="coerce") * 100).round(1)
                on_track  = len(tmp[tmp["_ach"] >= 80])
                at_risk   = len(tmp[(tmp["_ach"] >= 50) & (tmp["_ach"] < 80)])
                off_track = len(tmp[tmp["_ach"] < 50])
                not_started = tmp["_ach"].isna().sum()
                avg_prog  = tmp["_ach"].mean().round(1)
                analysis_df = tmp
                st.session_state.analysis_df = analysis_df
            except: pass
    else:
        total_ind=1248; avg_prog=68.4; on_track=842; at_risk=216; not_started=190

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-ic" style="background:#EFF6FF;">📊</div>
        <div class="kpi-lbl">Total Indicators</div>
        <div class="kpi-val">{total_ind:,}</div>
        <div class="kpi-trend up">↑ 12.4%</div>
        <div class="kpi-sub">vs last month</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-ic" style="background:#F0FDF4;">🎯</div>
        <div class="kpi-lbl">Overall Progress</div>
        <div class="kpi-val">{avg_prog}%</div>
        <div class="kpi-trend up">↑ 8.7%</div>
        <div class="kpi-sub">vs last month</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-ic" style="background:#F0FDF4;">✅</div>
        <div class="kpi-lbl">On Track</div>
        <div class="kpi-val">{on_track:,}</div>
        <div class="kpi-trend up">↑ 15.3%</div>
        <div class="kpi-sub">67.6% of total</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-ic" style="background:#FFFBEB;">⚠️</div>
        <div class="kpi-lbl">At Risk</div>
        <div class="kpi-val">{at_risk}</div>
        <div class="kpi-trend up">↑ 5.4%</div>
        <div class="kpi-sub">17.3% of total</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-ic" style="background:#FFF1F2;">🔴</div>
        <div class="kpi-lbl">Not Started</div>
        <div class="kpi-val">{not_started}</div>
        <div class="kpi-trend down">↓ 2.1%</div>
        <div class="kpi-sub">Last Updated 2 mins ago</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Feature Cards ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="feat-grid">
      <div class="feat-card">
        <div class="feat-ic" style="background:#EFF6FF;">☁️</div>
        <div class="feat-title">Data Upload</div>
        <div class="feat-desc">Upload and manage project datasets.</div>
        <div class="feat-arr">→</div>
      </div>
      <div class="feat-card">
        <div class="feat-ic" style="background:#F0FDF4;">📈</div>
        <div class="feat-title">Performance Dashboard</div>
        <div class="feat-desc">Monitor indicators and project performance.</div>
        <div class="feat-arr">→</div>
      </div>
      <div class="feat-card">
        <div class="feat-ic" style="background:#FDF4FF;">🔬</div>
        <div class="feat-title">Root Cause Analysis</div>
        <div class="feat-desc">AI-powered performance diagnostics.</div>
        <div class="feat-arr">→</div>
      </div>
      <div class="feat-card">
        <div class="feat-ic" style="background:#FFFBEB;">📋</div>
        <div class="feat-title">Donor Reporting</div>
        <div class="feat-desc">Generate donor-compliant reports.</div>
        <div class="feat-arr">→</div>
      </div>
      <div class="feat-card">
        <div class="feat-ic" style="background:#F0FDF4;">🛡</div>
        <div class="feat-title">Compliance Frameworks</div>
        <div class="feat-desc">Track reporting and compliance standards.</div>
        <div class="feat-arr">→</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Charts Row ─────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([1, 1.7, 1.3], gap="small")

    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Project Health Score</div><div class="chart-sub">Overall performance index</div>', unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=float(avg_prog) if avg_prog else 75,
            number={"suffix":"/100","font":{"size":28,"color":"#0F172A","family":"Inter"}},
            gauge={
                "axis":{"range":[0,100],"tickcolor":"#E2E8F0"},
                "bar":{"color":"#0F4CFF","thickness":0.28},
                "steps":[
                    {"range":[0,50],"color":"#FEE2E2"},
                    {"range":[50,80],"color":"#FEF9C3"},
                    {"range":[80,100],"color":"#DCFCE7"}
                ],
                "borderwidth":0,"bgcolor":"white"
            }
        ))
        fig_gauge.update_layout(
            height=200, margin=dict(t=20,b=10,l=20,r=20),
            paper_bgcolor="white", font_family="Inter"
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar":False})
        status = "Good" if float(avg_prog or 75) >= 70 else "Needs Attention"
        color = "#22C55E" if status=="Good" else "#F59E0B"
        st.markdown(f'<div style="text-align:center;font-size:.8rem;font-weight:700;color:{color};">● {status}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="chart-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">
          <div><div class="chart-title">AI Analysis Overview</div><div class="chart-sub">Qwen AI diagnostics summary</div></div>
          <span class="view-all">View full analysis →</span>
        </div>
        <div class="ai-grid">
          <div class="ai-item"><div class="ai-ic" style="background:#FDF4FF;">🔬</div><div><div class="ai-title">Root Cause Analysis</div><div class="ai-desc">3 key issues identified</div></div></div>
          <div class="ai-item"><div class="ai-ic" style="background:#F0FDF4;">💡</div><div><div class="ai-title">Recommendations</div><div class="ai-desc">12 action items generated</div></div></div>
          <div class="ai-item"><div class="ai-ic" style="background:#FFFBEB;">⚠️</div><div><div class="ai-title">Risk Detection</div><div class="ai-desc">5 risks detected</div></div></div>
          <div class="ai-item"><div class="ai-ic" style="background:#EFF6FF;">💰</div><div><div class="ai-title">Budget Utilization</div><div class="ai-desc">68% of budget utilized</div></div></div>
          <div class="ai-item"><div class="ai-ic" style="background:#F0FDF4;">📈</div><div><div class="ai-title">Performance Forecast</div><div class="ai-desc">On track to meet targets</div></div></div>
          <div class="ai-item"><div class="ai-ic" style="background:#EFF6FF;">✔️</div><div><div class="ai-title">Data Quality Score</div><div class="ai-desc">92% data quality</div></div></div>
        </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        if st.session_state.analysis_df is not None and "_ach" in st.session_state.analysis_df.columns:
            adf = st.session_state.analysis_df.copy()
            months = ["Dec","Jan","Feb","Mar","Apr","May"]
            progress_vals = [25,35,42,55,62,float(avg_prog)]
        else:
            months = ["Dec","Jan","Feb","Mar","Apr","May"]
            progress_vals = [25,35,42,55,62,68.4]

        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=months, y=progress_vals, mode="lines+markers",
            line=dict(color="#0F4CFF", width=2.5),
            marker=dict(size=7, color="#0F4CFF",
                        line=dict(width=2, color="white")),
            fill="tozeroy",
            fillcolor="rgba(15,76,255,0.07)"
        ))
        fig_line.update_layout(
            height=210, margin=dict(t=10,b=10,l=10,r=10),
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9",
                       ticksuffix="%", tickfont=dict(size=10),
                       range=[0,100]),
            showlegend=False, font_family="Inter"
        )
        st.markdown('<div class="chart-card"><div style="display:flex;justify-content:space-between;align-items:flex-start;"><div><div class="chart-title">Progress Over Time</div><div class="chart-sub">Last 6 months</div></div></div>', unsafe_allow_html=True)
        st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Analyze Section (shown when data uploaded) ────────────────────────────
    if df is not None:
        st.markdown('<div class="sec-title">Indicator Analysis</div>', unsafe_allow_html=True)

        cols = df.columns.tolist()
        num_cols = df.select_dtypes(include='number').columns.tolist()

        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a: indicator_col = st.selectbox("Indicator Name", cols)
        with col_b: target_col = st.selectbox("Target", num_cols if num_cols else cols, index=0)
        with col_c: actual_col = st.selectbox("Actual", num_cols if num_cols else cols, index=min(1, len(num_cols)-1) if len(num_cols)>1 else 0)
        with col_d: project_name = st.text_input("Project Name", value="NGO Project")

        report_period = st.text_input("Reporting Period", value="Q2 2026")
        donor_format  = st.selectbox("Donor Format", ["Generic NGO","USAID","European Union (EU)","United Nations (UN)","Global Fund"])

        if st.button("🤖 Run AI Analysis", type="primary", use_container_width=True):
            try:
                adf = df[[indicator_col, target_col, actual_col]].copy()
                adf.columns = ["Indicator","Target","Actual"]
                adf["Target"] = pd.to_numeric(adf["Target"], errors="coerce")
                adf["Actual"] = pd.to_numeric(adf["Actual"], errors="coerce")
                adf.dropna(inplace=True)
                adf["Achievement (%)"] = (adf["Actual"]/adf["Target"]*100).round(1)
                adf["Status"] = adf["Achievement (%)"].apply(
                    lambda x: "🟢 On Track" if x>=80 else ("🟡 At Risk" if x>=50 else "🔴 Off Track"))
                st.session_state.analysis_df = adf
            except Exception as e:
                st.error(f"Error: {e}"); st.stop()

            # Bar chart
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig_bar = px.bar(
                adf, x="Indicator", y="Achievement (%)",
                color="Status",
                color_discrete_map={"🟢 On Track":"#22C55E","🟡 At Risk":"#F59E0B","🔴 Off Track":"#EF4444"},
                text="Achievement (%)", title=""
            )
            fig_bar.add_hline(y=80, line_dash="dash", line_color="#94A3B8",
                              annotation_text="80% target", annotation_position="top right")
            fig_bar.update_traces(texttemplate="%{text}%", textposition="outside")
            fig_bar.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                height=360, margin=dict(t=10,b=10,l=10,r=10),
                font_family="Inter", showlegend=True,
                xaxis=dict(tickfont=dict(size=10)),
                yaxis=dict(gridcolor="#F1F5F9")
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar":False})
            st.dataframe(adf, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # AI Features
            if not api_key:
                st.warning("⚠️ Enter your Qwen API key to generate AI narrative, root cause analysis, and forecast.")
            else:
                client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
                data_str = adf.to_string(index=False)
                off_track_df = adf[adf["Achievement (%)"] < 80]

                donor_map = {
                    "Generic NGO":"Standard NGO reporting language.",
                    "USAID":"USAID PMP-style narrative. Use 'beneficiaries','host country partners','performance indicators'.",
                    "European Union (EU)":"EU grant format. Use 'action','contracting authority','result indicators','target groups'.",
                    "United Nations (UN)":"UN RBM framework. Use outcome/output/activity language. Reference SDG alignment.",
                    "Global Fund":"PUDR format. Emphasise absorption, coverage, and system-level change."
                }

                tabs = st.tabs(["📝 Donor Report","🔬 Root Cause Analysis","📈 Forecast"])

                with tabs[0]:
                    with st.spinner("✍️ Writing donor report..."):
                        try:
                            r = client.chat.completions.create(
                                model=model_choice,
                                messages=[{"role":"user","content":f"""Senior M&E officer writing donor report.
Project:{project_name} Period:{report_period} Format:{donor_format}
Instructions:{donor_map[donor_format]}
Data:\n{data_str}
Write: 1)Executive Summary 2)Progress per Indicator 3)Achievements 4)Challenges 5)Recommendations
450-600 words, cite exact numbers, no placeholders."""}],
                                max_tokens=1400)
                            narrative = r.choices[0].message.content
                            st.session_state["narrative"] = narrative
                            st.markdown(f'<div class="report-box">{narrative.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"API Error: {e}")

                with tabs[1]:
                    if len(off_track_df) == 0:
                        st.success("All indicators are on track.")
                    else:
                        with st.spinner("🔍 Analysing root causes..."):
                            try:
                                r = client.chat.completions.create(
                                    model=model_choice,
                                    messages=[{"role":"user","content":f"""M&E specialist. Off-track indicators:
{off_track_df[['Indicator','Target','Actual','Achievement (%)']].to_string(index=False)}
For EACH: Root Cause(1-2 sentences), Corrective Action(1 sentence), Risk Level(Low/Medium/High)
Format: **[Name]** (X%)\n- Root Cause:...\n- Action:...\n- Risk:..."""}],
                                    max_tokens=900)
                                rca = r.choices[0].message.content
                                st.session_state["rca_text"] = rca
                                st.markdown(f'<div class="report-box">{rca.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"API Error: {e}")

                with tabs[2]:
                    quarters = st.slider("Quarters elapsed",1,4,2)
                    with st.spinner("📊 Generating forecast..."):
                        try:
                            r = client.chat.completions.create(
                                model=model_choice,
                                messages=[{"role":"user","content":f"""M&E analyst. Quarters elapsed:{quarters}/4
Data:\n{data_str}
For each indicator: projected year-end %, verdict(Will Meet/At Risk/Will Miss), 1-sentence explanation.
Output markdown table then 2-sentence summary."""}],
                                max_tokens=800)
                            forecast = r.choices[0].message.content
                            st.session_state["forecast_text"] = forecast
                            st.markdown(f'<div class="report-box">{forecast}</div>', unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"API Error: {e}")

                # Downloads
                st.markdown('<div class="sec-title" style="margin-top:24px;">Download Report Package</div>', unsafe_allow_html=True)
                d1, d2 = st.columns(2)
                with d1:
                    report_txt = f"""M&E COPILOT ENTERPRISE — FULL REPORT PACKAGE
{'='*60}
Project: {project_name} | Period: {report_period} | Format: {donor_format}
Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}
{'='*60}

DONOR REPORT
{st.session_state.get('narrative','')}

ROOT CAUSE ANALYSIS
{st.session_state.get('rca_text','')}

FORECAST
{st.session_state.get('forecast_text','')}

DATA TABLE
{adf.to_string(index=False)}

Generated by M&E Copilot Enterprise · Powered by Qwen AI
"""
                    st.download_button("📥 Download Full Report (.txt)", data=report_txt,
                        file_name=f"me_copilot_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain", use_container_width=True)
                with d2:
                    st.download_button("📥 Download Data (.csv)", data=adf.to_csv(index=False),
                        file_name=f"indicators_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv", use_container_width=True)

    else:
        # ── Bottom Charts (static demo) ────────────────────────────────────────
        st.markdown('<div class="sec-title">Performance Analytics</div>', unsafe_allow_html=True)
        b1, b2 = st.columns([1.2, 1], gap="small")

        with b1:
            categories = ["Health","Education","WASH","Nutrition","Livelihood","Protection"]
            values = [7.2, 5.8, 6.9, 4.3, 5.1, 3.8]
            fig_cat = px.bar(x=categories, y=values, color=values,
                color_continuous_scale=["#EFF6FF","#0F4CFF"],
                labels={"x":"","y":"Performance %"})
            fig_cat.update_layout(height=260, margin=dict(t=10,b=10,l=10,r=10),
                paper_bgcolor="white", plot_bgcolor="white",
                showlegend=False, coloraxis_showscale=False,
                font_family="Inter",
                yaxis=dict(gridcolor="#F1F5F9"),
                xaxis=dict(tickfont=dict(size=10)))
            st.markdown('<div class="chart-card"><div class="chart-title">Performance by Indicator Category</div><div class="chart-sub">All categories</div>', unsafe_allow_html=True)
            st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar":False})
            st.markdown('</div>', unsafe_allow_html=True)

        with b2:
            st.markdown("""
            <div class="chart-card">
              <div class="chart-title">Risk Matrix</div>
              <div class="chart-sub">Impact vs. Likelihood</div>
              <div class="risk-matrix" style="margin-top:10px;">
                <div class="risk-cell" style="background:#FCA5A5;"></div>
                <div class="risk-cell" style="background:#FCA5A5;"><span class="risk-num">2</span></div>
                <div class="risk-cell" style="background:#FCA5A5;"><span class="risk-num">1</span></div>
                <div class="risk-cell" style="background:#FDE68A;"><span class="risk-num">1</span></div>
                <div class="risk-cell" style="background:#FCA5A5;"></div>
                <div class="risk-cell" style="background:#FCA5A5;"><span class="risk-num">5</span></div>
                <div class="risk-cell" style="background:#BBF7D0;"></div>
                <div class="risk-cell" style="background:#FDE68A;"></div>
                <div class="risk-cell" style="background:#FDE68A;"></div>
              </div>
              <div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap;">
                <div style="display:flex;align-items:center;gap:4px;font-size:.68rem;color:#64748B;"><span style="width:10px;height:10px;background:#BBF7D0;border-radius:2px;display:inline-block;"></span>Low</div>
                <div style="display:flex;align-items:center;gap:4px;font-size:.68rem;color:#64748B;"><span style="width:10px;height:10px;background:#FDE68A;border-radius:2px;display:inline-block;"></span>Medium</div>
                <div style="display:flex;align-items:center;gap:4px;font-size:.68rem;color:#64748B;"><span style="width:10px;height:10px;background:#FCA5A5;border-radius:2px;display:inline-block;"></span>High</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

