# -*- coding: utf-8 -*-
"""
Code to scrape flightera.net and calculate maximum movements per hour

Created on Sun Jan 28 21:54:06 2024

@author: Jens
"""

import numpy as np
import pandas as pd
import requests
import datetime
from fake_http_header import FakeHttpHeader

# %% Request html


def generate_url(date, time, type='departure'):
    """
    Generates a URL for a specific date and time for either departure or arrival data.

    :param date: datetime.date, the date for which to generate the URL
    :param time: str, the time in 'HH:MM' format
    :param type: str, type of data to retrieve ('departure' or 'arrival')
    :return: str, URL
    """
    base_url = f"https://www.flightera.net/en/airport/Amsterdam/EHAM/{type}/"
    # Format date as 'YYYY-MM-DD' and time as 'HH_MM'
    formatted_date = date.strftime('%Y-%m-%d')
    formatted_time = time.replace(':', '_')
    url = f"{base_url}{formatted_date}%20{formatted_time}?"
    return url


def get_html_data(date, time, type):
    """
    Retrieves HTML data from a URL for a specific date and time.

    :param date: datetime.date, the date for which to retrieve data
    :param time: str, the time in 'HH:MM' format for which to retrieve data
    :return: requests.Response, raw HTML data from the request
    """

    departure_url = generate_url(date, time, type)

    # fake random header generator to not get blacklisted
    fake_header = FakeHttpHeader(domain_name='nl').as_header_dict()

    # old header which got me blacklisted
    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 13729.41.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.76 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': 'RF_BROWSER_ID=k90lBkClQXStk8cYYsmZnA; RF_BID_UPDATED=1; RF_CORVAIR_LAST_VERSION=356.4.0; RF_BROWSER_CAPABILITIES=%7B%22screen-size%22%3A4%2C%22ie-browser%22%3Afalse%2C%22events-touch%22%3Afalse%2C%22ios-app-store%22%3Afalse%2C%22google-play-store%22%3Afalse%2C%22ios-web-view%22%3Afalse%2C%22android-web-view%22%3Afalse%7D; G_ENABLED_IDPS=google; RF_VISITED=true; AKA_A2=A; unifiedLastSearch=name%3DNew%2520York%26subName%3DNew%2520York%252C%2520NY%252C%2520USA%26url%3D%252Fcity%252F30749%252FNY%252FNew-York%26id%3D2_30749%26type%3D2%26unifiedSearchType%3D2%26isSavedSearch%3D%26countryCode%3DUS; RF_LAST_NAV=0; userPreferences=parcels%3Dtrue%26schools%3Dfalse%26mapStyle%3Ds%26statistics%3Dtrue%26agcTooltip%3Dfalse%26agentReset%3Dfalse%26ldpRegister%3Dfalse%26afCard%3D2%26schoolType%3D0%26viewedSwipeableHomeCardsDate%3D1615310319930; RF_MARKET=newyork; RF_LAST_SEARCHED_CITY=Rego%20Park',
        'sec-gpc': '1',
    }

    raw_html = requests.get(departure_url, headers=fake_header)
    return raw_html

# %% prepare data


def process_html_data(raw_html, type):
    """
    Processes HTML data to extract and clean a departure table.

    This function extracts the first table from the HTML, keeps specific columns (date, flight number, and departed/arrived time),
    drops rows with all NaN values, drops rows with NaN in the 'time' column (indicating cancelled flights), 
    and performs custom parsing on the date and time columns.

    :param raw_html: requests.Response, raw HTML data containing the departure table
    :return: pd.DataFrame, cleaned DataFrame with columns ['date', 'flight', 'time']
    """
    # Extract the first table from the HTML response
    departure_table = pd.read_html(raw_html.text)[0]

    # To grab correct column
    if type == 'arrival':
        column = 6
    elif type == 'departure':
        column = 5

    # Keep specific columns and drop rows with all NaN values
    departure_table = departure_table.iloc[:, [0, 1, column]]  # Only keep date, flight number, and time
    departure_table = departure_table.dropna(how='all')  # Remove empty rows
    departure_table.columns = ['date', 'flight', 'time']  # Rename columns

    # Custom function to parse the date string (e.g., "Thu, 10. Aug 2023  08:00 CEST  Landed")
    def parse_date(date_str):
        # Extract the date part (e.g., '10. Aug 2023')
        date_part = ' '.join(date_str.split()[:4])
        return datetime.datetime.strptime(date_part, '%a, %d. %b %Y').date()

    # Apply parsing to date and time columns
    departure_table['date'] = departure_table['date'].apply(parse_date)  # Convert the first column to date and remove time
    departure_table['flight'] = departure_table['flight'].str.split().str[0]  # Extract the first flight number from the second column
    departure_table['time'] = departure_table['time'].str.extract('(\d{2}:\d{2})')  # Convert the last column to time format and remove extra text

    # Drop rows where 'time' is NaN
    departure_table = departure_table.dropna(subset=['time'])

    return departure_table

