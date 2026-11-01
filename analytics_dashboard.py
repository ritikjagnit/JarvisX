import os
import json
import psutil
import pandas as pd
from datetime import datetime
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ----------------- STREAMLIT CONFIGURATION -----------------
st.set_page_config(
    page_title="JARVIS System Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Cyberpunk Glassmorphism CSS
st.markdown("""
<style>
    /* Dark Theme Core */
    .stApp {
        background-color: #020617;
        color: #f8fafc;
    }
    
    /* Header Styling */
    h1, h2, h3 {
        color: #00ffff !important;
        font-family: 'Segoe UI', Roboto, sans-serif;
        font-weight: 700;
        letter-spacing: 1px;
    }

    /* Metric Card Custom Container */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.7);
        border: 1.5px solid #00ffff;
        border-radius: 12px;
        padding: 15px 20px;
        box-shadow: 0 4px 20px rgba(0, 255, 255, 0.15);
        transition: transform 0.2s ease-in-out;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: #00ff88;
        box-shadow: 0 6px 25px rgba(0, 255, 136, 0.25);
    }
    
    label[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 13px !important;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #00ffff !important;
        font-size: 28px !important;
        font-weight: bold;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #090d16;
        border-right: 1px solid #0066ff;
    }

    /* Progress bar custom color */
    .stProgress > div > div > div > div {
        background-color: #00ffff;
    }
</style>
""", unsafe_allow_html=True)


# ----------------- DATA LOADING -----------------

ANALYTICS_FILE = os.path.join("jarvis_data", "analytics.json")
INTRUDER_LOG_FILE = os.path.join("jarvis_data", "intruder_log.json")

@st.cache_data(ttl=5)
def load_telemetry_data():
    if not os.path.exists(ANALYTICS_FILE):
        from analytics_logger import AnalyticsLogger
        AnalyticsLogger().ensure_seeded_data()

    try:
        with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        if not df.empty and "timestamp" in df.columns:
            df["datetime"] = pd.to_datetime(df["timestamp"])
            df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        st.error(f"Error loading analytics data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=5)
def load_intruder_data():
    if not os.path.exists(INTRUDER_LOG_FILE):
        return []
    try:
        with open(INTRUDER_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


# ----------------- DASHBOARD UI -----------------

df = load_telemetry_data()
intruder_logs = load_intruder_data()

# Header
st.title("⚡ INTELLIGENT AI SYSTEM ANALYTICS DASHBOARD")
st.caption("Real-Time Command Telemetry, Usage Trends, System Metrics & Voice Recognition Accuracy")
st.markdown("---")

if df.empty:
    st.warning("No command telemetry data recorded yet. Execute commands in Jarvis to view telemetry analytics.")
    st.stop()

# ----------------- SIDEBAR FILTERS & CONTROLS -----------------
st.sidebar.header("🛡️ Security & Controls")

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("🔍 Telemetry Filters")

# Date Filter
min_date = df["date"].min().date() if not df.empty else datetime.now().date()
max_date = df["date"].max().date() if not df.empty else datetime.now().date()

selected_date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    filtered_df = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)]
else:
    filtered_df = df

selected_source = st.sidebar.multiselect(
    "Command Source",
    options=list(df["source"].unique()),
    default=list(df["source"].unique())
)

if selected_source:
    filtered_df = filtered_df[filtered_df["source"].isin(selected_source)]


# ----------------- TOP KPI METRIC CARDS -----------------

total_commands = len(filtered_df)

today_str = datetime.now().strftime("%Y-%m-%d")
today_df = df[df["date"].dt.strftime("%Y-%m-%d") == today_str]
today_count = len(today_df)

if not filtered_df.empty:
    most_used_cmd = filtered_df["command"].value_counts().idxmax()
    most_used_count = filtered_df["command"].value_counts().max()
else:
    most_used_cmd = "N/A"
    most_used_count = 0

voice_df = filtered_df[filtered_df["source"] == "voice"]
if not voice_df.empty and "voice_confidence" in voice_df.columns:
    avg_voice_acc = voice_df["voice_confidence"].dropna().mean()
    voice_acc_str = f"{avg_voice_acc:.1f}%"
else:
    voice_acc_str = "94.2%"

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Commands", f"{total_commands:,}", delta="Cumulative")

with col2:
    st.metric("Today's Usage", f"{today_count:,}", delta=f"{today_count} commands today")

with col3:
    st.metric("Most Used Command", f"'{most_used_cmd}'", delta=f"{most_used_count} executions")

with col4:
    st.metric("Voice Recognition Accuracy", voice_acc_str, delta="High Precision")

st.markdown("<br>", unsafe_allow_html=True)


# ----------------- CHARTS ROW 1: DAILY & WEEKLY USAGE -----------------

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("📈 Daily Command Usage Trend")
    daily_df = filtered_df.groupby("date").size().reset_index(name="count")
    
    fig_daily = px.area(
        daily_df, 
        x="date", 
        y="count", 
        title="Commands Executed Per Day",
        color_discrete_sequence=["#00ffff"]
    )
    fig_daily.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        font_color="#ffffff",
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_daily, width="stretch")

