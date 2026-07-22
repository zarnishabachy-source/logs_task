import re
import os
import csv
from collections import defaultdict

input_log_path = r"c:\Users\User\Downloads\server-logs"
output_requests_csv = r"c:\Users\User\Downloads\server-logs-requests.csv"
output_lines_csv = r"c:\Users\User\Downloads\server-logs-lines.csv"

# Clean ANSI escape sequences
ansi_escape = re.compile(r'\x1b\[[0-9;]*[mK]')

# Regex patterns
# Started GET "/stocks/48950" for 172.69.242.130 at 2026-07-12 14:24:22 +0500
started_pattern = re.compile(
    r'Started (GET|POST|PUT|PATCH|DELETE|HEAD) "([^"]+)" for ([\d\.]+) at ([\d\-:\s\+]+)'
)
# Processing by StocksController#show as HTML
processing_pattern = re.compile(r'Processing by ([\w:]+#\w+)(?: as (\w+))?')
# Completed 200 OK in 39ms (Views: 20.9ms | ActiveRecord: 7.5ms | SQL Queries: 18 (2 cached) | Allocations: 14417)
completed_pattern = re.compile(
    r'Completed (\d+) ([ \w]+) in (\d+)ms(?: \((?:Views: ([\d\.]+)ms)?(?: \| )?(?:ActiveRecord: ([\d\.]+)ms)?.*?\))?'
)

req_id_pattern = re.compile(r'\[([a-f0-9\-]{36})\]')
log_prefix_pattern = re.compile(r'^([IDWEF]),\s+\[([\d\-T:\.]+)\s+#(\d+)\]\s+(\w+)\s+--\s+:\s+(.*)$')

def clean_ansi(text):
    return ansi_escape.sub('', text)

def split_logs():
    print(f"Reading {input_log_path}...")
    if not os.path.exists(input_log_path):
        print(f"Error: {input_log_path} not found.")
        return

    # To build requests CSV
    requests = {} # req_id -> dict
    
    # We will write the lines CSV incrementally to save memory
    print(f"Generating line-level CSV: {output_lines_csv}...")
    lines_written = 0
    
    # Levels dictionary
    level_map = {
        'I': 'INFO',
        'D': 'DEBUG',
        'W': 'WARN',
        'E': 'ERROR',
        'F': 'FATAL'
    }

    with open(input_log_path, 'r', encoding='utf-8', errors='ignore') as infile, \
         open(output_lines_csv, 'w', newline='', encoding='utf-8') as outlines_f:
         
        writer_lines = csv.writer(outlines_f)
        writer_lines.writerow(['Timestamp', 'Level', 'PID', 'Request ID', 'Content'])
        
        for line in infile:
            line_cleaned = clean_ansi(line).strip()
            
            # Parse line structure
            prefix_match = log_prefix_pattern.match(line_cleaned)
            
            level = ""
            timestamp = ""
            pid = ""
            req_id = ""
            content = line_cleaned
            
            if prefix_match:
                lvl_code = prefix_match.group(1)
                level = level_map.get(lvl_code, lvl_code)
                timestamp = prefix_match.group(2)
                pid = prefix_match.group(3)
                # group(4) is severity label e.g., INFO
                msg = prefix_match.group(5)
                
                # Check for request ID in message
                req_match = req_id_pattern.match(msg)
                if req_match:
                    req_id = req_match.group(1)
                    content = msg[req_match.end():].strip()
                else:
                    content = msg.strip()
            else:
                # If it doesn't match standard prefix, check for request ID anyway
                req_match = req_id_pattern.search(line_cleaned)
                if req_match:
                    req_id = req_match.group(1)
                    content = line_cleaned.replace(f"[{req_id}]", "").strip()
            
            # Write to lines CSV
            writer_lines.writerow([timestamp, level, pid, req_id, content])
            lines_written += 1
            
            # Track request details
            if req_id:
                if req_id not in requests:
                    requests[req_id] = {
                        'Request ID': req_id,
                        'Start Time': '',
                        'IP': '',
                        'Method': '',
                        'Path': '',
                        'Status': '',
                        'Status Msg': '',
                        'Duration (ms)': '',
                        'Views (ms)': '',
                        'DB (ms)': '',
                        'Controller Action': '',
                        'Errors': []
                    }
                
                req_info = requests[req_id]
                
                # Check started
                start_m = started_pattern.search(content)
                if start_m:
                    req_info['Method'] = start_m.group(1)
                    req_info['Path'] = start_m.group(2)
                    req_info['IP'] = start_m.group(3)
                    req_info['Start Time'] = start_m.group(4)
                
                # Check controller action
                proc_m = processing_pattern.search(content)
                if proc_m:
                    req_info['Controller Action'] = proc_m.group(1)
                
                # Check completed
                comp_m = completed_pattern.search(content)
                if comp_m:
                    req_info['Status'] = comp_m.group(1)
                    req_info['Status Msg'] = comp_m.group(2).strip()
                    req_info['Duration (ms)'] = comp_m.group(3)
                    if comp_m.group(4):
                        req_info['Views (ms)'] = comp_m.group(4)
                    if comp_m.group(5):
                        req_info['DB (ms)'] = comp_m.group(5)
                
                # Capture fatal/error details
                if level in ['ERROR', 'FATAL'] or 'Exception' in content or 'Error' in content:
                    req_info['Errors'].append(content)
                    
    print(f"Finished line-level CSV: {lines_written} lines written.")
    
    # Write requests CSV
    print(f"Generating request-level CSV: {output_requests_csv}...")
    with open(output_requests_csv, 'w', newline='', encoding='utf-8') as outreqs_f:
        fields = [
            'Request ID', 'Start Time', 'IP', 'Method', 'Path', 
            'Status', 'Status Msg', 'Duration (ms)', 'Views (ms)', 'DB (ms)', 
            'Controller Action', 'Errors'
        ]
        writer_reqs = csv.DictWriter(outreqs_f, fieldnames=fields)
        writer_reqs.writeheader()
        
        for req_id, info in requests.items():
            # Combine errors list into single string
            info['Errors'] = " | ".join(info['Errors']) if info['Errors'] else ""
            writer_reqs.writerow(info)
            
    print(f"Finished request-level CSV: {len(requests)} requests written.")

if __name__ == "__main__":
    split_logs()
