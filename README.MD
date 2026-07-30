# 🚀 Log Analytics Dashboard & Data Pipeline

A high-performance Streamlit analytics dashboard and log-processing pipeline for exploring **338,000+ log lines**.

> [!IMPORTANT]
> **Data Migration Update**: All legacy CSV files in this project have been fully converted to **compressed JSON (`.json.gz`) format**.
> - **Total Data Size**: Reduced from **457.36 MB** to **40.95 MB** (**91% compression ratio**, < 50 MB limit).
> - **Data Loss**: **0%** (All 338,000+ log records, columns, and metadata are 100% intact).
> - **CSV Status**: All legacy `.csv` files have been removed from the repository.

---

## ✨ Features & Capabilities

- **Log Type Selector** — Instantly switch between 7 categorized log datasets (`Started Request`, `Database Query`, `Render Template`, `Error / Exception`, `General`, `Processing`, `Completed Request`).
- **Dynamic Search & Filtering** — Filter logs by date range, request method, HTTP response status, client IP, severity level, and controller action.
- **Real Company Mapping** — Automatically extracts real company subdomains from SQL database query parameters and maps client IPs to company names.
- **KPI Metrics** — Displays key performance metrics including total log volume, unique client IPs, unique request endpoints, average response time, and active server processes.
- **Interactive Visualizations** — Time-series activity, status code distribution, top request paths, client IP breakdowns, and slow-request rankings.
- **Ultra-Fast Performance** — Native compressed JSON (`.json.gz`) loading via Pandas speeds up dashboard load time while keeping memory footprint low.

---

## 📁 Project Architecture

```text
├── app.py                          # Streamlit analytics dashboard & UI
├── cleaning_data.py                # Preprocessing pipeline (loads input JSON.GZ & exports cleaned JSON.GZ)
├── split_all_lines.py              # Log line parser & splitter
├── split_into_tables.py            # Categorizes master log lines into structured table files
├── stats.css                       # Custom CSS styling for Streamlit UI
├── .streamlit/
│   └── config.toml                 # Streamlit theme configuration
├── input files/                    # Raw categorized log datasets (.json.gz format)
└── cleaned_files/                  # Processed & cleaned log datasets (.json.gz format)
```

---

## 📊 Dataset Specifications & Compression Summary

| Dataset File (`.json.gz`) | Category | Records | Original CSV Size | Compressed JSON Size | Data Integrity |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `server-logs-table-Error_Exception.json.gz` | Error & Exception Logs | 124,243 | 133.80 MB | **6.48 MB** | 100% Intact |
| `server-logs-table-Render_Template.json.gz` | Template Renderings | 125,344 | 53.54 MB | **3.40 MB** | 100% Intact |
| `server-logs-table-General.json.gz` | General Logs | 56,114 | 32.32 MB | **3.07 MB** | 100% Intact |
| `server-logs-table-Completed_Request.json.gz` | Completed Requests | 10,270 | 5.64 MB | **1.15 MB** | 100% Intact |
| `server-logs-table-Started_Request.json.gz` | Started Requests | 10,894 | 6.20 MB | **1.06 MB** | 100% Intact |
| `server-logs-table-Processing.json.gz` | Processing Logs | 10,271 | 5.02 MB | **0.93 MB** | 100% Intact |
| `server-logs-table-Database_Query.json.gz` | Database Queries | 1,270 | 0.27 MB | **0.04 MB** | 100% Intact |
| `server-logs-all-lines.json.gz` | Raw Master Log Lines | 338,406 | 119.72 MB | **11.83 MB** | 100% Intact |
| `server-logs-requests-ultra.json.gz` | Request Aggregations | 10,902 | 9.24 MB | **3.68 MB** | 100% Intact |
| **Total Workspace Data** | **All Categories** | **338,406+** | **457.36 MB** | **40.95 MB** | **0% Loss** |

---

## 🚀 Setup & Execution

### 1. Requirements
Ensure Python 3.8+ is installed along with the required libraries:

```bash
pip install streamlit pandas plotly
```

### 2. Running the Dashboard
Launch the Streamlit dashboard using:

```bash
streamlit run app.py
```

The application will launch in your browser at `http://localhost:8501`.

---

## ⚙️ Configuration & Data Loading

The `FILES` mapping in `app.py` directly loads compressed JSON datasets:

```python
DATA_FOLDER = Path("cleaned_files")

FILES = {
    "All Logs (Combined)": "ALL",
    "Started Request": DATA_FOLDER / "server-logs-table-Started_Request.json.gz",
    "Database Query": DATA_FOLDER / "server-logs-table-Database_Query.json.gz",
    "Render Template": DATA_FOLDER / "server-logs-table-Render_Template.json.gz",
    "Error / Exception": DATA_FOLDER / "server-logs-table-Error_Exception.json.gz",
    "General": DATA_FOLDER / "server-logs-table-General.json.gz",
    "Processing": DATA_FOLDER / "server-logs-table-Processing.json.gz",
    "Completed Request": DATA_FOLDER / "server-logs-table-Completed_Request.json.gz",
}
```