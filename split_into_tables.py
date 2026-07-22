import csv
import os

# The master CSV file containing all 3.3 lakh lines
input_csv = r"c:\Users\User\Downloads\server-logs-all-lines-detailed.csv"

# The folder where we want to save our new separated files
output_dir = r"C:\Users\User\Downloads\logs\input files"

def split_tables():
    print(f"Reading {input_csv}...")
    
    # Stop the script if the master file is missing
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} not found.")
        return

    # Dictionaries to keep track of our new files and CSV writers
    writers = {}
    files = {}
    row_counts = {}

    # Open the master CSV file to read it line by line
    with open(input_csv, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fields = reader.fieldnames # Get the column headers

        # Go through each row (log line) one by one
        for row in reader:
            # Check what type of log this is (e.g., 'Database Query' or 'Render Template')
            log_type = row.get('Log Type', 'Unknown')
            
            # Clean up the log type name so we can safely use it as a file name
            safe_name = "".join(c if c.isalnum() else "_" for c in log_type).strip("_")
            
            # If we haven't created a file for this log type yet, create it now!
            if log_type not in writers:
                out_path = os.path.join(output_dir, f"server-logs-table-{safe_name}.csv")
                
                # Open a new CSV file to write data into
                f = open(out_path, 'w', newline='', encoding='utf-8')
                files[log_type] = f
                
                # Create a CSV writer and write the column headers at the top
                writers[log_type] = csv.DictWriter(f, fieldnames=fields)
                writers[log_type].writeheader()
                row_counts[log_type] = 0
                
                print(f"Created table file: {out_path}")
            
            # Write this specific row into its correct category file
            writers[log_type].writerow(row)
            row_counts[log_type] += 1

    # Close all the files we opened to save them properly
    for f in files.values():
        f.close()
    
    # Print a nice summary of how many lines went into each file
    print("\nSplitting Summary:")
    for log_type, count in row_counts.items():
        print(f" - {log_type}: {count} rows")
    print("Done splitting into multiple tables based on Log Type.")

# This block runs the script when you execute it in terminal
if __name__ == "__main__":
    # Increase the CSV size limit in case some log messages are super long
    csv.field_size_limit(10000000)
    split_tables()