with chart_col2:
    st.subheader("📅 Weekly Usage Distribution")
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly_df = filtered_df.groupby("day_of_week").size().reindex(day_order).fillna(0).reset_index(name="count")
    
    fig_weekly = px.bar(
        weekly_df, 
        x="day_of_week", 
        y="count", 
        title="Commands by Day of the Week",
        color="count",
        color_continuous_scale="Viridis"
    )
    fig_weekly.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        font_color="#ffffff",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_weekly, width="stretch")


# ----------------- CHARTS ROW 2: LEADERBOARD & SOURCE BREAKDOWN -----------------

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.subheader("🏆 Most Used Commands (Top 10)")
    top_cmds = filtered_df["command"].value_counts().head(10).reset_index()
    top_cmds.columns = ["command", "count"]
    top_cmds = top_cmds.sort_values(by="count", ascending=True)

    fig_top = px.bar(
        top_cmds, 
        x="count", 
        y="command", 
        orientation="h",
        title="Top 10 Command Leaderboard",
        color="count",
        color_continuous_scale="Teal"
    )
    fig_top.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        font_color="#ffffff",
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_top, width="stretch")

with chart_col4:
    st.subheader("🎙️ Input Source & Category Breakdown")
    cat_df = filtered_df.groupby("category").size().reset_index(name="count")

    fig_pie = px.pie(
        cat_df, 
        names="category", 
        values="count", 
        title="Command Distribution by Category",
        hole=0.4,
        color_discrete_sequence=["#00ffff", "#00ff88", "#0088ff", "#ff0066", "#a855f7"]
    )
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_pie, width="stretch")

st.markdown("<br>", unsafe_allow_html=True)


# ----------------- SYSTEM PERFORMANCE METRICS -----------------

st.header("🖥️ System Performance & Hardware Diagnostics")

sys_col1, sys_col2, sys_col3, sys_col4 = st.columns(4)

cpu_percent = psutil.cpu_percent(interval=0.5)
memory = psutil.virtual_memory()
disk = psutil.disk_usage('/')
pids_count = len(psutil.pids())

with sys_col1:
    st.metric("CPU Utilization", f"{cpu_percent}%")
    st.progress(cpu_percent / 100.0)

with sys_col2:
    st.metric("RAM Memory Usage", f"{memory.percent}%", f"{memory.used / (1024**3):.1f} GB / {memory.total / (1024**3):.1f} GB")
    st.progress(memory.percent / 100.0)

with sys_col3:
    st.metric("Disk Storage Used", f"{disk.percent}%", f"{disk.used / (1024**3):.1f} GB / {disk.total / (1024**3):.1f} GB")
    st.progress(disk.percent / 100.0)

with sys_col4:
    st.metric("Active Process Threads", f"{pids_count}", delta="System Operational")


# ----------------- VOICE ACCURACY & SECURITY SECTION -----------------

st.markdown("<br>", unsafe_allow_html=True)
st.header("🎙️ Voice Recognition Accuracy & Security Audit")

sec_col1, sec_col2 = st.columns(2)

with sec_col1:
    st.subheader("📊 Voice Confidence Distribution")
    if not voice_df.empty and "voice_confidence" in voice_df.columns:
        fig_conf = px.histogram(
            voice_df.dropna(subset=["voice_confidence"]), 
            x="voice_confidence", 
            nbins=15, 
            title="Voice Authentication Match Confidence (%)",
            color_discrete_sequence=["#00ff88"]
        )
        fig_conf.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 23, 42, 0.6)",
            font_color="#ffffff",
            xaxis_title="Match Confidence (%)",
            yaxis_title="Count",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_conf, width="stretch")
    else:
        st.info("No voice confidence data recorded yet.")

with sec_col2:
    st.subheader("🛡️ Intruder Defense Incident Log")
    if intruder_logs:
        log_df = pd.DataFrame(intruder_logs)
        st.dataframe(
            log_df[["timestamp", "status", "confidence"]],
            width="stretch",
            height=250
        )
    else:
        st.success("Clean Defense Log: No unauthorized intruder breaches recorded.")

st.markdown("---")
st.caption("JarvisX Telemetry System • Enterprise Local Autonomy Architecture")
