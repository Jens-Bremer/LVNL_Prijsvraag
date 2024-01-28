# -*- coding: utf-8 -*-
"""
Big code to answer the question "What is the maximum number of take-offs and landings (added up) that Schiphol handled within one hour in 2023?"


Created on Sun Jan 28 15:55:41 2024

@author: Max & Jens
"""

import numpy as np
import pandas as pd
import json
from datetime import datetime
import requests

# %%

# Read the JSON data from the file
with open('flightaware_data.json', 'r') as file:  # Data from https://www.flightaware.com/ajax/ignoreuser/airport_stats.rvt?airport=EHAM
    data = json.load(file)

# Process the data
# Create a list of tuples in the form (date, total_flights)
flights_data = [
    (
        datetime.utcfromtimestamp(day['date']).strftime('%Y-%m-%d'),
        day['arrivals'] + day['departures'],
        day['arrivals'],
        day['departures']
    )
    for day in data['chart_data']
    if datetime.utcfromtimestamp(day['date']).year == 2023
]


# Sort the list by total_flights in descending order to find the busiest days
sorted_flights_data = sorted(flights_data, key=lambda x: x[1], reverse=True)

sorted_flights_data[:5]  # Display the top 5 busiest days


# Display the busiest day with total flights, arrivals, and departures separately
busiest_day = sorted_flights_data[0] if sorted_flights_data else None
busiest_day_info = {
    'date': busiest_day[0],
    'total_flights': busiest_day[1],
    'arrivals': busiest_day[2],
    'departures': busiest_day[3]
}

busiest_day_info
