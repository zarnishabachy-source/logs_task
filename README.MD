# Log Analytics Dashboard

A polished Streamlit dashboard for exploring 300,000+ log rows across multiple CSV files with interactive filters, KPI summaries, visual charts, and a searchable table.

## ✨ What this project does

This app helps you quickly inspect server logs by:
- switching between log types from a sidebar selector
- filtering data by time, method, status, IP, level, and controller
- viewing summary KPIs such as total logs, unique IPs, unique requests, average duration, and unique processes
- exploring trends and distributions through charts
- searching and downloading the underlying data

## 🔧 Features

- **Log type switcher** — load a different CSV file based on the selected log type
- **Dynamic filters** — date range, request method, response status, client IP, level, and controller
- **KPI cards** — instant insights for the current dataset
- **Interactive charts** — status/level breakdowns, time trends, request method bars, top paths, top IPs, top controllers, and slow requests
- **Data table** — search, inspect, and export rows as CSV
- **Refresh control** — clear cached data and reload fresh results from disk
- **Fast loading** — cached data access keeps large files responsive

## 📁 Project structure

```text
├── app.py                          # main Streamlit dashboard
├── cleaning_data.py                # cleans and preprocesses raw log data
├── extract_companies.py            # extracts company-related information from logs
├── split_all_lines.py              # splits raw log files into individual lines
├── split_into_tables.py            # structures log lines into table-ready rows
├── split_logs.py                   # splits logs by log type
├── split_logs_ultra.requests.py   # optimized/faster log splitting
├── unmatched_scanner.py            # finds unmatched or unparsed log lines
├── stats.css                       # custom dashboard styling
├── .streamlit/
│   └── config.toml                 # Streamlit theme and server settings
├── input files/                    # original/raw input files
├── cleaned_files/                  # processed output files
└── README.md
```

> This README assumes the dashboard entry point is app.py. If your file is still named dashboard.py, rename it or update the run command below.

## 🚀 Setup

Install the required Python packages:

```bash
pip install streamlit pandas plotly
```

## ▶️ Run the app

```bash
streamlit run app.py
```

The app will open at http://localhost:8501.

## ⚙️ Configuration

Edit the FILES dictionary in app.py so it points to your actual CSV paths inside cleaned_files or another folder:

```python
FILES = {
    "Started Request": "started_request.csv",
    "Error / Exception": "error_exception.csv",
    "Database Query": "database_query.csv",
    "Rendered Template": "rendered_template.csv",
    "Completed": "completed.csv",
    "General": "general.csv",
    "Processing": "processing.csv"
}
```

## 📊 Expected columns

The dashboard uses the following columns when they are available:

| Column | Used for |
|---|---|
| any column containing "time" or "timestamp" | date filtering and time-series charts |
| Request Method | method filter and request method chart |
| Response Status / Level | status filter and distribution charts |
| Client IP | IP filter, unique IP KPI, and top-IP chart |
| Request Path | unique requests KPI, top paths, and slow request analysis |
| Request Controller Action | controller filter and top-controller chart |
| Total Duration (ms) | average duration KPI and slow request ranking |
| PID | unique processes KPI |

If a column is missing, the related chart, filter, or KPI will simply be skipped gracefully.

## 🎨 Customization

- Chart colors: update PIE_COLORS, LINE_COLOR, METHOD_COLORS, and BAR_COLOR_1-4 near the top of app.py
- Visual styling: adjust style_chart() or edit stats.css
- Table size: change the top-N row count used in the breakdown charts via the n parameter in top_n_bar()