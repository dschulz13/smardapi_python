# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 10:56:50 2026

@author: Dominik Schulz
"""

# Script for SMARD API access

from datetime import datetime
from zoneinfo import ZoneInfo
import requests
import pandas as pd
import numpy as np

def run_api(url):
    try:
        response = requests.get(url, timeout = 30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.JSONDecodeError:
        print("Error: The response server did not return valid JSON.")
    return data

def construct_timestamp_url(filter, region, resolution):
    base_url = 'https://www.smard.de/app'
    extension = '/chart_data/' + str(filter) + '/' + region + \
        '/index_' + resolution + '.json'
    return base_url + extension

def get_timestamps(filter, region, resolution):
    url = construct_timestamp_url(
        filter = filter,
        region = region,
        resolution = resolution
        )
    return run_api(url)['timestamps']

def construct_data_url(filter, region, resolution, timestamps):
    base_url = 'https://www.smard.de/app'
    filter_str = str(filter)
    extension_base = '/chart_data/' + filter_str + '/' + region + \
        '/' + filter_str + '_' + region + '_' + resolution + \
            '_'
    entire_base_url = base_url + extension_base

    return [entire_base_url + timestamp + '.json' for timestamp in [str(ts) for ts in timestamps]]

def filter_timestamps(timestamps, start = '2015-01-01 00:00', stop = None):
    # Timestamps in seconds since 1970-01-01
    timestamps_np = np.array(timestamps) / 1000
    # For default of stop, get current datetime in Berlin
    if stop is None:
        stop = datetime.now(ZoneInfo("Europe/Berlin")).strftime('%Y-%m-%d %H:%M')
    start_int = int(pd.to_datetime(start, format = 'ISO8601').timestamp())
    stop_int = int(pd.to_datetime(stop, format = 'ISO8601').timestamp())
    start_idx = max(np.sum(start_int >= timestamps_np).item() - 1, 0)
    stop_idx = max(np.sum(stop_int >= timestamps_np).item(), 1)
    return timestamps[start_idx:stop_idx]


def get_ts_data(filter, region, resolution, start = '2015-01-01 00:00', stop = None):
    tstamps = filter_timestamps(
        get_timestamps(
            filter = filter,
            region = region,
            resolution = resolution
            ),
        start = start, stop = stop
        )
    data_urls = construct_data_url(
        filter = filter,
        region = region,
        resolution = resolution,
        timestamps = tstamps)
    data_collection = []
    print('Downloading data...')
    for url in data_urls:
        data_collection.append(run_api(url)['series'])
    print('Download successful!')
    combined_list = [subsublist for sublist in data_collection for subsublist in sublist]
    all_tstamps = [int(sublist[0] / 1000) for sublist in combined_list]
    all_values = [sublist[1] for sublist in combined_list]
    df = pd.DataFrame({
        'Timestamp': [datetime.fromtimestamp(tstamp, tz = ZoneInfo("Europe/Berlin")) for tstamp in all_tstamps],
        'Value': all_values
        })
    df.drop_duplicates(subset = ['Timestamp'], ignore_index = True, inplace = True)
    df = df.loc[df['Value'].first_valid_index():df['Value'].last_valid_index()].reset_index(drop = True)
    #df.set_index('Timestamp', inplace = True)
    if df['Value'].isna().any().item():
        print('There are NaN values in the series! Check this thoroughly!')
    else:
        print('There are no NaN values in the series!')
    return df


class smardapi:
    data = None
    
    def __init__(self, filter = None, region = None):
        self.specification = {"filter": filter, "region": region}
    def specify(self, filter, region):
        self.specification = {"filter": filter, "region": region}
    def download(self, resolution, start = '2015-01-01', stop = None):
        self.data = get_ts_data(
            filter = self.specification['filter'],
            region = self.specification['region'],
            resolution = resolution,
            start = start,
            stop = stop)
    def plot(self):
        if (self.data is None):
            print('No data found.')
            return None
        else:
            sub_data = self.data
            sub_data = sub_data.set_index('Timestamp')
            ax = sub_data.plot(legend = False)
            xmin = sub_data.index.min()
            xmax = sub_data.index.max()
            delta = xmax - xmin
            ax.set_xlim(xmin - delta * 0.05, xmax + delta * 0.05)
            return ax
    def save_csv(self, file = "SmardApi.csv"):
        if (self.data is None):
            print('No data found.')
        else:
            self.data.to_csv(
                file,
                sep = ',',
                index = False)
        
