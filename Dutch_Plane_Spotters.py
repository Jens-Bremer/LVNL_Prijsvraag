import pandas as pd
from datetime import datetime, time
import numpy as np
import requests
from bs4 import BeautifulSoup

arrival_url = "https://schiphol.dutchplanespotters.nl/?date=2023-11-01"
arrival_table = pd.read_html(arrival_url)
departure_url = "https://schiphol.dutchplanespotters.nl/departures.php?date=2023-10-05"
departure_table = pd.read_html(departure_url)


timevalues_arrival = arrival_table[0]['Arrival']['ETA']
flightnums_arrival = arrival_table[0]['Arrival']['FLIGHTNR']
timevalues_departure = departure_table[0]['ETD']
flightnums_departure = departure_table[0]['FLIGHTNR']

flightdata = []
for i in range(len(timevalues_arrival)):
    if arrival_table[0]['Arrival']['Status'][i] != 'Cancelled':
        flightdata.append([datetime.strptime(timevalues_arrival[i], "%H:%M").time(), flightnums_arrival[i], 'Arrival'])

for i in range(len(timevalues_departure)):
    if departure_table[0]['Status'][i] != 'Cancelled':
        flightdata.append([datetime.strptime(timevalues_departure[i], "%H:%M").time(), flightnums_departure[i], 'Departure'])

flightdata=sorted(flightdata)
flightdata=np.array(flightdata)
movement_dict = {}

for hr in range(0,24):
    for min in range(0, 60):
        current_time = time(hour=hr, minute=min)
        end_time = time(hour=(hr+1)%24, minute=min)
        movements = len([True for tijd in flightdata[:,0] if tijd >= current_time and tijd < end_time])
        movement_dict[f'{hr}:{min}'] = movements

max_key = max(movement_dict, key=movement_dict.get)
print(f"{movement_dict[max_key]} movements in the hour starting at {max_key}")

