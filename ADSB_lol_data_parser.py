# -*- coding: utf-8 -*-
"""
Probeersel om ADSB.lol data te verwerken

@author: Jens
"""

import numpy as np
import json

# Path to your ADS-B data file
file_path = 'Data/acas.json'


# Initialize an empty list to hold the ADS-B data
adsb_data = []

# Read and parse each line (JSON object) individually
with open(file_path, 'r') as file:
    for line in file:
        try:
            adsb_data.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

# Now adsb_data contains all the parsed JSON objects
print(f"Loaded {len(adsb_data)} ADS-B data records.")

# %%

# Define the bounding box around Schiphol
bbox_top_left = (52.392124353727276, 4.65390042931)
bbox_bottom_right = (52.2632215325, 4.84323226670213)


def is_within_bbox(lat, lon, bbox_tl, bbox_br):
    # Function to check if a plane is within the bounding box
    return bbox_tl[0] >= lat >= bbox_br[0] and bbox_tl[1] <= lon <= bbox_br[1]


def get_lat_lon(plane):
    # Modified function to handle both adsb_icao and mode_s data
    if plane['type'] in ['adsb_icao', 'mlat']:
        return plane.get('lat'), plane.get('lon')
    elif plane['type'] == 'mode_s':
        last_position = plane.get('lastPosition', {})
        return last_position.get('lat'), last_position.get('lon')
    return None, None  # Return None if neither type matches or lat/lon not found


# Filter the data for planes within the bounding box
filtered_planes = []
for plane in adsb_data:
    lat, lon = get_lat_lon(plane)
    if lat is not None and lon is not None and is_within_bbox(lat, lon, bbox_top_left, bbox_bottom_right):
        filtered_planes.append(plane)

# Output the result
print(f"Filtered {len(filtered_planes)} planes near Schiphol.")
