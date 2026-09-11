"""
Name
----
    smardapi

Source
------
    https://github.com/dschulz13/smardapi_python

Description
-----------
    This module gives access to the SMARD API of the German
    Federal Network Agency. It uses a built-in object class
    to specify, download, plot and save data.

Classes
-------
    SmardApi

Details
-------
    Upon importing the module, the imported object is already
    an object of class SmardApi that can be used immediately
    for specifying and downloading data from the SMARD API.

Version
-------
    0.1.0
    This is still a work in progress.
"""

# Script for SMARD API access

## Identify, which names to copy out on import
__all__ = ['SmardApi']  # Only the SmardApi class, as 
                        # everything else is just
                        # helpers

## Import needed modules
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
import pandas as pd
import numpy as np

## Given a URL, run an API call and return the data
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

## Constructor function for the timestamp API URL
def construct_timestamp_url(filter_no, region, resolution):
    base_url = 'https://www.smard.de/app'
    extension = '/chart_data/' + str(filter_no) + '/' + region + \
        '/index_' + resolution + '.json'
    return base_url + extension

## Function to retrieve timestamps from SMARD API
def get_timestamps(filter_no, region, resolution):
    url = construct_timestamp_url(
        filter_no = filter_no,
        region = region,
        resolution = resolution
        )
    return run_api(url)['timestamps']

## Constructor function for the data API URL given starting time
## stamps for the data packages
def construct_data_url(filter_no, region, resolution, timestamps):
    base_url = 'https://www.smard.de/app'
    filter_str = str(filter_no)
    extension_base = '/chart_data/' + filter_str + '/' + region + \
        '/' + filter_str + '_' + region + '_' + resolution + \
            '_'
    entire_base_url = base_url + extension_base

    return [entire_base_url + timestamp + '.json' for timestamp in [str(ts) for ts in timestamps]]

## Filter timestamps given a starting and a stopping time point
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

## Function to retrieve and format data from the SMARD API
def get_ts_data(filter_no, region, resolution, start = '2015-01-01 00:00', stop = None, silent = False):
    tstamps = filter_timestamps(    # Filter time stamps by start and stop timestamps
        get_timestamps(             # Retrieve available timestamps for data packages
            filter_no = filter_no,
            region = region,
            resolution = resolution
            ),
        start = start, stop = stop
        )
    data_urls = construct_data_url(    # Get API URLs for relevant data packages
        filter_no = filter_no,
        region = region,
        resolution = resolution,
        timestamps = tstamps)
    if ~silent:
        print('Downloading data...')
    data_collection = [run_api(url)['series'] for url in data_urls]
    if ~silent:
        print('Download successful!')
    df = pd.DataFrame({
        'Timestamp': [datetime.fromtimestamp(int(subsublist[0] / 1000), tz = ZoneInfo("Europe/Berlin")) \
            for sublist in data_collection for subsublist in sublist],
        'Value': [subsublist[1] for sublist in data_collection for subsublist in sublist]
        })
    df.drop_duplicates(subset = ['Timestamp'], ignore_index = True, inplace = True)
    df = df.loc[df['Value'].first_valid_index():df['Value'].last_valid_index()].reset_index(drop = True)
    #df.set_index('Timestamp', inplace = True)
    if ~silent:
        if df['Value'].isna().any().item():
            print('There are NaN values in the series! Check this thoroughly!')
        else:
            print('There are no NaN values in the series!')
    return df


## Main object class to specify API settings, download data,
## plot data, and save data


