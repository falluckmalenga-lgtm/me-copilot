import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="M&E Copilot - Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional design
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] .stText {
        color: #FFFFFF;
    }
    
    [data-testid="stSidebar"] a {
        color: #94A3B8;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom card styling */
    .kpi-card {
        background-color: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #E2E8F0;
        margin-bottom: 16px;
    }
    
    .kpi-title {
        color: #64748B;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 8px;
    }
    
    .kpi-value {
        color: #0F172A;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    
    .kpi-trend-positive {
        color: #10B981;
        font-size: 14px;
        font-weight: 600;
    }
    
    .kpi-trend-negative {
        color: #EF4444;
        font-size: 14px;
        font-weight: 600;
    }
    
    /* Alert cards */
    .alert-card {
        background-color: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 4px solid;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .alert-success {
        border-left-color: #10B981;
        background-color: #F0FDF4;
    }
    
    .alert-warning {
        border-left-color: #F59E0B;
        background-color: #FFFBEB;
    }
    
    .alert-danger {
        border-left-color: #EF4444;
        background-color: #FEF2F2;
    }
    
    /* Donor cards */
    .donor-card {
        background-color: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #E2E8F0;
        height: 100%;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #1D4ED8;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
    }
    
    /* Header */
    .main-header {
        background-color: white;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .header-title {
        color: #0F172A;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    
    .header-subtitle {
        color: #64748B;
        font-size: 16px;
    }
    
    /* Activity items */
    .activity-item {
        display: flex;
        align-items: center;
        padding: 12px;
        background-color: white;
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid #E2E8F0;
    }
    
    /* Custom selectbox */
    .stSelectbox>div>div {
        background-color: white;
        border: 1px solid #CBD5E1;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.markdown("<h2 style='color: white; margin-bottom: 40px;'>📊 M&E Copilot</h2>", unsafe_allow_html=True)
    
    menu_items = [
        ("Dashboard", "📈"),
        ("Data Upload", "📁"),
        ("Analytics", "📊"),
        ("AI Insights", "🤖"),
        ("Reports", "📑"),
        ("Compliance", "✅"),
        ("Settings", "⚙️")
    ]
    
    for item, icon in menu_items:
        if item == "Dashboard":
            st.markdown(f"<div style='background-color: #2563EB; color: white; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; font-weight: 600;'>{icon} {item}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='color: #94A3B8; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; cursor: pointer;'>{icon} {item}</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 60px; padding-top: 20px; border-top: 1px solid #1E293B;'></div>", unsafe_allow_html=True)
    
    # User profile
    st.markdown("""
    <div style='display: flex; align-items: center; padding: 12px; background-color: #1E293B; border-radius: 8px; margin-bottom: 12px;'>
        <div style='width: 40px; height: 40px; background-color: #2563EB; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px;'>
            <span style='color: white; font-weight: 600;'>JD</span>
        </div>
        <div>
            <div style='color: white; font-weight: 600; font-size: 14px;'>John Doe</div>
            <div style='color: #94A3B8; font-size: 12px;'>M&E Officer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_out = True

# Main Content
# Header
st.markdown("""
<div class='main-header'>
    <div class='header-title'>Monitoring & Evaluation Intelligence Platform</div>
    <div class='header-subtitle'>Transform project data into actionable insights, donor-ready reports, compliance monitoring, and AI-powered recommendations.</div>
</div>
""", unsafe_allow_html=True)

# Top filters row
col_filter1, col_filter2, col_filter3 = st.columns([6, 1, 1])
with col_filter1:
    pass  # Empty space
with col_filter2:
    st.selectbox("", ["Last 6 Months", "Last 3 Months", "Last Year", "Custom Range"], label_visibility="collapsed")
with col_filter3:
    st.markdown("<div style='text-align: right;'>🔔 👤</div>", unsafe_allow_html=True)

# KPI Cards
st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.markdown("""
    <div class='kpi-card'>
        <div class='kpi-title'>Total Indicators</div>
        <div class='kpi-value'>1,248</div>
        <div class='kpi-trend-positive'>↑ +12.4%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown("""
    <div class='kpi-card'>
        <div class='kpi-title'>Overall Progress</div>
        <div class='kpi-value'>68.4%</div>
        <div class='kpi-trend-positive'>↑ +8.7%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown("""
    <div class='kpi-card'>
        <div class='kpi-title'>At Risk</div>
        <div class='kpi-value'>216</div>
        <div class='kpi-trend-negative'>↓ -5.4%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown("""
    <div class='kpi-card'>
        <div class='kpi-title'>Budget Utilization</div>
        <div class='kpi-value'>68%</div>
        <div class='kpi-trend-positive'>↑ +4.1%</div>
    </div>
    """, unsafe_allow_html=True)

# Main content area - Chart and AI Insights
chart_col, insights_col = st.columns([2, 1])

with chart_col:
    st.markdown("<div class='kpi-card'><h3 style='margin-bottom: 20px; color: #0F172A;'>Project Performance Chart</h3>", unsafe_allow_html=True)
    
    # Create sample data
    months = ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May']
    values = [45, 52, 48, 61, 65, 68.4]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months,
        y=values,
        mode='lines+markers',
        line=dict(color='#2563EB', width=3, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(37, 99, 235, 0.1)',
        marker=dict(size=8, color='#2563EB')
    ))
    
    fig.update_layout(
        height=300,
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#E2E8F0', zeroline=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with insights_col:
    st.markdown("<h3 style='margin-bottom: 16px; color: #0F172A;'>AI Insights</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='alert-card alert-success'>
        <div style='color: #065F46; font-weight: 600;'>✓ Data quality improved by 12%</div>
    </div>
    <div class='alert-card alert-warning'>
        <div style='color: #92400E; font-weight: 600;'>⚠ 5 indicators require review</div>
    </div>
    <div class='alert-card alert-danger'>
        <div style='color: #991B1B; font-weight: 600;'>ℹ Budget utilization below target</div>
    </div>
    """, unsafe_allow_html=True)

# Recent Activity and Performance Monitoring
activity_col, perf_col = st.columns(2)

with activity_col:
    st.markdown("<h3 style='margin-bottom: 16px; color: #0F172A;'>Recent Activity</h3>", unsafe_allow_html=True)
    
    activities = [
        ("📁", "Data uploaded", "2 hours ago"),
        ("📑", "Report generated", "5 hours ago"),
        ("✅", "Compliance check completed", "1 day ago"),
        ("🤖", "AI analysis completed", "2 days ago")
    ]
    
    for icon, activity, time in activities:
        st.markdown(f"""
        <div class='activity-item'>
            <span style='font-size: 20px; margin-right: 12px;'>{icon}</span>
            <div style='flex: 1;'>
                <div style='font-weight: 600; color: #0F172A;'>{activity}</div>
                <div style='font-size: 12px; color: #94A3B8;'>{time}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with perf_col:
    st.markdown("<h3 style='margin-bottom: 16px; color: #0F172A;'>Performance Monitoring</h3>", unsafe_allow_html=True)
    
    perf_col1, perf_col2, perf_col3 = st.columns(3)
    
    with perf_col1:
        # Gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=85,
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'font': {'size': 24, 'color': '#0F172A'}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#CBD5E1"},
                'bar': {'color': "#2563EB"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#E2E8F0",
                'steps': [
                    {'range': [0, 50], 'color': '#FEE2E2'},
                    {'range': [50, 80], 'color': '#FEF3C7'},
                    {'range': [80, 100], 'color': '#D1FAE5'}
                ],
            }
        ))
        fig_gauge.update_layout(height=200, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown("<div style='text-align: center; color: #64748B; font-size: 12px;'>Project Health Score</div>", unsafe_allow_html=True)
    
    with perf_col2:
        # Data Quality Score
        fig_circle = go.Figure(go.Indicator(
            mode="gauge+number",
            value=92,
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'font': {'size': 24, 'color': '#0F172A'}},
            gauge={
                'axis': {'range': [None, 100], 'visible': False},
                'bar': {'color': "#2563EB", 'thickness': 0.5},
                'bgcolor': "white",
                'steps': [],
                'shape': "bullet"
            }
        ))
        fig_circle.update_layout(height=200, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_circle, use_container_width=True)
        st.markdown("<div style='text-align: center; color: #64748B; font-size: 12px;'>Data Quality Score</div>", unsafe_allow_html=True)
    
    with perf_col3:
        # Risk Matrix (simplified)
        risk_data = np.array([[1, 2, 3], [2, 3, 4], [3, 4, 5]])
        fig_risk = px.imshow(risk_data, 
                            color_continuous_scale=['#D1FAE5', '#FEF3C7', '#FEE2E2'],
                            x=['Low', 'Med', 'High'],
                            y=['High', 'Med', 'Low'],
                            labels=dict(x="Likelihood", y="Impact"))
        fig_risk.update_layout(height=200, margin=dict(l=0, r=0, t=30, b=0), 
                              coloraxis_showscale=False,
                              xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_risk, use_container_width=True)
        st.markdown("<div style='text-align: center; color: #64748B; font-size: 12px;'>Risk Matrix</div>", unsafe_allow_html=True)

# Quick Actions
st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
st.markdown("<h3 style='margin-bottom: 16px; color: #0F172A;'>Quick Actions</h3>", unsafe_allow_html=True)
action_col1, action_col2, action_col3, action_col4 = st.columns(4)

with action_col1:
    if st.button("📁 Upload Data", use_container_width=True):
        st.info("Upload functionality would open here")
with action_col2:
    if st.button("🤖 AI Analysis", use_container_width=True):
        st.info("AI Analysis would run here")
with action_col3:
    if st.button("📑 Donor Reports", use_container_width=True):
        st.info("Report generation would start here")
with action_col4:
    if st.button("✅ Compliance Check", use_container_width=True):
        st.info("Compliance check would run here")

# Donor Reporting Section
st.markdown("<div style='margin: 32px 0;'></div>", unsafe_allow_html=True)
st.markdown("<h3 style='margin-bottom: 20px; color: #0F172A;'>Donor Reporting</h3>", unsafe_allow_html=True)
donor_col1, donor_col2, donor_col3 = st.columns(3)

with donor_col1:
    st.markdown("""
    <div class='donor-card'>
        <div style='display: flex; align-items: center; margin-bottom: 12px;'>
            <div style='font-size: 32px; margin-right: 12px;'>🇺🇸</div>
            <div>
                <div style='font-weight: 700; color: #0F172A; font-size: 18px;'>USAID Reports</div>
                <div style='color: #64748B; font-size: 14px;'>ADS 201 Compliant</div>
            </div>
        </div>
        <div style='color: #64748B; font-size: 14px; margin-bottom: 16px;'>Customized reporting templates aligned with USAID ADS 201 requirements</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Generate Report", key="usaid", use_container_width=True):
        st.success("USAID report generated!")

with donor_col2:
    st.markdown("""
    <div class='donor-card'>
        <div style='display: flex; align-items: center; margin-bottom: 12px;'>
            <div style='font-size: 32px; margin-right: 12px;'>🇪🇺</div>
            <div>
                <div style='font-weight: 700; color: #0F172A; font-size: 18px;'>EU Reports</div>
                <div style='color: #64748B; font-size: 14px;'>DG DEVCO Compliant</div>
            </div>
        </div>
        <div style='color: #64748B; font-size: 14px; margin-bottom: 16px;'>DG DEVCO & DG INTPA compliant formats and templates</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Generate Report", key="eu", use_container_width=True):
        st.success("EU report generated!")

with donor_col3:
    st.markdown("""
    <div class='donor-card'>
        <div style='display: flex; align-items: center; margin-bottom: 12px;'>
            <div style='font-size: 32px; margin-right: 12px;'>🌍</div>
            <div>
                <div style='font-weight: 700; color: #0F172A; font-size: 18px;'>UN Reports</div>
                <div style='color: #64748B; font-size: 14px;'>SDG-Aligned</div>
            </div>
        </div>
        <div style='color: #64748B; font-size: 14px; margin-bottom: 16px;'>UNDP Results-Based Management & SDG-aligned outputs</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Generate Report", key="un", use_container_width=True):
        st.success("UN report generated!")

# Export Section
st.markdown("<div style='margin: 32px 0;'></div>", unsafe_allow_html=True)
st.markdown("<h3 style='margin-bottom: 16px; color: #0F172A;'>Export</h3>", unsafe_allow_html=True)
export_col1, export_col2, export_col3 = st.columns(3)

with export_col1:
    if st.button("📄 Export as PDF", use_container_width=True):
        st.success("PDF export started!")
with export_col2:
    if st.button("📊 Export as Excel", use_container_width=True):
        st.success("Excel export started!")
with export_col3:
    if st.button("📽 Export as PowerPoint", use_container_width=True):
        st.success("PowerPoint export started!")

# Footer
st.markdown("<div style='margin: 40px 0; padding: 20px; text-align: center; color: #94A3B8; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
st.markdown("© 2024 M&E Copilot - Powered by Qwen Cloud AI", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)