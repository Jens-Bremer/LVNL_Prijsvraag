import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, time, timedelta
import numpy as np


def find_movements(date: str, interval: int):  # Date in yyyy-mm-dd, interval in minutes
    arrival_url = "https://schiphol.dutchplanespotters.nl/?date="+date
    arrival_table = pd.read_html(arrival_url)
    departure_url = "https://schiphol.dutchplanespotters.nl/departures.php?date="+date
    departure_table = pd.read_html(departure_url)

    timevalues_arrival = arrival_table[0]['Arrival']['ETA']
    flightnums_arrival = arrival_table[0]['Arrival']['FLIGHTNR']
    status_arrival = arrival_table[0]['Arrival']['Status']

    timevalues_departure = departure_table[0]['ETD']
    flightnums_departure = departure_table[0]['FLIGHTNR']
    status_departure = departure_table[0]['Status']
    del arrival_table
    del departure_table

    flightdata = []
    for i in range(len(timevalues_arrival)):
        if status_arrival[i] != 'Cancelled':
            flightdata.append([datetime.strptime(timevalues_arrival[i], "%H:%M").time(), flightnums_arrival[i], 'Arrival'])

    for i in range(len(timevalues_departure)):
        if status_departure[i] != 'Cancelled':
            flightdata.append([datetime.strptime(timevalues_departure[i], "%H:%M").time(), flightnums_departure[i], 'Departure'])

    # flightdata=sorted(flightdata) To improve runtime, this is smarter
    flightdata=np.array(flightdata)
    movement_dict = {}

    for hr in range(0, 24):
        for min in range(0, 60, interval):
            current_time = time(hour=hr, minute=min)
            end_time = time(hour=(hr+1) % 24, minute=min)
            movements = len([True for tijd in flightdata[:, 0] if current_time <= tijd < end_time])
            movement_dict[f'{hr}:{min}'] = movements

    max_key = max(movement_dict, key=movement_dict.get)
    # print(f"{movement_dict[max_key]} movements in the hour starting at {max_key}")
    return {'Movement_amount': movement_dict[max_key],
            'Time': datetime.strptime(max_key, "%H:%M").time().strftime("%H:%M")
            }
    # End of definition


start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)

# Create a list of strings for all dates in 2023
date_strings = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days + 1)]
month_string = [(start_date + timedelta(days=10*i)).strftime('%Y-%m-%d') for i in range(36)]

year_dict = {}

for day in date_strings:
    result = find_movements(day, 1)
    year_dict[f'{day} {result["Time"]}'] = result['Movement_amount']
    if day in month_string:
        max_day = max(year_dict, key=year_dict.get)
        print(f'Now at {day}, incumbent is {year_dict[max_day]} at {max_day}')

max_day = max(year_dict, key=year_dict.get)
print(f'Maximum amount of movements was {year_dict[max_day]} and this occurred in an hour starting at {max_day}')

plt.plot(list(range(len(year_dict))),[year_dict[key] for key in list(year_dict.keys())])
plt.show()
