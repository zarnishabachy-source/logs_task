import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
input_file = r"c:\Users\User\Downloads\server-logs-all-lines-detailed.csv"
output_dir = os.path.join(BASE_DIR, "input files")
os.makedirs(output_dir, exist_ok=True)

def split_tables():
    print(f"Reading {input_file}...")
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    df = pd.read_csv(input_file, low_memory=False)
    if 'Log Type' not in df.columns:
        print("Log Type column missing.")
        return

    grouped = df.groupby('Log Type')
    for log_type, group in grouped:
        safe_name = "".join(c if c.isalnum() else "_" for c in str(log_type)).strip("_")
        out_path = os.path.join(output_dir, f"server-logs-table-{safe_name}.json.gz")
        group.to_json(out_path, orient="records", compression="gzip")
        print(f"Created compressed JSON table: {out_path} ({len(group)} rows)")

if __name__ == "__main__":
    split_tables()
