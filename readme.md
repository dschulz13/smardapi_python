# smardapi

This is a Python package for specifying, downloading, plotting and saving time series data from the [SMARD API](https://smard.api.bund.dev/) of the German Federal Network Agency.

## Installation

Install the latest package version from GitHub via entering the following in the terminal:


```pip install git+https://github.com/dschulz13/smardapi_python.git```

## Example

Firstly, import the module under a self-selected name. This is already a working instance of the class "SmardApi".


```python
import smardapi as smard
```

Then specify the series and region via `smard.specify()`. For available options, call `smard.allowed_filter_no()` and `smard.allowed_region()`.


```python
smard.specify(filter_no = 410, region = "DE")
```

The previos code specifies the region as Germany (`region = "DE"`) and the series to be the total electricity consumption (`filter_no = 410`).

Afterwards, we are ready to download the data via `smard.download()`.


```python
smard.download(resolution = "day", start = "2016-03-15", stop = "2023-05-11")
```

    Downloading data...
    Download successful!
    There are no NaN values in the series!
    

`resolution` defines the observation frequency. Here, we pick daily. For an overview of the options, see `smard.allowed_resolution()`. Furthermore, `start` and `stop` are timestamps that align with the ISO8601 standard and they define the time window for which to download the data. For more granular data, like hourly data via `resolution = "hour"`, `start` and `stop` may also include times.

`smard.data` now contains a `pandas` data frame with the downloaded data.


```python
smard.data.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Timestamp</th>
      <th>Value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2016-01-01 00:00:00+01:00</td>
      <td>1063470.42</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2016-01-02 00:00:00+01:00</td>
      <td>1198901.79</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2016-01-03 00:00:00+01:00</td>
      <td>1181825.57</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2016-01-04 00:00:00+01:00</td>
      <td>1445246.36</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2016-01-05 00:00:00+01:00</td>
      <td>1498693.79</td>
    </tr>
  </tbody>
</table>
</div>



Now, we may wish to create a plot of the downloaded series.


```python
smard.plot()
```




    <Axes: xlabel='Timestamp'>




    
![png](output_11_1.png)
    


The `.plot()` method may contain any further positional or keyword arguments from `pandas.DataFrame.plot()`.

The data frame in `smard.data` may also be saved locally to your device using `smard.save_csv()`.


```smard.save_csv(file = "NewData.csv")```

## Contact

Issues can be stated at https://github.com/dschulz13/smardapi_python/issues. Otherwise, please feel free to reach out via dominik.schulz.r@gmail.com.
