import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input files")
CLEANED_DIR = os.path.join(BASE_DIR, "cleaned_files")
os.makedirs(CLEANED_DIR, exist_ok=True)

# loading datasets from compressed JSON
df1 = pd.read_json(os.path.join(INPUT_DIR, "server-logs-table-Database_Query.json.gz"))
df2 = pd.read_json(os.path.join(INPUT_DIR, "server-logs-table-Error_Exception.json.gz"))
df3 = pd.read_json(os.path.join(INPUT_DIR, "server-logs-table-General.json.gz"))
df4 = pd.read_json(os.path.join(INPUT_DIR, "server-logs-table-Processing.json.gz"))
df5 = pd.read_json(os.path.join(INPUT_DIR, "server-logs-table-Render_Template.json.gz"))
df6 = pd.read_json(os.path.join(INPUT_DIR, "server-logs-table-Started_Request.json.gz"))
df7 = pd.read_json(os.path.join(INPUT_DIR, "server-logs-table-Completed_Request.json.gz"))

print("Data is loaded from compressed JSON files.")
# reading shape of datasets
print(df1.shape)
print(df2.shape)
print(df3.shape)
print(df4.shape)
print(df5.shape)
print(df6.shape)
print(df7.shape)

# remove query data, rendered, line duration (ms), line allocation columns from server logs table started request
drop_cols_common = ['Query Category', 'Rendered Template', 'Line Duration (ms)', 'Line Allocations']
df6 = df6.drop([c for c in drop_cols_common if c in df6.columns], axis=1)

# remove query category column from server logs table render template
if 'Query Category' in df5.columns:
    df5 = df5.drop(['Query Category'], axis=1)

# remove query data, rendered, line duration (ms), line allocation columns from processing & general
df4 = df4.drop([c for c in drop_cols_common if c in df4.columns], axis=1)
df3 = df3.drop([c for c in drop_cols_common if c in df3.columns], axis=1)

# remove total views time(ms), query data, rendered, line duration (ms), line allocation columns from error exception
drop_cols_err = ['Total Views Time (ms)', 'Query Category', 'Rendered Template', 'Line Duration (ms)', 'Line Allocations']
df2 = df2.drop([c for c in drop_cols_err if c in df2.columns], axis=1)

# remove rendered template and line allocation from db query
drop_cols_db = ['Rendered Template', 'Line Allocations']
df1 = df1.drop([c for c in drop_cols_db if c in df1.columns], axis=1)

# remove query category and render template from completed request
drop_cols_comp = ['Query Category', 'Rendered Template']
df7 = df7.drop([c for c in drop_cols_comp if c in df7.columns], axis=1)

# replace null values with NULL
df7 = df7.fillna('NULL')
df3 = df3.fillna('NULL')
df4 = df4.fillna('NULL')
df6 = df6.fillna('NULL')
df1 = df1.fillna('NULL')
df2 = df2.fillna('NULL')
df5 = df5.fillna('NULL')

# save files to cleaned_files folder as compressed JSON (.json.gz)
df6.to_json(os.path.join(CLEANED_DIR, "server-logs-table-Started_Request.json.gz"), orient="records", compression="gzip")
df5.to_json(os.path.join(CLEANED_DIR, "server-logs-table-Render_Template.json.gz"), orient="records", compression="gzip")
df4.to_json(os.path.join(CLEANED_DIR, "server-logs-table-Processing.json.gz"), orient="records", compression="gzip")
df3.to_json(os.path.join(CLEANED_DIR, "server-logs-table-General.json.gz"), orient="records", compression="gzip")
df2.to_json(os.path.join(CLEANED_DIR, "server-logs-table-Error_Exception.json.gz"), orient="records", compression="gzip")
df1.to_json(os.path.join(CLEANED_DIR, "server-logs-table-Database_Query.json.gz"), orient="records", compression="gzip")
df7.to_json(os.path.join(CLEANED_DIR, "server-logs-table-Completed_Request.json.gz"), orient="records", compression="gzip")

print("Cleaned datasets saved as compressed JSON files.")