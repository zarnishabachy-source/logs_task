import re
import os

input_log_path = r"c:\Users\User\Downloads\server-logs"
req_id_pattern = re.compile(r'\[([a-f0-9\-]{36})\]')

def scan_unmatched():
    if not os.path.exists(input_log_path):
        print("Log file not found.")
        return
        
    unmatched_samples = []
    total_unmatched = 0
    total_lines = 0
    
    with open(input_log_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            total_lines += 1
            if not req_id_pattern.search(line):
                total_unmatched += 1
                if len(unmatched_samples) < 100:
                    unmatched_samples.append(line.strip())
                    
    print(f"Total lines: {total_lines}")
    print(f"Total unmatched lines (no request ID): {total_unmatched}")
    print("\nFirst 100 unmatched lines:")
    for idx, line in enumerate(unmatched_samples, 1):
        print(f"{idx}: {line}")

if __name__ == "__main__":
    scan_unmatched()
