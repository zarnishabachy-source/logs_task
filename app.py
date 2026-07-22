"""
Multi Log Type Analytics Dashboard
Run: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Log Analytics Dashboard", layout="wide")

#  FORCE LIGHT THEME & FIXED SIDEBAR INPUTS CSS 
st.markdown("""
    <style>
    /* 1. Main Canvas Background */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #E4E9F0 !important;
        color: #2D3748 !important;
    }

    /* 2. Sidebar Styling (Dark Navy) */
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div {
        background-color: #183B56 !important;
    }
    
    /* Sidebar Text & Labels White */
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: #FFFFFF !important;
    }

    /* 3. FIX: Sidebar Specific Inputs & Selectboxes (Sleek Dark Style) */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] div[data-baseweb="input"] > div,
    [data-testid="stSidebar"] input {
        background-color: #0F2C59 !important;
        color: #FFFFFF !important;
        border: 1px solid #1A365D !important;
        border-radius: 8px !important;
    }

    /* Input Placeholders & Dropdown Icons */
    [data-testid="stSidebar"] div[data-baseweb="select"] svg {
        fill: #FFFFFF !important;
    }

    /* 4. Streamlit Metric Cards Styling (Top Stat Numbers) */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        padding: 15px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05) !important;
    }
    div[data-testid="stMetricValue"] {
        color: #0F2C59 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #8C9DAE !important;
    }
    </style>
""", unsafe_allow_html=True)

# COLOR PALETTE 
PIE_COLORS = ["#0F2C59", "#FF9A00", "#1A365D", "#FFA800", "#8C9DAE", "#2D3748"]
LINE_COLOR = "#FF9A00"
LINE_FILL_COLOR = "rgba(255, 154, 0, 0.2)"

METHOD_COLORS = ["#0F2C59", "#FF9A00", "#1A365D", "#FFA800", "#8C9DAE", "#2D3748"]

BAR_COLOR_1 = "#0F2C59"     # paths (Dark Navy)
BAR_COLOR_2 = "#FF9A00"     # client IPs (Vibrant Orange)
BAR_COLOR_3 = "#1A365D"     # controllers (Medium Navy)
BAR_COLOR_4 = "#FFA800"     # slow requests (Warm Amber)

PAGE_BG_COLOR = "#E4E9F0"
CARD_BG_COLOR = "#FFFFFF"
SIDEBAR_BG_COLOR = "#183B56"
TEXT_COLOR = "#2D3748"
MUTED_TEXT_COLOR = "#8C9DAE"
GRID_COLOR = "#E2E8F0"

# 6 LOG FILES 
DATA_FOLDER = Path("cleaned_files")

FILES = {
    "Started Request": DATA_FOLDER / "server-logs-table-Started_Request.csv",
    "Database Query": DATA_FOLDER / "server-logs-table-Database_Query.csv",
    "Render Template": DATA_FOLDER / "server-logs-table-Render_Template.csv",
    "Error / Exception": DATA_FOLDER / "server-logs-table-Error_Exception.csv",
    "General": DATA_FOLDER / "server-logs-table-General.csv",
    "Processing": DATA_FOLDER / "server-logs-table-Processing.csv",
    "Completed Request": DATA_FOLDER / "server-logs-table-Completed_Request.csv",
}

#  LOAD DATA 
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    for col in df.columns:
        if "time" in col.lower() or "timestamp" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


# SIDEBAR: LOG TYPE NAVIGATION 
st.sidebar.title("LOG ANALYTICS")
log_type = st.sidebar.radio("Log Types", list(FILES.keys()), index=1)

df = load_data(FILES[log_type])

# find the timestamp column automatically (each file may name it differently)
ts_col = next((c for c in df.columns if "time" in c.lower()), None)


# SIDEBAR: DYNAMIC FILTERS (only show if column exists) 
st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

filters = {}  # column -> selected values

if ts_col:
    min_d, max_d = df[ts_col].min(), df[ts_col].max()
    date_range = st.sidebar.date_input("Date Range", value=(min_d.date(), max_d.date()))
else:
    date_range = None

# common optional filter columns across log types
for col in ["Request Method", "Response Status", "Client IP", "Level",
            "Request Controller Action", "Request Path"]:
    if col in df.columns:
        filters[col] = st.sidebar.multiselect(col, sorted(df[col].dropna().unique()))

#  LIVE BADGE (TOP-RIGHT) 
st.markdown("""
    <div style="display: flex; justify-content: flex-end; margin-bottom: 15px;">
        <span style="
            background-color: #E6F4EA; 
            color: #137333; 
            padding: 5px 13px; 
            border-radius: 20px; 
            font-size: 12px; 
            font-weight: 600; 
            border: 1px solid #CEEAD6; 
            display: inline-flex; 
            align-items: center; 
            gap: 6px;
            white-space: nowrap;">
            <span style="width: 8px; height: 8px; background-color: #34A853; border-radius: 50%; display: inline-block;"></span> Live
        </span>
    </div>