# %% append dataframe


def append_to_dataframe(existing_df, new_data):
    """
    Appends new data to an existing dataframe. If the existing dataframe is None, 
    it returns the new data as a dataframe.

    :param existing_df: pd.DataFrame or None
    :param new_data: pd.DataFrame
    :return: pd.DataFrame
    """
    if existing_df is not None:
        # Append new_data to existing_df
        return pd.concat([existing_df, new_data], ignore_index=True)
    else:
        # Return new_data as the dataframe
        return new_data


# %% function to get info of specified period in day

def retrieve_data(date, start_time, end_time):
    """
    Retrieves and processes both departure and arrival data for a specified day and time window.

    :param date: datetime.date, the date for which to retrieve data
    :param start_time: str, the start time in 'HH:MM' format for the time window
    :param end_time: str, the end time in 'HH:MM' format for the time window
    :return: tuple of pd.DataFrame, (departure data, arrival data)
    """
    start_datetime = datetime.datetime.combine(date, datetime.datetime.strptime(start_time, '%H:%M').time())
    end_datetime = datetime.datetime.combine(date, datetime.datetime.strptime(end_time, '%H:%M').time())

    departure_data = None
    arrival_data = None

    # Retrieve Departure Data
    current_time = start_datetime
    while current_time <= end_datetime:
        formatted_time = current_time.strftime('%H:%M')
        html_data = get_html_data(date, formatted_time, type='departure')
        processed_data = process_html_data(html_data, type='departure')
        departure_data = append_to_dataframe(departure_data, processed_data)
        current_time += datetime.timedelta(hours=1)

    # Retrieve Arrival Data
    current_time = start_datetime
    while current_time <= end_datetime:
        formatted_time = current_time.strftime('%H:%M')
        html_data = get_html_data(date, formatted_time, type='arrival')
        processed_data = process_html_data(html_data, type='arrival')
        arrival_data = append_to_dataframe(arrival_data, processed_data)
        current_time += datetime.timedelta(hours=1)

    return departure_data, arrival_data


specific_date = datetime.date(2023, 8, 10)
start_time = "08:00"
end_time = "12:00"
departure_data, arrival_data = retrieve_data(specific_date, start_time, end_time)


# %% Find maximunm movements


def find_max_movements(start_date, end_date, start_hour, end_hour, interval):
    """
    Analyzes flight movements data over a range of dates and within a specified hour window each day.
    Finds the maximum number of arrivals and departures within a given interval.
    Prints the maximum movements per day and the overall maximum.

    :param start_date: datetime.date, the start date of the period
    :param end_date: datetime.date, the end date of the period
    :param start_hour: int, the start hour of the analysis window
    :param end_hour: int, the end hour of the analysis window
    :param interval: int, interval in minutes
    :return: dict, information about the day and time with the highest movement count
    """
    max_movements = 0
    max_movement_time = None
    max_movement_day = None

    for single_date in pd.date_range(start=start_date, end=end_date, freq='D'):
        daily_max_movements = 0
        daily_max_time = None

        # Retrieve data for the day
        arrival_data, departure_data = retrieve_data(single_date.date(), f'{start_hour:02d}:00', f'{end_hour:02d}:00')

        for hr in range(start_hour, end_hour):
            for min in range(0, 60, interval):
                current_time = datetime.time(hour=hr, minute=min)
                end_time = (datetime.datetime.combine(datetime.date.today(), current_time) + datetime.timedelta(minutes=interval)).time()

                movements = 0
                for index, row in arrival_data.iterrows():

                    if current_time <= datetime.datetime.strptime(row['time'], "%H:%M").time() < end_time:
                        movements += 1
                for index, row in departure_data.iterrows():
                    if current_time <= datetime.datetime.strptime(row['time'], "%H:%M").time() < end_time:
                        movements += 1

                if movements > daily_max_movements:
                    daily_max_movements = movements
                    daily_max_time = f'{hr:02d}:{min:02d}'

                if movements > max_movements:
                    max_movements = movements
                    max_movement_time = f'{hr:02d}:{min:02d}'
                    max_movement_day = single_date.strftime('%Y-%m-%d')

        print(f"Max movements on {single_date.strftime('%Y-%m-%d')}: {daily_max_movements} at {daily_max_time}")

    print(f"Overall maximum movements: {max_movements} on {max_movement_day} at {max_movement_time}")
    return {'Day': max_movement_day, 'Time': max_movement_time, 'Movement_amount': max_movements}


start_date = datetime.date(2023, 8, 9)
end_date = datetime.date(2023, 8, 11)
start_hour = 4
end_hour = 12
interval = 1  # minute
result = find_max_movements(start_date, end_date, start_hour, end_hour, interval)
