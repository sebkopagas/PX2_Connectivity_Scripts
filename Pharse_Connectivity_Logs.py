import re
import pandas as pd

# Function to extract all timestamps for each step
def extract_timestamps(log_file_path):
    # Define search terms for each step (as lists to handle multiple keywords per step)
    steps_keywords = {
        "Meter Wakes up": [r"DEEPSLEEP_RESET"],
        "Attaches to GSM Network": [r"resetModem", r"get network status"],
        "Opens Protocol (TCP or MQTT)": [r"Modem Connect to PPP Server", r"MQTT ACK"],
        "Authenticates to Server": [r"get_cacert"],
        "Check for Job / Commands": [r"handleIncomePublish.*jobs/get/accepted"],
        "Meter Finishes Executing Command": [r"AdjustCredit"],
        "Send Telemetry Data": [r"aws_Publish.*successed", r"meter-status"],
        "Disconnection from Server": [r"aws_Disconnect"],
        "Disconnection from GSM Network": [r"PPP state changed event 5"],
        "Deep Sleep": [r"into low power"]
    }

    # Reading the log file
    try:
        with open(log_file_path, 'r') as file:
            log_content = file.readlines()
    except FileNotFoundError:
        print(f"Error: The file '{log_file_path}' was not found. Please check the file path and try again.")
        return

    # Regex to capture timestamps in the format [HH:MM:SS.SSS]
    timestamp_pattern = re.compile(r"\[\d{2}:\d{2}:\d{2}\.\d{3}\]")

    # Dictionary to store the extracted timestamps (as lists to capture multiple matches per step)
    timestamps = {step: [] for step in steps_keywords}

    # Iterate through log file and find matching entries
    for line in log_content:
        timestamp_match = timestamp_pattern.search(line)
        if timestamp_match:
            timestamp = timestamp_match.group(0)
            for step, keywords in steps_keywords.items():
                # Check each keyword for the current step
                for keyword in keywords:
                    if re.search(keyword, line):
                        timestamps[step].append(timestamp)
                        break  # Move to the next step once a keyword is found

    return timestamps

# Prompt the user for the log file path
log_file_path = input("Please enter the full path to your log file: ")

# Extract timestamps and display the results
timestamps = extract_timestamps(log_file_path)

if timestamps:
    # Prepare DataFrame with multiple entries for each step (if applicable)
    data = [(step, timestamp) for step, ts_list in timestamps.items() for timestamp in ts_list]
    timestamps_df = pd.DataFrame(data, columns=['Event', 'Timestamp'])
    
    print("\nExtracted Timestamps:")
    print(timestamps_df)
    
    # Optionally save the results to a CSV file
    save_to_csv = input("\nDo you want to save the extracted timestamps to a CSV file? (yes/no): ").strip().lower()
    if save_to_csv == 'yes':
        output_file = input("Enter the full path and filename for the output CSV (e.g., /path/to/output.csv): ")
        timestamps_df.to_csv(output_file, index=False)
        print(f"Timestamps saved to {output_file}")
    else:
        print("Timestamps not saved.")
