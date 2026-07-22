import re
import os
import csv
from collections import defaultdict

input_log_path = r"c:\Users\User\Downloads\server-logs"
output_ultra_csv = r"c:\Users\User\Downloads\server-logs-requests-ultra.csv"

# Clean ANSI escape sequences
ansi_escape = re.compile(r'\x1b\[[0-9;]*[mK]')

# Regex patterns
# Started GET "/stocks/48950" ...
started_pattern = re.compile(
    r'Started (GET|POST|PUT|PATCH|DELETE|HEAD) "([^"]+)" for ([\d\.]+) at ([\d\-:\s\+]+)'
)
# Processing by StocksController#show as HTML
processing_pattern = re.compile(r'Processing by ([\w:]+#\w+)(?: as (\w+))?')
# Completed 200 OK in 39ms ...
completed_pattern = re.compile(
    r'Completed (\d+) ([ \w]+) in (\d+)ms(?: \((?:Views: ([\d\.]+)ms)?(?: \| )?(?:ActiveRecord: ([\d\.]+)ms)?.*?\))?'
)

req_id_pattern = re.compile(r'\[([a-f0-9\-]{36})\]')
log_prefix_pattern = re.compile(r'^([IDWEF]),\s+\[([\d\-T:\.]+)\s+#(\d+)\]\s+(\w+)\s+--\s+:\s+(.*)$')

# Match query label and duration e.g. "Company Load (0.3ms)  SELECT ..."
query_pattern = re.compile(r'^([\w\s\?:]+)\s+\(([\d\.]+)ms\)\s+(.*)$')

# Match rendered templates e.g. "Rendered shared/_navbar.html.haml (Duration: 4.0ms | Allocations: 801)"
rendered_pattern = re.compile(r'^Rendered\s+([\w\/\.\_\-\#\(\)\:\!\?\s]+)\s+\(Duration:\s+([\d\.]+)ms\s*\|\s*Allocations:\s+(\d+)\)')

# Completed metrics regexes
sql_queries_pattern = re.compile(r'SQL Queries:\s+(\d+)')
sql_cached_pattern = re.compile(r'(\d+)\s+cached')
allocations_pattern = re.compile(r'Allocations:\s+(\d+)')

def clean_ansi(text):
    return ansi_escape.sub('', text)

