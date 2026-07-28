"""
Multi Log Type Analytics Dashboard
Run: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="🚀 Log Analytics Dashboard", layout="wide")

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
    "All Logs (Combined)": "ALL",
    "Started Request": DATA_FOLDER / "server-logs-table-Started_Request.csv",
    "Database Query": DATA_FOLDER / "server-logs-table-Error_Exception.csv",
    "Render Template": DATA_FOLDER / "server-logs-table-Render_Template.csv",
    "Error / Exception": DATA_FOLDER / "server-logs-table-Database_Query.csv",
    "General": DATA_FOLDER / "server-logs-table-General.csv",
    "Processing": DATA_FOLDER / "server-logs-table-Processing.csv",
    "Completed Request": DATA_FOLDER / "server-logs-table-Completed_Request.csv",
}

# ============================================================
# BUILD REAL COMPANY MAPPING FROM DATABASE QUERY SQL
# Database Query logs have SQL like:
#   SELECT * FROM companies WHERE subdomain=$1 [["subdomain", "alimran6512"]]
# We extract the subdomain value and link it to each Client IP.
# This gives us 19 real company names used across ALL log types.
# ============================================================
import re as _re

def _build_company_mapping():
    """Read the Database Query CSV and extract IP -> real company name mapping."""
    # NOTE: Database Query data is in Error_Exception.csv (files were swapped at creation time)
    db_file = DATA_FOLDER / "server-logs-table-Error_Exception.csv"
    mapping = {}
    if db_file.exists():
        db_df = pd.read_csv(db_file, usecols=["Client IP", "SQL / Message Content"])
        pattern = r'\["subdomain",\s*"([^"]+)"\]'
        db_df["Company"] = db_df["SQL / Message Content"].astype(str).str.extract(pattern)
        db_df = db_df[db_df["Company"].notna()]
        # One IP maps to one company — use the first match
        for _, row in db_df.drop_duplicates("Client IP").iterrows():
            mapping[row["Client IP"]] = row["Company"].strip()
    return mapping

# Build company mapping once at startup — reused for all log types
_IP_COMPANY_MAP = _build_company_mapping()

# LOAD DATA FUNCTION
@st.cache_data
def load_data(path_key):
    if path_key == "ALL":
        # Combine all 7 log files into one big DataFrame
        dfs = []
        for key, path in FILES.items():
            if key != "All Logs (Combined)" and path.exists():
                temp_df = pd.read_csv(path)
                temp_df["Log Source"] = key
                dfs.append(temp_df)
        df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    else:
        df = pd.read_csv(path_key)

    # Convert any timestamp column to proper datetime format
    for col in df.columns:
        if "time" in col.lower() or "timestamp" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Attach real company names using the IP->company mapping built from DB Query SQL
    # IPs with no match get labeled as "Unknown"
    if "Client IP" in df.columns:
        df["Company"] = df["Client IP"].map(_IP_COMPANY_MAP).fillna("Unknown")
    return df


# SIDEBAR: LOG TYPE NAVIGATION 
st.sidebar.title("🚀 LOG ANALYTICS")
log_type = st.sidebar.radio("Log Types", list(FILES.keys()), index=1)

df = load_data(FILES[log_type])

# find the timestamp column automatically (each file may name it differently)
ts_col = next((c for c in df.columns if "time" in c.lower()), None)


# SIDEBAR: DYNAMIC FILTERS
st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

filters = {}  # column -> selected values

if ts_col:
    min_d, max_d = df[ts_col].min(), df[ts_col].max()
    date_range = st.sidebar.date_input("Date Range", value=(min_d.date(), max_d.date()))
else:
    date_range = None

# common optional filter columns across log types
for col in ["Company", "Request Method", "Response Status", "Client IP", "Level",
            "Request Controller Action", "Request Path"]:
    if col in df.columns:
        # Using multiselect automatically adds a search bar in Streamlit
        filters[col] = st.sidebar.multiselect(f"{col} (Searchable)", sorted(df[col].dropna().unique()), help=f"Type to search for {col} options")

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

# Function ko global scope me define kar lein taake sab charts me chale
def apply_card_style(fig):
    fig.update_layout(
        height=420,  # Increased height so charts don't look squished
        paper_bgcolor="#FFFFFF",   # Card container white
        plot_bgcolor="#FFFFFF",    # Plot background white
        font=dict(color="#2D3748", family="Arial, sans-serif", size=12), # Slightly larger font for readability
        xaxis=dict(showgrid=True, gridcolor="#E2E8F0", tickfont=dict(color="#2D3748"), title=""),
        yaxis=dict(showgrid=True, gridcolor="#E2E8F0", tickfont=dict(color="#2D3748"), title=""),
        margin=dict(l=40, r=40, t=60, b=40), # Increased margins to let the chart breathe
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

st.markdown("---")
st.subheader("📊 Advanced Visual Analytics")

valid_charts = []

# 1. Traffic Trend
if ts_col:
    trend = filtered_df.set_index(ts_col).resample("h").size().reset_index()
    trend.columns = [ts_col, "Count"]
    fig1 = px.line(trend, x=ts_col, y="Count", color_discrete_sequence=["#0F2C59"], markers=True)
    valid_charts.append(("Traffic Trend (Line)", fig1))

# 2. Cumulative Area
if ts_col:
    trend['Cumulative'] = trend['Count'].cumsum()
    fig2 = px.area(trend, x=ts_col, y="Cumulative", color_discrete_sequence=["#FF9A00"])
    valid_charts.append(("Cumulative Load (Area)", fig2))

# 3. Donut
cat_col = next((c for c in ["Response Status", "Level", "Request Method"] if c in filtered_df.columns), None)
if cat_col:
    counts = filtered_df[cat_col].value_counts().reset_index()
    counts.columns = [cat_col, "Count"]
    fig3 = px.pie(counts, names=cat_col, values="Count", hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig3.update_traces(textinfo='percent', textposition='inside')
    # Place legend vertically on the right side of the donut chart
    fig3.update_layout(
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(size=11, color="#2D3748")
        )
    )
    valid_charts.append((f"{cat_col} Distribution (Donut)", fig3))

# 4. Top Endpoints
path_col = next((c for c in ["Request Controller Action", "Request Path", "Query Category"] if c in filtered_df.columns), None)
if path_col:
    c_path = filtered_df[path_col].value_counts().head(5).reset_index()
    c_path.columns = [path_col, "Count"]
    c_path["Full Path"] = c_path[path_col]
    # Truncate label so it doesn't squish the chart
    c_path[path_col] = c_path[path_col].apply(lambda x: (str(x)[:25] + '..') if len(str(x)) > 25 else x)
    
    fig4 = px.bar(c_path, x=path_col, y="Count", color_discrete_sequence=["#1A365D"], hover_data=["Full Path"])
    valid_charts.append((f"Top {path_col} (Bar)", fig4))

# 5. Top IPs
if "Client IP" in filtered_df.columns:
    c_ip = filtered_df["Client IP"].value_counts().head(5).reset_index()
    c_ip.columns = ["Client IP", "Count"]
    fig5 = px.bar(c_ip, x="Count", y="Client IP", orientation="h", color_discrete_sequence=["#E83E8C"])
    fig5.update_layout(yaxis={"categoryorder": "total ascending"})
    valid_charts.append(("Top Client IPs (H-Bar)", fig5))

# 6. Latency Hist
dur_col = next((c for c in ["Total Duration (ms)", "Line Duration (ms)"] if c in filtered_df.columns), None)
if dur_col:
    p99 = filtered_df[dur_col].quantile(0.99)
    fig6 = px.histogram(filtered_df[filtered_df[dur_col] < p99], x=dur_col, nbins=20, color_discrete_sequence=["#38B2AC"])
    valid_charts.append(("Latency Dist (Hist)", fig6))

# 7. Box Plot
if dur_col and path_col:
    top_p = filtered_df[path_col].value_counts().head(5).index
    fig7 = px.box(filtered_df[filtered_df[path_col].isin(top_p)], x=path_col, y=dur_col, color=path_col, color_discrete_sequence=px.colors.qualitative.Set3)
    valid_charts.append(("Latency (Box Plot)", fig7))

# 8. Treemap
if cat_col and path_col:
    tree_df = filtered_df.groupby([cat_col, path_col]).size().reset_index(name='Count').sort_values('Count', ascending=False).head(20)
    fig8 = px.treemap(tree_df, path=[cat_col, path_col], values='Count', color='Count', color_continuous_scale="Viridis")
    fig8.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    valid_charts.append(("Hierarchical (Treemap)", fig8))

# 9. Heatmap
if ts_col:
    df_heat = filtered_df.copy()
    df_heat['Day'] = df_heat[ts_col].dt.day_name()
    df_heat['Hour'] = df_heat[ts_col].dt.hour
    h_data = df_heat.groupby(['Day', 'Hour']).size().unstack(fill_value=0)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    h_data = h_data.reindex([d for d in days if d in h_data.index]).dropna(how='all')
    fig9 = px.imshow(h_data, aspect="auto", color_continuous_scale="Plasma")
    valid_charts.append(("Traffic Heatmap", fig9))

# 10. Correlation / Funnel
if "Total DB Time (ms)" in filtered_df.columns and "Total Duration (ms)" in filtered_df.columns:
    fig10 = px.scatter(filtered_df, x="Total DB Time (ms)", y="Total Duration (ms)", opacity=0.5, color_discrete_sequence=["#D53F8C"])
    valid_charts.append(("Correlation Analysis", fig10))
elif path_col:
    c_fun = filtered_df[path_col].value_counts().head(5).reset_index()
    c_fun.columns = [path_col, "Count"]
    c_fun["Full Path"] = c_fun[path_col]
    # Truncate label to give maximum space to the graph
    c_fun[path_col] = c_fun[path_col].apply(lambda x: (str(x)[:25] + '..') if len(str(x)) > 25 else x)
    
    fig10 = px.funnel(c_fun, x="Count", y=path_col, color_discrete_sequence=["#9F7AEA"], hover_data=["Full Path"])
    valid_charts.append(("Funnel Analysis", fig10))

# --- DISPLAY CHARTS DYNAMICALLY IN ROWS OF 2 ---
for i in range(0, len(valid_charts), 2):
    cols = st.columns(2)
    chunk = valid_charts[i:i+2]
    for col, (title, fig) in zip(cols, chunk):
        with col:
            st.markdown(f"**{title}**")
            st.plotly_chart(apply_card_style(fig), use_container_width=True)

# TABLE + SEARCH + DOWNLOAD (works for any log type) 
st.subheader(f"{log_type} Logs")

search_term = st.text_input("Search in table...")
table_df = filtered_df.copy()
if search_term:
    mask = table_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
    table_df = table_df[mask]

# Limit the dataframe size for the UI to prevent MessageSizeError (200MB limit in Streamlit)
if len(table_df) > 1000:
    st.warning(f"⚠️ Showing first 1000 rows out of {len(table_df):,} to prevent browser overload. Use filters to narrow down.")
    st.dataframe(table_df.head(1000), use_container_width=True, height=350)
else:
    st.dataframe(table_df, use_container_width=True, height=350)

csv_data = table_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", data=csv_data, file_name=f"{log_type.replace(' ', '_').lower()}.csv", mime="text/csv")

st.caption(f"Showing {len(table_df):,} of {len(df):,} entries")