class SmardApi:
    """
    Help on the SmardApi class from module smardapi.

    Attributes:
    -----------
        data             The downloaded data. Is None before a call to .download().
        specification    A dictionary giving filter number and region specifications.
                         Both are None before a call to .specify().

    Purpose:
    --------
        Specify, download, plot and save data from the SMARD API of
        the German Federal Network Agency. This is data on electricity
        production, consumption and prices and various resolution
        levels.

    Example call:
    -------------
        SmardApi()

    Returns:
    --------
        An object of class SmardApi.
    """

    def __init__(self):
        self.data = None,
        self.specification = {"filter_no": None, "region": None}

    def specify(self, filter_no, region):
        """
        Specify the time series type (called the filter number) and
        the region for the SMARD API

        Parameters:
        -----------
            filter_no (int): The filter number specifying the type of series
            region (str):    The region to get the data for

        Returns:
        --------
            Nothing, but it updates the element .specification with
            the provided information.

        Example:
        --------
            import smardapi as smard
            smard.specify(filter_no = 410, region = 'DE')
        """
        self.specification = {"filter_no": filter_no, "region": region}

    def download(self, resolution, start = '2015-01-01', stop = None, silent = False):
        """
        Download the time series specified in .specification

        Parameters:
        -----------
            resolution (str): The resolution of the time series, i.e. the time between
                              observations
            start (str):      The starting time point following the ISO8601 format
            stop (str):       The stopping time point following the ISO8601 format;
                              the default None gets data until the last available time point
            silent (bool):    A boolean indicating whether or not to suppress messages
                              from the download method to the console

        Returns:
        --------
            Nothing, but it downloads the data via the SMARD API and
            updates the element .data to then contain a pd.DataFrame
            with the downloaded data. If .specify() has not been run
            at least once before, this method will simply print
            a message to the console and do nothing otherwise.

        Example:
        --------
            import smardapi as smard
            smard.specify(filter_no = 410, region = 'DE')
            smard.download(resolution = 'day', start = '2016-02-01', stop = '2018-11-11')
        """
        if (self.data is None):
            print('Firstly, use .specify() to specify filter_no and region settings.')
        else:
            self.data = get_ts_data(
                filter_no = self.specification['filter_no'],
                region = self.specification['region'],
                resolution = resolution,
                start = start,
                stop = stop,
                silent = silent)
        
    def plot(self, *args, **kwargs):
        """
        Plot the data in .data as a time series plot

        Parameters:
        -----------
            *args:    Further positional arguments to pass to
                      pd.DataFrame.plot()
            **kwargs: Further keyword arguments to pass to
                      pd.DataFrame.plot()

        Returns:
        --------
            Returns an Axis object. If .download() has not been
            run at least once before, this method just prints
            a message to the console and returns None.

        Example:
        --------
            import smardapi as smard
            smard.specify(filter_no = 410, region = 'DE')
            smard.download(resolution = 'day', start = '2016-02-01', stop = '2018-11-11')
            smard.plot()
        """
        if (self.data is None):
            print('No data found.')
            return None
        else:
            sub_data = self.data.copy()
            sub_data = sub_data.set_index('Timestamp')
            ax = sub_data.plot(*args, **kwargs)
            xmin = sub_data.index.min()
            xmax = sub_data.index.max()
            delta = xmax - xmin
            ax.set_xlim(xmin - delta * 0.05, xmax + delta * 0.05)
            return ax

    def save_csv(self, file = "SmardApi.csv"):
        """
        Save the data in .data as a CSV file

        Parameters:
        -----------
            file (str): The path and filename (with file ending) specifying
                        where and under what name to save the data

        Returns:
        --------
            Returns nothing but saves a CSV file to the specified path.
            If .download() has not been called at least once before, this
            method prints a message to the console.

        Example:
        --------
            import smardapi as smard
            smard.specify(filter_no = 410, region = 'DE')
            smard.download(resolution = 'day', start = '2016-02-01', stop = '2018-11-11')
            smard.save_csv(file = 'NewData.csv')
        """
        if (self.data is None):
            print('No data found.')
        else:
            self.data.to_csv(
                file,
                sep = ',',
                index = False)
    def allowed_filter_no(self):
        """
        Get a dictionary of allowed filter numbers with explanations

        Parameters:
        -----------
            No parameters

        Returns:
        --------
            Returns a dictionary, whose values are the allowed filter numbers
            for filter_no in .specify(). The names of these values give an
            explanation what the numbers stand for.

        Example:
        --------
            import smardapi as smard
            smard.allowed_filter_no()
        """
        print('Check https://smard.api.bund.dev/ for details')
        return {
            "Electricity Production: Lignite": 1223,
            "Electricity Production: Nuclear Energy": 1224,
            "Electricity Production: Wind Offshore": 1225,
            "Electricity Production: Hydropower": 1226,
            "Electricity Production: Other Conventional Sources": 1227,
            "Electricity Production: Other Renewable Sources": 1228,
            "Electricity Production: Biomass": 4066,
            "Electricity Production: Wind Onshore": 4067,
            "Electricity Production: Photovoltaicss": 4068,
            "Electricity Production: Coal": 4069,
            "Electricity Production: Pump Storage": 4070,
            "Electricity Production: Gas": 4071,
            "Electricity Consumption: Total": 410,
            "Electricity Consumption: Residual Load": 4359,
            "Electricity Consumption: Pump Storage": 4387,
            "Market Price: Germany/Luxembourg": 4169,
            "Market Price: Neighbors of Germany/Luxembourg": 5078,
            "Market Price: Belgium": 4996,
            "Market Price: Norway 2": 4997,
            "Market Price: Austria": 4170,
            "Market Price: Denmark 1": 252,
            "Market Price: Denmark 2": 253,
            "Market Price: France": 254,
            "Market Price: Italy (North)": 255,
            "Market Price: Netherlands": 256,
            "Market Price: Poland 1": 257,
            "Market Price: Poland 2": 258,
            "Market Price: Switzerland": 259,
            "Market Price: Slovenia": 260,
            "Market Price: Czech Republic": 261,
            "Market Price: Hungary": 262,
            "Predicted Production: Offshore": 3791,
            "Predicted Production: Onshore": 123,
            "Predicted Production: Photovoltaics": 125,
            "Predicted Production: Others": 715,
            "Predicted Production: Wind and Photovoltaics": 5097,
            "Predicted Production: Total": 122
        }
    def allowed_region(self):
        """
        Get a dictionary of allowed region settings with explanations

        Parameters:
        -----------
            No parameters

        Returns:
        --------
            Returns a dictionary, whose values are the allowed strings
            for region settings for region in .specify(). The names of
            these values give an explanation what the settings stand for.

        Example:
        --------
            import smardapi as smard
            smard.allowed_region()
        """
        print('Check https://smard.api.bund.dev/ for details')
        return {
            "Germany": "DE",
            "Austria": "AT",
            "Luxembourg": "LU",
            "Germany/Luxembourg (from 2018-10-01)": "DE-LU",
            "Germany-Austria-Luxembourg (until 2018-09-30)": "DE-AT-LU",
            "50Hertz control area (Germany)": "50Hertz",
            "Amprion control area (Germany)": "Amprion",
            "TenneT control area (Germany)": "TenneT",
            "TransnetBW control area (Germany)": "TransnetBW",
            "APG control area (Austria)": "APG",
            "Creos control area (Luxembourg)": "Creos"
        }
    def allowed_resolution(self):
        """
        Get a dictionary of allowed resolution settings with explanations

        Parameters:
        -----------
            No parameters

        Returns:
        --------
            Returns a dictionary, whose values are the allowed resolution
            strings for resolution in .download(). The names of these values
            give an explanation what the settings stand for.

        Example:
        --------
            import smardapi as smard
            smard.allowed_resolution()
        """
        print('Check https://smard.api.bund.dev/ for details')
        return {
            "Every 15 Minutes": "quarterhour",
            "Hourly": "hour",
            "daily": "day",
            "Weekly": "week",
            "Monthly": "month",
            "Yearly": "year"
        }