def split_logs_ultra():
    print(f"Reading {input_log_path}...")
    if not os.path.exists(input_log_path):
        print(f"Error: {input_log_path} not found.")
        return

    requests = {} # req_id -> dict
    all_query_categories = set()
    all_render_categories = set()
    
    # Process the log file
    with open(input_log_path, 'r', encoding='utf-8', errors='ignore') as infile:
        for line in infile:
            line_cleaned = clean_ansi(line).strip()
            
            # Parse line structure
            prefix_match = log_prefix_pattern.match(line_cleaned)
            
            level = ""
            req_id = ""
            content = line_cleaned
            
            if prefix_match:
                level = prefix_match.group(1)
                msg = prefix_match.group(5)
                
                # Check for request ID in message
                req_match = req_id_pattern.match(msg)
                if req_match:
                    req_id = req_match.group(1)
                    content = msg[req_match.end():].strip()
                else:
                    content = msg.strip()
            else:
                # If no prefix match, try finding request ID in raw line
                req_match = req_id_pattern.search(line_cleaned)
                if req_match:
                    req_id = req_match.group(1)
                    content = line_cleaned.replace(f"[{req_id}]", "").strip()
            
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
                        'Started Line': '',
                        'Completed Line': '',
                        'Total Allocations': '',
                        'SQL Query Count': '',
                        'SQL Query Cached': '',
                        'Errors': [],
                        'queries': defaultdict(float),  # category -> cumulative duration ms
                        'renderings': defaultdict(float) # template -> duration ms
                    }
                
                req_info = requests[req_id]
                
                # Check started
                start_m = started_pattern.search(content)
                if start_m:
                    req_info['Method'] = start_m.group(1)
                    req_info['Path'] = start_m.group(2)
                    req_info['IP'] = start_m.group(3)
                    req_info['Start Time'] = start_m.group(4)
                    req_info['Started Line'] = content
                
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
                    req_info['Completed Line'] = content
                    
                    if comp_m.group(4):
                        req_info['Views (ms)'] = comp_m.group(4)
                    if comp_m.group(5):
                        req_info['DB (ms)'] = comp_m.group(5)
                        
                    # Extract advanced metrics from completed line
                    sql_m = sql_queries_pattern.search(content)
                    if sql_m:
                        req_info['SQL Query Count'] = sql_m.group(1)
                    cached_m = sql_cached_pattern.search(content)
                    if cached_m:
                        req_info['SQL Query Cached'] = cached_m.group(1)
                    alloc_m = allocations_pattern.search(content)
                    if alloc_m:
                        req_info['Total Allocations'] = alloc_m.group(1)
                
                # Capture query details
                q_match = query_pattern.match(content)
                if q_match:
                    category = q_match.group(1).strip()
                    duration = float(q_match.group(2))
                    req_info['queries'][category] += duration
                    all_query_categories.add(category)
                    
                # Capture rendering details
                r_match = rendered_pattern.match(content)
                if r_match:
                    template_path = r_match.group(1).strip()
                    duration = float(r_match.group(2))
                    req_info['renderings'][template_path] += duration
                    all_render_categories.add(template_path)
                
                # Capture fatal/error details
                if level in ['E', 'F'] or 'Exception' in content or 'Error' in content:
                    req_info['Errors'].append(content)
                    
    print(f"Parsed {len(requests)} unique requests.")
    print(f"Discovered {len(all_query_categories)} query/load categories.")
    print(f"Discovered {len(all_render_categories)} rendering categories.")
    
    # Sort categories to keep headers neat
    sorted_queries = sorted(list(all_query_categories))
    # We prefix rendering categories with "Render: " to distinguish them
    sorted_renders = sorted(list(all_render_categories))
    render_headers = [f"Render: {r}" for r in sorted_renders]
    
    # Write output requests CSV with columns for queries and renderings
    print(f"Generating ultra request-level CSV: {output_ultra_csv}...")
    
    # Define CSV fields
    base_fields = [
        'Request ID', 'Start Time', 'IP', 'Method', 'Path', 
        'Status', 'Status Msg', 'Duration (ms)', 'Views (ms)', 'DB (ms)', 
        'Controller Action', 'Total Allocations', 'SQL Query Count', 'SQL Query Cached',
        'Started Line', 'Completed Line', 'Errors'
    ]
    all_fields = base_fields + sorted_queries + render_headers
    
    with open(output_ultra_csv, 'w', newline='', encoding='utf-8') as out_f:
        writer = csv.writer(out_f)
        writer.writerow(all_fields)
        
        for req_id, info in requests.items():
            row = [
                info['Request ID'],
                info['Start Time'],
                info['IP'],
                info['Method'],
                info['Path'],
                info['Status'],
                info['Status Msg'],
                info['Duration (ms)'],
                info['Views (ms)'],
                info['DB (ms)'],
                info['Controller Action'],
                info['Total Allocations'],
                info['SQL Query Count'],
                info['SQL Query Cached'],
                info['Started Line'],
                info['Completed Line'],
                " | ".join(info['Errors']) if info['Errors'] else ""
            ]
            
            # Add dynamic query durations
            for cat in sorted_queries:
                duration = info['queries'].get(cat, 0.0)
                row.append(f"{duration:.2f}" if duration > 0.0 else "")
                
            # Add dynamic rendering durations
            for r_cat in sorted_renders:
                duration = info['renderings'].get(r_cat, 0.0)
                row.append(f"{duration:.2f}" if duration > 0.0 else "")
                
            writer.writerow(row)
            
    print(f"Finished writing {output_ultra_csv}.")

if __name__ == "__main__":
    split_logs_ultra()
