# -*- coding: utf-8 -*-
"""
Probeersel om ADSB.lol data te verwerken

@author: Jens
"""

from collections import Counter
from datetime import datetime, timedelta
import json
import glob
import gzip
import sys
import random

# Define the bounding box around Schiphol
"""
52.392124353727276,4.84323226670213
52.392124353727276,4.65390042931
52.2632215325,4.65390042931
52.2632215325,4.84323226670213

"""

bbox_top_left = (52.392124353727276, 4.65390042931)
bbox_bottom_right = (52.2632215325, 4.84323226670213)


def is_within_bbox(lat, lon, bbox_tl, bbox_br):
    """Function to check if a point is within the bounding box."""
    return bbox_tl[0] >= lat >= bbox_br[0] and bbox_tl[1] <= lon <= bbox_br[1]


def filter_trace(trace):
    """Filter the trace to keep only points within the bounding box."""
    filtered_trace = [point for point in trace if is_within_bbox(point[1], point[2], bbox_top_left, bbox_bottom_right)]
    return filtered_trace


def filter_all_data(file_pattern, output_to_json=False):
    # Find all files matching the pattern
    files = list(glob.glob(file_pattern, recursive=True))
    total_files = len(files)

    # Select % of the files randomly for processing
    percentage_to_process = 1
    files_to_process = random.sample(files, int(total_files * percentage_to_process))

    # Initialize a list to hold filtered trace data
    filtered_traces = []

    # Process each selected file
    for i, file_path in enumerate(files_to_process, start=1):
        # Open, decompress, and read each JSON file
        with gzip.open(file_path, 'rt', encoding='utf-8') as file:
            try:
                data = json.load(file)
                # Filter the trace for points within the bounding box
                filtered_trace = filter_trace(data['trace'])
                if filtered_trace:
                    # Save only the filtered trace points
                    filtered_traces.append({'icao': data['icao'], 'registration': data.get('r', None), 'trace': filtered_trace})
            except json.JSONDecodeError as e:
                print(f"\nError decoding JSON in {file_path}: {e}", file=sys.stderr)
            except Exception as e:
                print(f"\nAn error occurred with file {file_path}: {e}", file=sys.stderr)

        # Print progress every 250 files
        if i % 250 == 0:
            print(f"\rProcessing file {i} of {len(files_to_process)}...", end='')
            sys.stdout.flush()

    print(f"\rProcessing file {i} of {len(files_to_process)}...", end='')
    print(f"\nFiltered {len(filtered_traces)} planes with points near Schiphol.")

    if output_to_json:
        # Save the filtered trace data to a JSON file
        output_file = 'filtered_traces_near_schiphol.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_traces, f, ensure_ascii=False, indent=4)

        print(f"Filtered trace data saved to {output_file}")

    return filtered_traces


# %%


def analyze_altitude_changes(filtered_traces):
    events = []  # List to hold departure and arrival events

    for trace in filtered_traces:
        previous_state = None  # Track the previous state (airborne or ground)
        for point in trace['trace']:
            timestamp, icao, _, altitude = point[0], trace['icao'], point[2], point[3]
            current_state = 'airborne' if isinstance(altitude, int) else 'ground'

            # Check for a state change (either from ground to airborne or vice versa)
            if previous_state and previous_state != current_state:
                event_type = 'departed' if current_state == 'airborne' else 'arrived'
                events.append({
                    'timestamp': timestamp,
                    'icao': icao,
                    'registration': trace.get('registration', None),
                    'event': event_type
                })

            previous_state = current_state

    return events


def print_total_movements(events):
    # Initialize counters for arrivals and departures
    arrivals_count = 0
    departures_count = 0

    # Loop through the events to count arrivals and departures
    for event in events:
        if event['event'] == 'arrived':
            arrivals_count += 1
        elif event['event'] == 'departed':
            departures_count += 1

    # Print the counts
    print(f"\nArrivals: {arrivals_count}")
    print(f"Departures: {departures_count}")
    print(f"Total movements: {arrivals_count + departures_count}\n")


# %%


def find_busiest_hour(events):
    # Convert timestamps to datetime objects and sort events
    for event in events:
        event['timestamp'] = datetime.fromtimestamp(event['timestamp'])
    events.sort(key=lambda x: x['timestamp'])

    # Initialize variables to track the busiest hour
    busiest_start_time = None
    busiest_count = 0
    arrivals_during_busiest = 0
    departures_during_busiest = 0

    # Use a moving window to count events in each hour-long period
    for i, event in enumerate(events):
        start_time = event['timestamp']
        end_time = start_time + timedelta(hours=1)
        window_events = [e for e in events if start_time <= e['timestamp'] < end_time]

        # Count arrivals and departures within the window
        event_counts = Counter(e['event'] for e in window_events)
        total_events = sum(event_counts.values())

        # Update the busiest hour if this window has more events
        if total_events > busiest_count:
            busiest_count = total_events
            busiest_start_time = start_time
            arrivals_during_busiest = event_counts['arrived']
            departures_during_busiest = event_counts['departed']

    return busiest_start_time, arrivals_during_busiest, departures_during_busiest, busiest_count

# %% Main


top_5 = ["2023.08.10", "2023.10.09", "2023.07.14", "2023.07.20", "2023.08.07"]
results = [["date", 'total movements', 'busiest hour', 'arrivals', 'departures']]

for date in top_5:
    # Pattern to match all relevant gzip-compressed JSON files in subdirectories
    file_pattern = f'Data/{date}/v{date}-planes-readsb-prod-0/traces/**/trace_full_*.json'
    filtered_traces = filter_all_data(file_pattern)
    events = analyze_altitude_changes(filtered_traces)
    print_total_movements(events)
    busiest_hour_start, arrivals, departures, total_events = find_busiest_hour(events)

    results.append([date, total_events, busiest_hour_start.strftime('%H:%M:%S'), arrivals, departures])
    # Print the results
    # print(f"Busiest hour starts at: {busiest_hour_start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Busiest hour starts at: {busiest_hour_start.strftime('%H:%M:%S')}")
    print(f"Arrivals during busiest hour: {arrivals}")
    print(f"Departures during busiest hour: {departures}")
    print(f"Total events during busiest hour: {total_events}")


# Save results to txt. since that is the best format to store data xD
filename = 'results.txt'

with open(filename, 'w') as file:
    for item in results:
        file.write(f"{item}\n")

print(f"Results have been written to {filename}")
