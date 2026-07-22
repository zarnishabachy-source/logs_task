import re
import os
import csv

input_log_path = r"c:\Users\User\Downloads\server-logs"
output_all_lines_csv = r"c:\Users\User\Downloads\server-logs-all-lines.csv"

# Clean ANSI escape sequences
ansi_escape = re.compile(r'\x1b\[[0-9;]*[mK]')

# Regex patterns
started_pattern = re.compile(
    r'Started (GET|POST|PUT|PATCH|DELETE|HEAD) "([^"]+)" for ([\d\.]+) at ([\d\-:\s\+]+)'
)
processing_pattern = re.compile(r'Processing by ([\w:]+#\w+)(?: as (\w+))?')
completed_pattern = re.compile(
    r'Completed (\d+) ([ \w]+) in (\d+)ms(?: \((?:Views: ([\d\.]+)ms)?(?: \| )?(?:ActiveRecord: ([\d\.]+)ms)?.*?\))?'
)

req_id_pattern = re.compile(r'\[([a-f0-9\-]{36})\]')
log_prefix_pattern = re.compile(r'^([IDWEF]),\s+\[([\d\-T:\.]+)\s+#(\d+)\]\s+(\w+)\s+--\s+:\s+(.*)$')

# Match query label and duration e.g. "Company Load (0.3ms)  SELECT ..."
query_pattern = re.compile(r'^([\w\s\?:]+)\s+\(([\d\.]+)ms\)\s+(.*)$')

# Match rendered templates e.g. "Rendered shared/_navbar.html.haml (Duration: 4.0ms | Allocations: 801)"
rendered_pattern = re.compile(r'^Rendered\s+([\w\/\.\_\-\#\(\)\:\!\?\s]+)\s+\(Duration:\s+([\d\.]+)ms\s*\|\s*Allocations:\s+(\d+)\)')

sql_queries_pattern = re.compile(r'SQL Queries:\s+(\d+)')
allocations_pattern = re.compile(r'Allocations:\s+(\d+)')

def clean_ansi(text):
    return ansi_escape.sub('', text)

def split_all_lines():
    print(f"Reading {input_log_path}...")
    if not os.path.exists(input_log_path):
        print(f"Error: {input_log_path} not found.")
        return

    # Pass 1: Gather request metadata
    print("Pass 1: Harvesting request metadata (Method, Path, Controller)...")
    request_metadata = {} # req_id -> {method, path, controller}
    
    with open(input_log_path, 'r', encoding='utf-8', errors='ignore') as infile:
        for line in infile:
            line_cleaned = clean_ansi(line).strip()
            
            # Find request ID
            req_match = req_id_pattern.search(line_cleaned)
            if not req_match:
                continue
            req_id = req_match.group(1)
            
            if req_id not in request_metadata:
                request_metadata[req_id] = {'method': '', 'path': '', 'controller': ''}
                
            # Check started
            start_m = started_pattern.search(line_cleaned)
            if start_m:
                request_metadata[req_id]['method'] = start_m.group(1)
                request_metadata[req_id]['path'] = start_m.group(2)
                continue
                
            # Check processing
            proc_m = processing_pattern.search(line_cleaned)
            if proc_m:
                request_metadata[req_id]['controller'] = proc_m.group(1)
                
    print(f"Metadata collected for {len(request_metadata)} requests.")
    
    # Pass 2: Parse every line and write to CSV
    print(f"Pass 2: Writing all log lines to {output_all_lines_csv}...")
    
    fields = [
        'Line Number', 'Timestamp', 'Level', 'PID', 'Request ID', 
        'Request Method', 'Request Path', 'Request Controller Action',
        'Log Type', 'Query Category', 'Rendered Template', 
        'Duration (ms)', 'Allocations', 'SQL / Message Content'
    ]
    
    level_map = {
        'I': 'INFO',
        'D': 'DEBUG',
        'W': 'WARN',
        'E': 'ERROR',
        'F': 'FATAL'
    }
    
    with open(input_log_path, 'r', encoding='utf-8', errors='ignore') as infile, \
         open(output_all_lines_csv, 'w', newline='', encoding='utf-8') as outfile:
         
        writer = csv.writer(outfile)
        writer.writerow(fields)
        
        line_num = 0
        for line in infile:
            line_num += 1
            line_cleaned = clean_ansi(line).strip()
            
            # Parse prefix
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
                msg = prefix_match.group(5)
                
                req_match = req_id_pattern.match(msg)
                if req_match:
                    req_id = req_match.group(1)
                    content = msg[req_match.end():].strip()
                else:
                    content = msg.strip()
            else:
                req_match = req_id_pattern.search(line_cleaned)
                if req_match:
                    req_id = req_match.group(1)
                    content = line_cleaned.replace(f"[{req_id}]", "").strip()
            
            # Request metadata propagation
            req_method = ""
            req_path = ""
            req_controller = ""
            if req_id and req_id in request_metadata:
                req_method = request_metadata[req_id]['method']
                req_path = request_metadata[req_id]['path']
                req_controller = request_metadata[req_id]['controller']
                
            # Log Type classification and detailed column extraction
            log_type = "General"
            query_cat = ""
            rendered_temp = ""
            duration = ""
            allocations = ""
            
            # Check started
            if started_pattern.search(content):
                log_type = "Started Request"
            # Check processing
            elif processing_pattern.search(content):
                log_type = "Processing"
            # Check completed
            elif completed_pattern.search(content):
                log_type = "Completed Request"
                comp_m = completed_pattern.search(content)
                if comp_m:
                    duration = comp_m.group(3)
                alloc_m = allocations_pattern.search(content)
                if alloc_m:
                    allocations = alloc_m.group(1)
            # Check database query
            elif query_pattern.match(content):
                log_type = "Database Query"
                q_match = query_pattern.match(content)
                if q_match:
                    query_cat = q_match.group(1).strip()
                    duration = q_match.group(2)
                    content = q_match.group(3).strip()
            # Check rendered template
            elif rendered_pattern.match(content):
                log_type = "Render Template"
                r_match = rendered_pattern.match(content)
                if r_match:
                    rendered_temp = r_match.group(1).strip()
                    duration = r_match.group(2)
                    allocations = r_match.group(3)
            # Check errors
            elif level in ['ERROR', 'FATAL'] or "exception" in content.lower() or "error" in content.lower():
                log_type = "Error/Exception"
                
            # Write row
            writer.writerow([
                line_num,
                timestamp,
                level,
                pid,
                req_id,
                req_method,
                req_path,
                req_controller,
                log_type,
                query_cat,
                rendered_temp,
                duration,
                allocations,
                content
            ])
            
    print(f"Completed! Wrote {line_num} rows to {output_all_lines_csv}.")

if __name__ == "__main__":
    split_all_lines()