""", unsafe_allow_html=True)

# FUNCTION: APPLY FILTERS TO ANY LOG TYPE 
def apply_filters(data):
    filtered = data.copy()
    if ts_col and date_range and len(date_range) == 2:
        start_date, end_date = date_range
        filtered = filtered[(filtered[ts_col].dt.date >= start_date) & (filtered[ts_col].dt.date <= end_date)]
    for col, selected in filters.items():
        if selected:
            filtered = filtered[filtered[col].isin(selected)]
    return filtered


filtered_df = apply_filters(df)


# HEADER
st.title(f"{log_type} Dashboard")
st.caption(f"Real-time monitoring & analysis of {log_type} logs")


# KPI CARDS (shown only if the underlying column exists) 
def draw_kpi_card(title, value, icon, badge_bg="rgba(255, 154, 0, 0.15)", icon_color="#FF9A00"):
    return f"""
    <div style="
        background-color: #FFFFFF;
        padding: 18px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #E2E8F0;
        min-height: 90px;">
        <div>
            <p style="color: #718096; margin: 0; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">{title}</p>
            <h2 style="color: #0F2C59; margin: 6px 0 0 0; font-weight: 800; font-size: 26px; line-height: 1.2;">{value}</h2>
        </div>
        <div style="
            background-color: {badge_bg};
            width: 44px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            color: {icon_color};">
            {icon}
        </div>
    </div>
    """

def show_kpis(data):
    # 1.colect active matircs (Title, Value, Icon)
    metrics = []
    
    metrics.append(("Total Logs", f"{len(data):,}", "📊"))

    if "Client IP" in data.columns:
        metrics.append(("Unique IPs", f"{data['Client IP'].nunique():,}", "🌐"))

    if "Request Path" in data.columns:
        metrics.append(("Unique Requests", f"{data['Request Path'].nunique():,}", "⚡"))

    if "Total Duration (ms)" in data.columns:
        metrics.append(("Avg. Duration", f"{data['Total Duration (ms)'].mean():.0f} ms", "⏱️"))

    if "PID" in data.columns:
        metrics.append(("Unique Processes", f"{data['PID'].nunique():,}", "⚙️"))

    # 2. Dynamic Columns Grid (Maximum 5 Columns)
    cols = st.columns(len(metrics) if len(metrics) <= 5 else 5)
    
    for idx, (title, value, icon) in enumerate(metrics):
        with cols[idx]:
            st.markdown(draw_kpi_card(title, value, icon), unsafe_allow_html=True)

# Function call
show_kpis(filtered_df)

# CHART ROW 1: distribution + trend + method 
c1, c2, c3 = st.columns(3)
# Function ko global scope me define kar lein taake sab charts me chale
def apply_card_style(fig):
    fig.update_layout(
        height=380,
        paper_bgcolor="#FFFFFF",   # Card container white
        plot_bgcolor="#FFFFFF",    # Plot background white
        font=dict(color="#2D3748", family="Arial, sans-serif"),
        xaxis=dict(showgrid=True, gridcolor="#E2E8F0", tickfont=dict(color="#2D3748")),
        yaxis=dict(showgrid=True, gridcolor="#E2E8F0", tickfont=dict(color="#2D3748")),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig



#  1. COLUMN 1: Donut Chart (Percentage inside + Clean Legend) 
with c1:
    dist_col = next((c for c in ["Response Status", "Level"] if c in filtered_df.columns), None)
    if dist_col:
        st.subheader(f"{dist_col} Distribution")
        counts = filtered_df[dist_col].value_counts().reset_index()
        counts.columns = [dist_col, "Count"]

        fig_pie = px.pie(
            counts, 
            names=dist_col, 
            values="Count", 
            hole=0.55,
            color_discrete_sequence=PIE_COLORS
        )
        fig_pie.update_traces(
            textposition='inside',
            textinfo='percent',
            insidetextorientation='radial'
        )

        # Legend 
        fig_pie.update_layout(
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=0.95,
                font=dict(size=10, color="#2D3748")
            ),
            margin=dict(l=10, r=40, t=30, b=20)
        )

        fig_pie = apply_card_style(fig_pie)
        st.plotly_chart(fig_pie, use_container_width=True)


# 2. COLUMN 2: Logs Over Time (Aligned Baseline) 
with c2:
    if ts_col:
        st.subheader("Logs Over Time")
        freq = st.selectbox("Group by", ["Day", "hour", "Week"], key="freq_select")
        rule = {"Day": "D", "hour": "h", "Week": "W"}[freq]
        trend = filtered_df.set_index(ts_col).resample(rule).size().reset_index(name="Count")
        
        fig_line = px.line(trend, x=ts_col, y="Count")
        fig_line.update_traces(
            line_color=LINE_COLOR, 
            fill="tozeroy", 
            fillcolor="rgba(255, 154, 0, 0.2)"
        )
        
        fig_line = apply_card_style(fig_line)
        fig_line.update_layout(height=305)
        st.plotly_chart(fig_line, use_container_width=True)


# 3. COLUMN 3: Request Methods 
with c3:
    if "Request Method" in filtered_df.columns:
        st.subheader("Request Methods")
        m = filtered_df["Request Method"].value_counts().reset_index()
        m.columns = ["Method", "Count"]
        
        fig_m = px.bar(
            m, 
            x="Method", 
            y="Count", 
            color="Method", 
            color_discrete_sequence=METHOD_COLORS
        )
        fig_m.update_layout(showlegend=False)
        fig_m = apply_card_style(fig_m)
        st.plotly_chart(fig_m, use_container_width=True)
# CHART ROW 2: top-N breakdown bars 
def top_n_bar(data, column, title, color, n=8):
    counts = data[column].value_counts().head(n).reset_index()
    counts.columns = [column, "Count"]
    fig = px.bar(counts, x="Count", y=column, orientation="h", color_discrete_sequence=[color])
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.subheader(title)
    st.plotly_chart(fig, use_container_width=True)


top_cols_map = {
    "Request Path": ("Top Paths", BAR_COLOR_1),
    "Client IP": ("Top Client IPs", BAR_COLOR_2),
    "Request Controller Action": ("Top Controllers", BAR_COLOR_3),
}
available_top_cols = [c for c in top_cols_map if c in filtered_df.columns]

if available_top_cols:
    grid = st.columns(len(available_top_cols) + (1 if "Total Duration (ms)" in filtered_df.columns else 0))
    for i, col in enumerate(available_top_cols):
        with grid[i]:
            title, color = top_cols_map[col]
            top_n_bar(filtered_df, col, title, color)

    if "Total Duration (ms)" in filtered_df.columns and "Request Path" in filtered_df.columns:
        with grid[-1]:
            slow = filtered_df.groupby("Request Path")["Total Duration (ms)"].mean()
            slow = slow.sort_values(ascending=False).head(8).reset_index()
            fig = px.bar(slow, x="Total Duration (ms)", y="Request Path", orientation="h",
                         color_discrete_sequence=[BAR_COLOR_4])
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.subheader("Top Slow Requests")
            st.plotly_chart(fig, use_container_width=True)


# TABLE + SEARCH + DOWNLOAD (works for any log type) 
st.subheader(f"{log_type} Logs")

search_term = st.text_input("Search in table...")
table_df = filtered_df.copy()
if search_term:
    mask = table_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
    table_df = table_df[mask]

st.dataframe(table_df, use_container_width=True, height=350)

csv_data = table_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", data=csv_data, file_name=f"{log_type.replace(' ', '_').lower()}.csv", mime="text/csv")

st.caption(f"Showing {len(table_df):,} of {len(df):,} entries")