# Log Analytics Dashboard

A Streamlit dashboard to explore 300,000+ log rows split across 7 log-type CSV files, with filters, KPIs, charts, and a searchable/downloadable table.

## Features
- **Log type switcher** (sidebar radio) — loads a different CSV per log type
- **Dynamic filters** — Date Range, Request Method, Response Status, Client IP, Level, Controller (only shown if that column exists in the selected file)
- **KPI cards** — Total Logs, Unique IPs, Unique Requests, Avg. Duration, Unique Processes
- **Charts** — Response Status/Level donut, Logs Over Time line (Day/Hour/Week), Request Methods bar, Top Paths, Top Client IPs, Top Controllers, Top Slow Requests
- **Table** — search box, full data table, CSV download
- **Refresh button** — clears cache and reloads CSVs fresh from disk
- Cached data loading (`st.cache_data`) so 3L+ row files stay fast

## Project Structure
```
├── app.py                  # main Streamlit dashboard (rename of dashboard.py)
├── cleaning_data.py         # cleans/preprocesses raw logs
├── split_all_lines.py       # splits raw log file into individual lines
├── split_into_tables.py     # splits lines into structured tables
├── split_logs.py            # splits logs by log type
├── split_logs_ultra.py      # optimized/faster log splitting
├── unmatched_scanner.py     # finds log lines that didn't match any parser
├── stats.css                # custom CSS for dashboard styling
├── .streamlit/
│   └── config.toml          # Streamlit theme/server config
├── input files/              # raw/original log files go here
├── cleaned_files/            # output of cleaning_data.py
└── README.md
```

> Note: this README assumes the dashboard file is `app.py`. If your file is still named `dashboard.py`, either rename it or update the run command below.


## Setup
```bash
pip install streamlit pandas plotly
```

## Run
```bash
streamlit run app.py
```
App opens at `http://localhost:8501`.

## Configuration
Edit the `FILES` dict in `app.py` to point to your actual CSV paths (e.g. inside `cleaned_files/`):
```python
FILES = {
    "Started Request": "started_request.csv",
    "Error / Exception": "error_exception.csv",
    "Database Query": "database_query.csv",
    "Rendered Template": "rendered_template.csv",
    "Completed": "completed.csv",
    "General":"general.csv",
    "Processing":"processing.csv"
}
```

### Expected columns (used if present)
| Column | Used for |
|---|---|
| any column with "time"/"timestamp" in its name | Date filter, time-series trend chart |
| `Request Method` | Method filter, Request Methods bar |
| `Response Status` / `Level` | Status filter, distribution donut |
| `Client IP` | IP filter, Unique IPs KPI, Top Client IPs |
| `Request Path` | Unique Requests KPI, Top Paths, Top Slow Requests |
| `Request Controller Action` | Controller filter, Top Controllers |
| `Total Duration (ms)` | Avg. Duration KPI, Top Slow Requests |
| `PID` | Unique Processes KPI |

Missing columns are handled gracefully — that chart/filter/KPI simply won't render for files that don't have it.

## Customization
- Chart colors: edit `PIE_COLORS`, `LINE_COLOR`, `METHOD_COLORS`, `BAR_COLOR_1-4` at the top of `app.py`
- Dark theme styling: `style_chart()` function, or `stats.css`
- Top-N rows shown in breakdown bars: `n` parameter in `top_n_bar()`