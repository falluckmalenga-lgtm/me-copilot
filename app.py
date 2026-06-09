import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
import io
from datetime import datetime

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="M&E Copilot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS — Professional SaaS Design System ───────────────────────────────
st.markdown("""
<style>
/* ── Base & Typography ──────────────────────────────────────────────────────── */
* {
    font-family: system-ui, -apple-system, BlinkMacSystemFont,
                 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
}
.stApp { background: #f4f7fb; }
.main .block-container {
    padding: 2rem 3rem 4rem 3rem;
    max-width: 1440px;
}

/* ── Sidebar ────────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(175deg, #0a1628 0%, #0f1f3d 55%, #162d50 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] > div { padding: 1.8rem 1.3rem; }
section[data-testid="stSidebar"] * { color: #dde8f8 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
    font-weight: 700;
    letter-spacing: -0.02em;
}
section[data-testid="stSidebar"] label {
    color: #7a9cc4 !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
section[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.07) !important;
    border: 1.5px solid rgba(255,255,255,0.12) !important;
    border-radius: 999px !important;
    color: #ffffff !important;
    padding: 9px 18px !important;
    font-size: 0.875rem !important;
    transition: all 0.2s !important;
}
section[data-testid="stSidebar"] .stTextInput input:focus {
    border-color: #1a73e8 !important;
    box-shadow: 0 0 0 3px rgba(26,115,232,0.22) !important;
    background: rgba(255,255,255,0.1) !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.07) !important;
    border: 1.5px solid rgba(255,255,255,0.12) !important;
    border-radius: 999px !important;
    color: #ffffff !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.08) !important;
    margin: 1.2rem 0 !important;
}
section[data-testid="stSidebar"] .stCaption {
    color: #5a7a9e !important;
    font-size: 0.75rem !important;
}

/* ── Section Headers ────────────────────────────────────────────────────────── */
.section-header {
    background: linear-gradient(92deg, #0f1f3d 0%, #1253a4 60%, #1a73e8 100%);
    color: #ffffff !important;
    padding: 14px 24px;
    border-radius: 10px;
    font-size: 0.82rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 36px 0 18px 0;
    box-shadow: 0 4px 18px rgba(26,115,232,0.28);
}

/* ── Metric Cards ───────────────────────────────────────────────────────────── */
div[data-testid="metric-container"] {
    background: #ffffff;
    border-radius: 14px;
    padding: 22px 22px 22px 26px;
    box-shadow: 0 1px 3px rgba(15,31,61,0.05),
                0 6px 20px rgba(15,31,61,0.07);
    border-left: 4px solid #1a73e8;
    transition: transform 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(15,31,61,0.13);
}
div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 0.68rem !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: #7a8aaa !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 2.1rem !important;
    font-weight: 800 !important;
    color: #0f1f3d !important;
    letter-spacing: -0.04em !important;
    line-height: 1.15 !important;
}

/* ── Buttons ────────────────────────────────────────────────────────────────── */
.stButton > button {
    font-weight: 700 !important;
    font-size: 0.875rem !important;
    border-radius: 10px !important;
    padding: 11px 26px !important;
    transition: all 0.2s ease !important;
    border: none !important;
    letter-spacing: 0.02em !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0f1f3d 0%, #1a73e8 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 16px rgba(26,115,232,0.38) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #162d50 0%, #1557b0 100%) !important;
    box-shadow: 0 8px 24px rgba(26,115,232,0.50) !important;
    transform: translateY(-2px) !important;
}
.stButton > button[kind="secondary"] {
    background: #ffffff !important;
    color: #0f1f3d !important;
    border: 1.5px solid #cdd8e8 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #f0f4f8 !important;
    border-color: #1a73e8 !important;
    color: #1a73e8 !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #0f1f3d, #1a73e8) !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    border: none !important;
    box-shadow: 0 4px 16px rgba(26,115,232,0.32) !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(26,115,232,0.46) !important;
}

/* ── Inputs & Selects ───────────────────────────────────────────────────────── */
.stTextInput > div > input {
    border-radius: 9px !important;
    border: 1.5px solid #d0dcea !important;
    font-size: 0.9rem !important;
    padding: 10px 14px !important;
    background: #ffffff !important;
    transition: all 0.2s !important;
    color: #0f1f3d !important;
}
.stTextInput > div > input:focus {
    border-color: #1a73e8 !important;
    box-shadow: 0 0 0 3px rgba(26,115,232,0.14) !important;
}
.stSelectbox > div > div {
    border-radius: 9px !important;
    border: 1.5px solid #d0dcea !important;
    background: #ffffff !important;
}

/* ── File Uploader ──────────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: #ffffff;
    border-radius: 14px !important;
    border: 2px dashed #c0d2e8 !important;
    transition: border-color 0.2s;
    padding: 6px;
}
[data-testid="stFileUploader"]:hover {
    border-color: #1a73e8 !important;
}

/* ── Dataframe ──────────────────────────────────────────────────────────────── */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 1px 4px rgba(15,31,61,0.07),
                0 4px 14px rgba(15,31,61,0.06) !important;
}

/* ── Alerts ─────────────────────────────────────────────────────────────────── */
.stAlert { border-radius: 10px !important; font-size: 0.875rem !important; }

/* ── Report Box ─────────────────────────────────────────────────────────────── */
.report-box {
    background: #ffffff;
    border-radius: 14px;
    padding: 36px 40px;
    box-shadow: 0 1px 4px rgba(15,31,61,0.05),
                0 10px 30px rgba(15,31,61,0.09);
    border-top: 5px solid #1a73e8;
    line-height: 1.9;
    font-size: 0.93rem;
    color: #1c2b48;
}

/* ── Status badges ──────────────────────────────────────────────────────────── */
.badge-green  { background:#e8f5e9; color:#1b5e20; padding:4px 12px; border-radius:999px;
                font-weight:700; font-size:0.76rem; letter-spacing:0.04em; border:1px solid #a5d6a7; }
.badge-orange { background:#fff3e0; color:#bf360c; padding:4px 12px; border-radius:999px;
                font-weight:700; font-size:0.76rem; letter-spacing:0.04em; border:1px solid #ffcc80; }
.badge-red    { background:#ffebee; color:#b71c1c; padding:4px 12px; border-radius:999px;
                font-weight:700; font-size:0.76rem; letter-spacing:0.04em; border:1px solid #ef9a9a; }

/* ── Slider ─────────────────────────────────────────────────────────────────── */
.stSlider > div > div > div { background: linear-gradient(90deg,#1a73e8,#0056cc) !important; }

/* ── Dividers ───────────────────────────────────────────────────────────────── */
hr { border:none !important; border-top:1px solid #e4ecf4 !important; margin:1.5rem 0 !important; }

/* ── Caption ────────────────────────────────────────────────────────────────── */
.stCaption { color:#7a8aaa !important; font-size:0.8rem !important; }

/* ── Hide Streamlit chrome ──────────────────────────────────────────────────── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 M&E Copilot")
    st.markdown("*AI-powered M&E reporting for NGOs*")
    st.markdown("---")
    st.markdown("### ⚙️ API Settings")
    api_key = st.text_input(
        "Qwen API Key",
        type="password",
        placeholder="sk-...",
        help="Get your key at: dashscope.aliyuncs.com"
    )
    model_choice = st.selectbox(
        "Model",
        ["qwen-plus", "qwen-turbo", "qwen-max"],
        index=0,
        help="qwen-plus is recommended for M&E reports"
    )
    st.markdown("---")
    st.markdown("### 📖 How to use")
    st.markdown("""
1. Enter your Qwen API key  
2. Upload your M&E data (CSV or Excel)  
3. Map your indicator columns  
4. Click **Analyze**  
5. Download your report  
""")
    st.markdown("---")
    st.markdown("### 📌 Sample columns expected")
    st.markdown("`Indicator` · `Target` · `Actual`")
    st.markdown("---")
    st.caption("Built by Falluck Malenga · Blantyre, Malawi")

# ── Hero banner ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#0a1628 0%,#0f1f3d 40%,#1253a4 75%,#1a73e8 100%);
            border-radius:18px;padding:44px 48px;margin-bottom:28px;
            position:relative;overflow:hidden;
            box-shadow:0 8px 32px rgba(15,31,61,0.22);">
    <div style="position:absolute;top:-40px;right:-40px;width:200px;height:200px;
                background:rgba(255,255,255,0.04);border-radius:50%;"></div>
    <div style="position:absolute;bottom:-60px;right:120px;width:150px;height:150px;
                background:rgba(26,115,232,0.12);border-radius:50%;"></div>
    <div style="display:inline-flex;align-items:center;gap:7px;
                background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.18);
                border-radius:999px;padding:5px 14px;margin-bottom:18px;">
        <span style="color:#7ec8ff;font-size:0.72rem;font-weight:700;
                     letter-spacing:0.1em;text-transform:uppercase;">
            ✦ Powered by Qwen AI
        </span>
    </div>
    <h1 style="color:#ffffff;margin:0 0 12px 0;font-size:2.6rem;
               font-weight:800;letter-spacing:-0.04em;line-height:1.1;">
        📊 M&amp;E Copilot
    </h1>
    <p style="color:#a8ccf0;margin:0 0 24px 0;font-size:1.08rem;
              font-weight:400;max-width:580px;line-height:1.6;">
        Upload your project data and get AI-generated indicator analysis,
        root cause insights, and a donor-ready report in under 20 minutes.
    </p>
    <div style="display:flex;gap:10px;flex-wrap:wrap;">
        <span style="background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.15);
                     color:#d0e8ff;border-radius:999px;padding:5px 14px;
                     font-size:0.78rem;font-weight:600;">📂 CSV &amp; Excel</span>
        <span style="background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.15);
                     color:#d0e8ff;border-radius:999px;padding:5px 14px;
                     font-size:0.78rem;font-weight:600;">📈 KPI Dashboard</span>
        <span style="background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.15);
                     color:#d0e8ff;border-radius:999px;padding:5px 14px;
                     font-size:0.78rem;font-weight:600;">🔬 Root Cause AI</span>
        <span style="background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.15);
                     color:#d0e8ff;border-radius:999px;padding:5px 14px;
                     font-size:0.78rem;font-weight:600;">📝 Donor Reports</span>
        <span style="background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.15);
                     color:#d0e8ff;border-radius:999px;padding:5px 14px;
                     font-size:0.78rem;font-weight:600;">🌍 USAID · EU · UN</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Step 1: Upload ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Step 1 — Upload Project Data</div>', unsafe_allow_html=True)

col_up, col_info = st.columns([2, 1])
with col_up:
    uploaded_file = st.file_uploader(
        "Drop your CSV or Excel file here",
        type=["csv", "xlsx", "xls"],
        help="Accepted formats: .csv, .xlsx, .xls"
    )
with col_info:
    st.info("💡 Your file should have columns for **Indicator name**, **Target value**, and **Actual/Achieved value**.")

# ── Process file ───────────────────────────────────────────────────────────────
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Could not read file: {e}")
        st.stop()

    st.success(f"✅ File loaded — **{len(df)} rows** and **{len(df.columns)} columns**")

    # ── Step 2: Preview ────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Step 2 — Data Preview</div>', unsafe_allow_html=True)
    st.dataframe(df.head(10), use_container_width=True)

    # ── Step 3: Map columns ────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Step 3 — Map Your Indicator Columns</div>', unsafe_allow_html=True)
    cols = df.columns.tolist()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        indicator_col = st.selectbox("📋 Indicator Name", cols, index=0)
    with c2:
        target_col = st.selectbox("🎯 Target Value", cols, index=min(1, len(cols)-1))
    with c3:
        actual_col = st.selectbox("✅ Actual/Achieved", cols, index=min(2, len(cols)-1))
    with c4:
        project_name = st.text_input("🏷️ Project Name", value="NGO Project Report")

    report_period = st.text_input("📅 Reporting Period", value="Q2 2026 (April – June 2026)")

    # ── Analyze button ─────────────────────────────────────────────────────────
    if st.button("🔍 Analyze & Generate Report", type="primary", use_container_width=True):

        # Build analysis dataframe
        try:
            analysis_df = df[[indicator_col, target_col, actual_col]].copy()
            analysis_df.columns = ["Indicator", "Target", "Actual"]
            analysis_df["Target"] = pd.to_numeric(analysis_df["Target"], errors="coerce")
            analysis_df["Actual"] = pd.to_numeric(analysis_df["Actual"], errors="coerce")
            analysis_df.dropna(subset=["Target", "Actual"], inplace=True)
            analysis_df["Achievement (%)"] = (
                analysis_df["Actual"] / analysis_df["Target"] * 100
            ).round(1)
            analysis_df["Status"] = analysis_df["Achievement (%)"].apply(
                lambda x: "🟢 On Track" if x >= 80 else ("🟡 At Risk" if x >= 50 else "🔴 Off Track")
            )
        except Exception as e:
            st.error(f"Could not process columns: {e}")
            st.stop()

        # ── Step 4: KPI Dashboard ──────────────────────────────────────────────
        st.markdown('<div class="section-header">Step 4 — KPI Dashboard</div>', unsafe_allow_html=True)

        total     = len(analysis_df)
        on_track  = len(analysis_df[analysis_df["Achievement (%)"] >= 80])
        at_risk   = len(analysis_df[(analysis_df["Achievement (%)"] >= 50) & (analysis_df["Achievement (%)"] < 80)])
        off_track = len(analysis_df[analysis_df["Achievement (%)"] < 50])
        avg_ach   = analysis_df["Achievement (%)"].mean().round(1)

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("📌 Total Indicators", total)
        m2.metric("🟢 On Track",  on_track)
        m3.metric("🟡 At Risk",   at_risk)
        m4.metric("🔴 Off Track", off_track)
        m5.metric("📈 Avg Achievement", f"{avg_ach}%")

        # Bar chart
        fig_bar = px.bar(
            analysis_df,
            x="Indicator",
            y="Achievement (%)",
            color="Status",
            color_discrete_map={
                "🟢 On Track":  "#34a853",
                "🟡 At Risk":   "#fbbc04",
                "🔴 Off Track": "#ea4335"
            },
            title=f"Indicator Achievement — {project_name}",
            text="Achievement (%)"
        )
        fig_bar.add_hline(
            y=80, line_dash="dash", line_color="#888",
            annotation_text="80% threshold", annotation_position="top right"
        )
        fig_bar.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_bar.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis_title="Achievement (%)",
            xaxis_title="",
            showlegend=True,
            height=420
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Gauge chart — overall
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=avg_ach,
            title={"text": "Overall Project Achievement"},
            delta={"reference": 80},
            gauge={
                "axis": {"range": [0, 100]},
                "bar":  {"color": "#1a73e8"},
                "steps": [
                    {"range": [0,  50], "color": "#fce8e6"},
                    {"range": [50, 80], "color": "#fff3e0"},
                    {"range": [80, 100],"color": "#e6f4ea"}
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 80
                }
            }
        ))
        fig_gauge.update_layout(height=280, paper_bgcolor="white")
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Indicator table
        st.dataframe(analysis_df, use_container_width=True, hide_index=True)

        # ── Step 5: AI Layer ───────────────────────────────────────────────────
        st.markdown('<div class="section-header">Step 5 — AI Intelligence Layer (Powered by Qwen)</div>', unsafe_allow_html=True)

        if not api_key:
            st.warning("⚠️ Enter your Qwen API key in the sidebar to unlock all AI features.")
        else:
            client = OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            data_str = analysis_df.to_string(index=False)

            # ── AI Feature 1: Root Cause Analysis ─────────────────────────────
            st.markdown("#### 🔬 AI Feature 1 — Root Cause Analysis")
            st.caption("Qwen AI analyses each off-track indicator and explains *why* it may be failing and what action to take.")

            off_track_df = analysis_df[analysis_df["Achievement (%)"] < 80]

            if len(off_track_df) == 0:
                st.success("All indicators are on track — no root cause analysis needed.")
            else:
                with st.spinner("🔍 Analysing root causes for off-track indicators..."):
                    try:
                        rca_prompt = f"""You are a senior M&E specialist reviewing underperforming project indicators.

Project: {project_name} | Period: {report_period}

Off-track indicators (below 80% achievement):
{off_track_df[['Indicator','Target','Actual','Achievement (%)']].to_string(index=False)}

For EACH indicator above, provide:
1. Most likely root cause (1-2 sentences — think about common NGO implementation challenges)
2. Immediate corrective action recommended (1 sentence)
3. Risk level if unaddressed: Low / Medium / High

Format each indicator as:
**[Indicator Name]** (Achievement: X%)
- Root Cause: ...
- Action: ...
- Risk if unaddressed: ...

Be specific and practical. Draw on real M&E field experience."""

                        rca_response = client.chat.completions.create(
                            model=model_choice,
                            messages=[{"role": "user", "content": rca_prompt}],
                            max_tokens=900
                        )
                        rca_text = rca_response.choices[0].message.content
                        st.session_state["rca_text"] = rca_text
                        st.markdown(
                            f'<div class="report-box">{rca_text.replace(chr(10), "<br>")}</div>',
                            unsafe_allow_html=True
                        )
                    except Exception as e:
                        st.error(f"Qwen API error (Root Cause): {e}")

            st.markdown("---")

            # ── AI Feature 2: End-of-Year Forecast ────────────────────────────
            st.markdown("#### 📈 AI Feature 2 — End-of-Year Forecast")
            st.caption("Qwen AI predicts whether each indicator will meet its annual target based on current trajectory.")

            quarters_elapsed = st.slider(
                "Quarters elapsed so far this year", 1, 4, 2,
                help="How many quarters of the project year have passed?"
            )

            with st.spinner("📊 Generating end-of-year forecast..."):
                try:
                    forecast_prompt = f"""You are an M&E data analyst forecasting project performance.

Project: {project_name} | Period: {report_period}
Quarters elapsed: {quarters_elapsed} of 4

Current indicator data:
{data_str}

For each indicator, calculate and state:
1. Projected year-end achievement % (extrapolate linearly from current progress)
2. Forecast verdict: Will Meet Target / At Risk of Missing / Will Miss Target
3. One-sentence explanation

Format as a clean table using markdown:
| Indicator | Current % | Projected Year-End % | Forecast Verdict |
|-----------|-----------|----------------------|------------------|

Then write 2-sentence overall project forecast summary below the table."""

                    forecast_response = client.chat.completions.create(
                        model=model_choice,
                        messages=[{"role": "user", "content": forecast_prompt}],
                        max_tokens=800
                    )
                    forecast_text = forecast_response.choices[0].message.content
                    st.session_state["forecast_text"] = forecast_text
                    st.markdown(
                        f'<div class="report-box">{forecast_text}</div>',
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.error(f"Qwen API error (Forecast): {e}")

            st.markdown("---")

            # ── AI Feature 3: Donor Report with Format Switching ──────────────
            st.markdown("#### 📝 AI Feature 3 — Donor Report Generator")
            st.caption("Qwen AI writes the full report in your chosen donor's exact language and structure.")

            donor_format = st.selectbox(
                "Select donor report format",
                ["Generic NGO", "USAID", "European Union (EU)", "United Nations (UN)", "Global Fund"],
                index=0
            )

            donor_instructions = {
                "Generic NGO": "Use standard NGO progress reporting language with clear sections.",
                "USAID": "Follow USAID reporting standards. Use terms like 'beneficiaries', 'indicators of performance', 'host country partners'. Include a Performance Management Plan (PMP) style narrative.",
                "European Union (EU)": "Follow EU grant reporting format. Use terms like 'action', 'contracting authority', 'target groups', 'result indicators'. Reference EU visibility guidelines.",
                "United Nations (UN)": "Follow UN Results-Based Management (RBM) framework. Use outcome/output/activity language. Reference SDG alignment where relevant.",
                "Global Fund": "Follow Global Fund Progress Update/Disbursement Request (PUDR) language. Emphasise absorption rates, coverage, and system-level change."
            }

            with st.spinner(f"✍️ Writing {donor_format} format report..."):
                try:
                    report_prompt = f"""You are a senior M&E officer writing a formal donor progress report.

Project: {project_name} | Period: {report_period}
Donor Format: {donor_format}
Format Instructions: {donor_instructions[donor_format]}

Indicator Data:
{data_str}

Write a complete donor progress report with:
1. Executive Summary (3 sentences)
2. Progress Against Indicators (one paragraph per indicator with exact numbers)
3. Key Achievements
4. Challenges and Risks (flag indicators below 50%)
5. Recommendations

Rules:
- Strictly follow {donor_format} reporting language and structure
- Cite all numbers and percentages from the data
- 450–600 words total
- No placeholders"""

                    report_response = client.chat.completions.create(
                        model=model_choice,
                        messages=[{"role": "user", "content": report_prompt}],
                        max_tokens=1400
                    )
                    narrative = report_response.choices[0].message.content
                    st.session_state["narrative"] = narrative
                    st.session_state["donor_format"] = donor_format

                    st.markdown(
                        f'<div class="report-box">{narrative.replace(chr(10), "<br>")}</div>',
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.error(f"Qwen API error (Report): {e}")
                    narrative = "[Report not generated — check API key]"
                    st.session_state["narrative"] = narrative

        # ── Step 6: Download ───────────────────────────────────────────────────
        st.markdown('<div class="section-header">Step 6 — Download Full Report Package</div>', unsafe_allow_html=True)

        narrative_text = st.session_state.get("narrative", "[Report not generated]")
        rca_text       = st.session_state.get("rca_text",  "[Root cause analysis not generated]")
        forecast_text  = st.session_state.get("forecast_text", "[Forecast not generated]")
        donor_fmt      = st.session_state.get("donor_format", "Generic NGO")

        report_txt = f"""M&E COPILOT - FULL DONOR REPORT PACKAGE
{'='*60}
Project      : {project_name}
Period       : {report_period}
Donor Format : {donor_fmt}
Generated    : {datetime.now().strftime('%d %B %Y, %H:%M')}
{'='*60}

SECTION 1 - DONOR PROGRESS REPORT
{'='*60}
{narrative_text}

{'='*60}
SECTION 2 - ROOT CAUSE ANALYSIS (AI-Generated)
{'='*60}
{rca_text}

{'='*60}
SECTION 3 - END-OF-YEAR FORECAST (AI-Generated)
{'='*60}
{forecast_text}

{'='*60}
SECTION 4 - INDICATOR DATA TABLE
{'='*60}
{analysis_df.to_string(index=False)}

{'='*60}
Generated by M&E Copilot · Powered by Qwen AI · Built by Falluck Malenga
"""

        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                label="📥 Download Report (.txt)",
                data=report_txt,
                file_name=f"me_copilot_report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with dl2:
            csv_data = analysis_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Data Table (.csv)",
                data=csv_data,
                file_name=f"indicator_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.success("✅ Analysis complete! Your report is ready to download.")

else:
    # Empty state
    st.markdown("""
    <div style="text-align:center; padding:60px 20px; background:white;
                border-radius:16px; border:2px dashed #c0d0e8;">
        <div style="font-size:3rem;">📂</div>
        <h3 style="color:#1a2e4a;">Upload your M&E data to get started</h3>
        <p style="color:#555;">Accepted formats: CSV (.csv) · Excel (.xlsx / .xls)</p>
    </div>
    """, unsafe_allow_html=True)
