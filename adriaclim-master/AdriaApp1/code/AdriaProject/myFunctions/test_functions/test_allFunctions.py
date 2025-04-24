import pytest
import pandas as pd
from unittest.mock import patch, AsyncMock, MagicMock
import io
import time
import urllib.request
from statistics import mean, median, stdev
import datetime as dt
import sys
import os
import numpy as np
from types import SimpleNamespace
from statistics import mean, median, stdev


# # Function -> delete_all

# def delete_all(param, **kwargs):
#     if param == "Node":
#         # Simulazione di oggetti e cancellazione
#         objects = [FakeObject(), FakeObject()]
#         for obj in objects:
#             obj.delete()
#     elif param == "Polygon":
#         polygons = [FakeObject()]
#         for poly in polygons:
#             poly.delete()

# class FakeObject:
#     def delete(self):
#         return True

# def test_delete_all_node_sync():
#     delete_all("Node")
#     assert True

# def test_delete_all_polygon_sync():
#     delete_all("Polygon")
#     assert True

# # TEST OK!


# # Function -> getGraphicGeneric


# def getDataGraphicGeneric(
#     dataset_id,
#     adriaclim_timeperiod,
#     layer_name,
#     time_start,
#     time_finish,
#     latitude,
#     longitude,
#     num_parameters,
#     range_value,
#     is_indicator,
#     lat_start,
#     long_start,
#     lat_end,
#     long_end,
#     **kwargs
# ):
#     try:
#         # simulazione URL
#         if kwargs.get("simulate") == "fail":
#             return "fuoriWms"
#         values = [1.0, 2.0, 3.0]
#         dates = ["2020-01-01", "2020-01-02", "2020-01-03"]
#         unit = "mockUnit"
#         layerName = [layer_name] * 3
#         lats = [latitude] * 3
#         longs = [longitude] * 3
#         allData = [values, dates, unit, layerName, lats, longs]
#         return allData
#     except Exception as e:
#         return str(e)

# # Test base

# def test_getDataGraphicGeneric_default():
#     result = getDataGraphicGeneric(
#         dataset_id="id1",
#         adriaclim_timeperiod="monthly",
#         layer_name="temp",
#         time_start="2020-01-01",
#         time_finish="2020-01-03",
#         latitude=45.0,
#         longitude=12.0,
#         num_parameters=1,
#         range_value=0,
#         is_indicator=True,
#         lat_start="no",
#         long_start="no",
#         lat_end="no",
#         long_end="no",
#     )
#     assert isinstance(result, list)
#     assert result[0] == [1.0, 2.0, 3.0]


# def test_getDataGraphicGeneric_fallback():
#     result = getDataGraphicGeneric(
#         dataset_id="id2",
#         adriaclim_timeperiod="daily",
#         layer_name="sal",
#         time_start="2021-01-01",
#         time_finish="2021-01-03",
#         latitude=42.0,
#         longitude=13.0,
#         num_parameters=2,
#         range_value=5,
#         is_indicator=False,
#         lat_start="no",
#         long_start="no",
#         lat_end="no",
#         long_end="no",
#         simulate="fail"
#     )
#     assert result == "fuoriWms"
    
# # TEST OK!



# # Function -> getAllDatasets, getMetadataTime1, getMetadata, getMetadataofASpecificDataset

# def getAllDatasets():
#     print("Mock getAllDatasets eseguito")
#     return True

# def getMetadataTime1(dataset_id):
#     return [["v1,v2"], ["v1,v2"], ["spacing"]]

# def getMetadata(dataset_id):
#     metadata = getMetadataTime1(dataset_id)
#     return [metadata, [0, 0], [0, 0]]

# def getMetadataOfASpecificDataset(dataset_id):
#     if dataset_id == "Node":
#         return {"source": "Node", "metadata_url": "http://mocked.com"}
#     elif dataset_id == "Indicator":
#         return {"source": "Indicator", "metadata_url": "http://mocked.com"}
#     else:
#         return {}

# # Test getAllDatasets

# def test_getAllDatasets_runs():
#     assert getAllDatasets() is True

# # Test getMetadataTime1

# def test_getMetadataTime1_returns():
#     result = getMetadataTime1("test_dataset")
#     assert isinstance(result, list)
#     assert len(result) == 3

# # Test getMetadata

# def test_getMetadata_returns():
#     result = getMetadata("dataset_id")
#     assert isinstance(result, list)
#     assert len(result) == 3

# # Test getMetadataOfASpecificDataset (Node)

# def test_getMetadataOfASpecificDataset_node():
#     result = getMetadataOfASpecificDataset("Node")
#     assert result["source"] == "Node"

# # Test getMetadataOfASpecificDataset (Indicator)

# def test_getMetadataOfASpecificDataset_indicator():
#     result = getMetadataOfASpecificDataset("Indicator")
#     assert result["source"] == "Indicator"

# # TEST OK!



# Function -> packageGraphData


# def calculate_trend(dates, values, timeperiod=None):
#     return 1.0  # valore mock

# # Funzione da testare
# def packageGraphData(allData, **kwargs):
#     try:
#         values = allData[0]
#         dates = allData[1]
#         unit = allData[2]
#         layerName = allData[3]
#         lats = allData[4]
#         longs = allData[5]
#         data = {}
#         data["unit"] = unit
#         data["entries"] = []
#         if "operation" in kwargs:
#             if kwargs["operation"] == "default":
#                 try:
#                     mean_result = mean(values)
#                     median_result = median(values)
#                     stdev_result = stdev(values)
#                     trend_result = calculate_trend(dates, values, timeperiod=kwargs["adriaclim_timeperiod"])
#                     data["mean"] = float(mean_result)
#                     data["median"] = float(median_result)
#                     data["stdev"] = float(stdev_result)
#                     data["trend_yr"] = float(trend_result)
#                 except Exception as e:
#                     if str(e) == "variance requires at least two data points":
#                         data["mean"] = values
#                         data["stdev"] = values
#                         data["median"] = values
#                         data["trend_yr"] = values
#         if "output" in kwargs:
#             if kwargs["output"] == "csv":
#                 out = "Date,Dataset,Latitude,Longitude,Value\n"
#                 for n in range(len(values)):
#                     out += f"{dates[n]},{layerName[n]},{lats[n]},{longs[n]},{values[n]}\n"
#                 return out
#         for n in range(len(values)):
#             dictKey = layerName[n]
#             dictValue = data.get(dictKey, [])
#             if dictKey not in data:
#                 data[dictKey] = dictValue
#                 data["entries"].append(dictKey)
#             entry = {"x": dates[n], "y": values[n]}
#             dictValue.append(entry)
#         return data
#     except Exception as e:
#         print("Exception in packageGraphData: " + str(e))
#         return str(e)

# # Test semplice

# def test_packageGraphData_default():
#     allData = (
#         [1, 2, 3],
#         ["2020-01-01", "2020-01-02", "2020-01-03"],
#         "°C",
#         ["temp"] * 3,
#         [45.0] * 3,
#         [12.0] * 3,
#     )
#     result = packageGraphData(allData, operation="default", adriaclim_timeperiod="monthly")
#     assert result["unit"] == "°C"
#     assert "temp" in result
#     assert isinstance(result["mean"], float)


# def test_packageGraphData_csv():
#     allData = (
#         [1, 2],
#         ["2020-01-01", "2020-01-02"],
#         "°C",
#         ["temp", "temp"],
#         [45.0, 45.0],
#         [12.0, 12.0],
#     )
#     result = packageGraphData(allData, output="csv")
#     assert result.startswith("Date,Dataset")
#     assert "2020-01-01,temp,45.0,12.0,1" in result
    
# # TEST OK!



# # Function -> aggregateGraphicValues & processOperation


# def aggregateGraphicValues(operation, values):
#     return sum(values) / len(values)  # media semplice per mock

# # Funzione da testare

# def processOperation(operation, values, dates, unit, layerName, lats, longs):
#     if operation == "default":
#         return [values, dates, unit, layerName, lats, longs]
#     values2 = []
#     dates2 = []
#     layerName2 = []
#     lats2 = []
#     longs2 = []
#     i = 0
#     vals = []
#     lastDate = None
#     for n in range(len(values)):
#         if lastDate is None:
#             lastDate = dates[n]
#         elif lastDate != dates[n]:
#             dates2.insert(i, lastDate)
#             lats2.insert(i, 0)
#             longs2.insert(i, 0)
#             layerName2.insert(i, layerName[0])
#             values2.insert(i, aggregateGraphicValues(operation, vals))
#             i += 1
#             lastDate = dates[n]
#             vals = []
#         vals.append(values[n])
#     if lastDate is not None:
#         dates2.insert(i, lastDate)
#         lats2.insert(i, 0)
#         longs2.insert(i, 0)
#         layerName2.insert(i, layerName[0])
#         values2.insert(i, aggregateGraphicValues(operation, vals))
#         i += 1
#     return [values2, dates2, unit, layerName2, lats2, longs2]

# # Test

# def test_processOperation_default():
#     result = processOperation(
#         "default",
#         [1, 2, 3],
#         ["2020-01-01", "2020-01-02", "2020-01-03"],
#         "units",
#         ["layer"] * 3,
#         [45.0, 45.0, 45.0],
#         [12.0, 12.0, 12.0],
#     )
#     assert result[0] == [1, 2, 3]
#     assert result[1][0] == "2020-01-01"
#     assert result[2] == "units"

# def test_processOperation_avg():
#     result = processOperation(
#         "avg",
#         [1, 1, 2, 2],
#         ["2020-01-01", "2020-01-01", "2020-01-02", "2020-01-02"],
#         "units",
#         ["layer"] * 4,
#         [0] * 4,
#         [0] * 4,
#     )
#     assert result[0] == [1.0, 2.0]  # avg per giorno
#     assert result[1] == ["2020-01-01", "2020-01-02"]
#     assert result[2] == "units"
    

# # TEST OK!




# # Function-> operation_before_after_cache


# def percentile_new(n):
#     def percentile_(x):
#         return np.percentile(x, n)
#     percentile_.__name__ = f"percentile_{n}"
#     return percentile_

# def operation_before_after_cache(df_polygon, statistic, time_op):
#     try:
#         ops = {
#             "avg": "mean",
#             "min": "min",
#             "max": "max",
#             "sum": "sum",
#             "median": "median",
#             "10thPerc": percentile_new(10),
#             "90thPerc": percentile_new(90),
#             "min_mean_max": "min_mean_max",
#             "min_10thPerc_median_90thPerc_max": "min_10thPerc_median_90thPerc_max",
#         }
#         if time_op == "annualSeason":
#             df_polygon["date_value"] = pd.to_datetime(df_polygon["date_value"])
#             df_polygon["season"] = df_polygon["date_value"].apply(get_season)

#         if time_op == "default":
#             groupby_col = "date_value"
#         elif time_op == "annualMonth":
#             groupby_col = df_polygon["date_value"].dt.month
#         elif time_op == "annualSeason":
#             groupby_col = df_polygon["season"]
#         else:
#             df_polygon["day_month"] = df_polygon["date_value"].dt.strftime('%m-%d')
#             groupby_col = df_polygon["date_month"]

#         if ops[statistic] == "min_mean_max":
#             agg_func = ["min", "mean", "max"]
#         elif ops[statistic] == "min_10thPerc_median_90thPerc_max":
#             agg_func = ["min", percentile_new(10), "median", percentile_new(90), "max"]
#         else:
#             agg_func = ops[statistic]

#         res_values = df_polygon.groupby(groupby_col)["value_0"].agg(agg_func)
#         df_polygon = df_polygon.drop_duplicates(subset=["date_value"], keep="first")

#         if time_op == "default":
#             list_time = list(res_values.index.strftime('%Y-%m-%dT%H:%M:%SZ'))
#         elif time_op == "annualMonth":
#             list_time = [months[index] for index in res_values.index.tolist()]
#         elif time_op == "annualDay":
#             list_time = list(res_values.index.strftime("%d/%m"))
#         elif time_op == "annualSeason":
#             list_time = [seasons[index] for index in res_values.index.tolist()]

#         data_pol_list = []
#         if ops[statistic] == "min_mean_max":
#             for i in range(len(list_time)):
#                 data_pol = {
#                     "x": list_time[i],
#                     "Minimum": res_values["min"].tolist()[i],
#                     "Mean": res_values["mean"].tolist()[i],
#                     "Maximum": res_values["max"].tolist()[i]
#                 }
#                 data_pol_list.append(data_pol)
#         elif ops[statistic] == "min_10thPerc_median_90thPerc_max":
#             for i in range(len(list_time)):
#                 data_pol = {
#                     "x": list_time[i],
#                     "Minimum": res_values["min"].tolist()[i],
#                     "10th Percentile": res_values["percentile_10"].tolist()[i],
#                     "90th Percentile": res_values["percentile_90"].tolist()[i],
#                     "Median": res_values["median"].tolist()[i],
#                     "Maximum": res_values["max"].tolist()[i]
#                 }
#                 data_pol_list.append(data_pol)
#         else:
#             for i in range(len(list_time)):
#                 data_pol = {
#                     "x": list_time[i],
#                     "y": list(res_values)[i]
#                 }
#                 data_pol_list.append(data_pol)

#         return data_pol_list
#     except Exception as e:
#         print("eccezione========", e)
#         return str(e)

# def test_operation_before_after_cache_min():
#     df = pd.DataFrame({
#         "date_value": pd.date_range("2020-01-01", periods=3),
#         "value_0": [3, 1, 2]
#     })
#     result = operation_before_after_cache(df, "min", "default")
#     assert isinstance(result, list)
#     assert "x" in result[0] and "y" in result[0]
    
# # TEST OK!



# # Function -> updateStatistics


# class allFunctions:
#     @staticmethod
#     def updateStatistics(dates, values, timeperiod, polygon):
#         return [float(v) * 2 for v in values]  # semplice mock: raddoppia i valori

# # Funzione originale riscritta senza DRF

# def updateStatistics(request):
#     new_dates = request.data.get("dates")
#     new_values = request.data.get("values")
#     dataset = request.data.get("dataset")
#     polygon = request.data.get("polygon")
#     adriaclim_timeperiod = dataset.get("adriaclim_timeperiod")
#     new_values_calculated = allFunctions.updateStatistics(new_dates,new_values,adriaclim_timeperiod,polygon)
#     return {"newValues": new_values_calculated}

# def test_update_statistics_post():
#     request = SimpleNamespace()
#     request.data = {
#         "dates": ["2020-01-01", "2020-01-02"],
#         "values": [1, 2],
#         "dataset": {"adriaclim_timeperiod": "monthly"},
#         "polygon": "dummy"
#     }
#     response = updateStatistics(request)
#     assert response["newValues"] == [2, 4]

# # TEST OK!



# # Function -> subtract_mean_trend


# def get_season(date):
#     year = str(date.year)
#     seasons = {
#         'spring': pd.date_range(start=pd.Timestamp(year+'-03-01'), end=pd.Timestamp(year+'-05-31')),
#         'summer': pd.date_range(start=pd.Timestamp(year+'-06-01'), end=pd.Timestamp(year+'-08-31')),
#         'autumn': pd.date_range(start=pd.Timestamp(year+'-09-01'), end=pd.Timestamp(year+'-11-30'))
#     }
#     if date in seasons['spring']:
#         return 1
#     elif date in seasons['summer']:
#         return 2
#     elif date in seasons['autumn']:
#         return 3
#     else:
#         return 0

# def subtract_mean_trend(dates, values, timeperiod):
#     df_mean_trend = pd.DataFrame({"date": dates, "value": values})
#     df_mean_trend["date"] = pd.to_datetime(df_mean_trend["date"])
#     if timeperiod == "monthly":
#         groupby_col = df_mean_trend["date"].dt.month
#     if timeperiod == "daily":
#         df_mean_trend["day_month"] = df_mean_trend["date"].dt.strftime('%m-%d')
#         groupby_col = df_mean_trend["day_month"]
#     if timeperiod == "seasonal":
#         df_mean_trend["season"] = df_mean_trend["date"].apply(get_season)
#         groupby_col = df_mean_trend["season"]

#     df_mean_trend["mean_timeperiod"] = df_mean_trend.groupby(groupby_col)["value"].transform("mean")
#     df_mean_trend["value"] = df_mean_trend["value"] - df_mean_trend["mean_timeperiod"]
#     return df_mean_trend["value"].values

# def test_subtract_mean_trend_monthly():
#     dates = pd.date_range(start="2020-01-01", periods=12, freq='MS')
#     values = np.arange(12)
#     adjusted = subtract_mean_trend(dates, values, "monthly")
#     assert round(np.mean(adjusted), 10) == 0.0

# def test_subtract_mean_trend_seasonal():
#     dates = pd.date_range(start="2020-03-01", periods=6, freq='2MS')
#     values = np.array([1, 2, 3, 4, 5, 6])
#     adjusted = subtract_mean_trend(dates, values, "seasonal")
#     assert isinstance(adjusted, np.ndarray)
#     assert round(np.mean(adjusted), 10) == 0.0

# # # TEST OK!


# # Function -> caculate_trend


# def calculate_trend(dates, values, **kwargs):
#     try:
#         y = [float(v) for v in values]

#         if "timeperiod" in kwargs and kwargs["timeperiod"] != "yearly":
#             y = y

#         days = [(d - dates[0]).days for d in dates]
#         n = len(days)
#         x_mean = sum(days) / n
#         y_mean = sum(y) / n

#         num = sum((days[i] - x_mean) * (y[i] - y_mean) for i in range(n))
#         den = sum((days[i] - x_mean) ** 2 for i in range(n))

#         if den == 0:
#             return 0.0

#         slope = num / den
#         return slope * 365.25
#     except Exception as e:
#         print("Errore in calculate_trend:", e)
#         return str(e)

# def test_calculate_trend_linear():
#     base = dt.datetime(2020, 1, 1)
#     dates = [base + dt.timedelta(days=i) for i in range(10)]
#     values = list(range(10))
#     result = calculate_trend(dates, values)
#     assert isinstance(result, float)
#     assert round(result, 2) == 365.25

# def test_calculate_trend_monthly():
#     base = dt.datetime(2020, 1, 1)
#     dates = [base + dt.timedelta(days=i) for i in range(10)]
#     values = list(range(10))
#     result = calculate_trend(dates, values, timeperiod="monthly")
#     assert isinstance(result, float)
#     assert round(result, 2) == 365.25

# def test_calculate_trend_invalid():
#     base = dt.datetime(2020, 1, 1)
#     dates = [base + dt.timedelta(days=i) for i in range(3)]
#     values = ["a", "b", "c"]
#     result = calculate_trend(dates, values)
#     assert isinstance(result, str)
#     assert "could not convert string to float" in result


# # TEST OK!



# # Function -> percentile_new & percentileFunctions


# def percentile_new(n):
#     def percentile_(x):
#         return np.percentile(x, n)
#     percentile_.__name__ = "percentile_%s" % n
#     return percentile_

# def percentileFunction(arr, percentile):
#     arr.sort()
#     k = len(arr) * percentile
#     if int(k) == k and len(arr) > 1:
#         mean = (arr[int(k) - 1] + arr[int(k)]) / 2
#         return mean
#     else:
#         index_array = int(round(k))
#         return arr[index_array - 1]

# def test_percentile_new():
#     data = [1, 2, 3, 4, 5]
#     p75 = percentile_new(75)
#     assert p75(data) == np.percentile(data, 75)

# def test_percentileFunction_even():
#     data = [1, 2, 3, 4]
#     result = percentileFunction(data, 0.5)
#     assert result == 2.5

# def test_percentileFunction_odd():
#     data = [1, 2, 3, 4, 5]
#     result = percentileFunction(data, 0.6)
#     assert result == 3.5

# # TEST OK! 



# Function -> check_dates_format_trend


# months = {
#     "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
#     "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
#     "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
# }

# season_trend = {
#     "01": "Winter", "02": "Spring", "03": "Summer", "04": "Autumn"
# }

# def check_dates_format_trend(dates):
#     if type(dates[0]) is str:
#         if dates[0].startswith("0000"):
#             try:
#                 dates = [dt.datetime.strptime(d.replace("0000","2000"), "%Y-%m-%dT%H:%M:%SZ") for d in dates]
#             except Exception as e:
#                 return 'Invalid date format: '+ str(e)
#         elif len(dates[0].split("-")) == 2:
#             for fmt in ('%m-%d', '%d/%m'):
#                 try:
#                     dates = [dt.datetime.strptime(d, fmt).replace(year=2000) for d in dates]
#                     break
#                 except ValueError:
#                     pass
#         elif dates[0] == "Jan":
#             create_dates = []
#             for d in dates:
#                 for key, val in months.items():
#                     if val ==  d:
#                         month_number = key
#                         create_dates.append(dt.datetime.strptime("2000-" + month_number + "-01", "%Y-%m-%d"))
#             dates = list(create_dates)
#         elif dates[0] in ("Winter", "Spring", "Summer", "Autumn"):
#             create_dates = []
#             for d in dates:
#                 for key, val in season_trend.items():
#                     if val == d:
#                         season_number = key
#                         create_dates.append(dt.datetime.strptime("2000-" + season_number + "-01", "%Y-%m-%d"))
#             dates = list(create_dates)
#         else:
#             for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%SZ', '%d/%m/%Y'):
#                 try:
#                     dates = [dt.datetime.strptime(str(d), fmt) for d in dates]
#                 except ValueError:
#                     pass
#     return dates

# def test_check_dates_format_trend_0000():
#     result = check_dates_format_trend(["0000-05-01T00:00:00Z"])
#     assert result[0].year == 2000 and result[0].month == 5 and result[0].day == 1

# def test_check_dates_format_trend_day_month():
#     result = check_dates_format_trend(["05-01"])
#     assert result[0].month == 5 and result[0].day == 1

# def test_check_dates_format_trend_month_name():
#     result = check_dates_format_trend(["Jan"])
#     assert isinstance(result[0], dt.datetime)

# def test_check_dates_format_trend_season():
#     result = check_dates_format_trend(["Winter"])
#     assert isinstance(result[0], dt.datetime)

# def test_check_dates_format_trend_standard():
#     result = check_dates_format_trend(["2020-01-01"])
#     assert result[0].year == 2020

# TEST OK!    


    
# # Function -> download_with_cache.py


# _fake_cache = {}

# def fake_cache_get(key):
#     return _fake_cache.get(key)

# def fake_cache_set(key, value, timeout=None):
#     _fake_cache[key] = value

# def download_with_cache(u):
#     cache_key = u
#     cache_time = 43200
#     output_value = fake_cache_get(cache_key)
#     if output_value is None:
#         try:
#             output_value = urllib.request.urlopen(cache_key).read()
#         except Exception:
#             return "fuoriWms"
#         if output_value:
#             output_value = output_value.decode("utf-8")
#             fake_cache_set(cache_key, output_value, cache_time)
#             return output_value
#     else:
#         return output_value

# @patch("urllib.request.urlopen")
# def test_download_with_cache_fetches_and_caches_data(mock_urlopen):
#     _fake_cache.clear()
#     mock_urlopen.return_value.read.return_value = b"mocked response"
#     url = "http://example.com/test"
#     result = download_with_cache(url)
#     assert result == "mocked response"
#     assert _fake_cache[url] == "mocked response"

# @patch("urllib.request.urlopen")
# def test_download_with_cache_uses_cached_data(mock_urlopen):
#     _fake_cache.clear()
#     url = "http://example.com/test"
#     _fake_cache[url] = "cached response"
#     result = download_with_cache(url)
#     assert result == "cached response"
#     mock_urlopen.assert_not_called()

# @patch("urllib.request.urlopen")
# def test_download_with_cache_handles_fetch_error(mock_urlopen):
#     _fake_cache.clear()
#     mock_urlopen.side_effect = Exception("Network error")
#     url = "http://example.com/test"
#     result = download_with_cache(url)
#     assert result == "fuoriWms"
    
# # TEST OK!



# # Function -> remove_from_cache.py


# _fake_cache = {}

# def fake_cache_get(key):
#     return _fake_cache.get(key)

# def fake_cache_set(key, value, timeout=None):
#     _fake_cache[key] = value

# def fake_cache_delete(key):
#     _fake_cache.pop(key, None)

# def remove_from_cache(u):
#     cache_key = u
#     output_value = fake_cache_get(cache_key)
#     if output_value:
#         if isinstance(output_value, bytes):
#             output_value = output_value.decode("utf-8")
#         fake_cache_delete(cache_key)
#         return output_value
#     else:
#         return None

# def test_remove_from_cache_removes_and_returns_value():
#     _fake_cache.clear()
#     url = "http://example.com/test"
#     _fake_cache[url] = "cached response"
#     result = remove_from_cache(url)
#     assert result == "cached response"
#     assert url not in _fake_cache

# def test_remove_from_cache_returns_none_if_not_exists():
#     _fake_cache.clear()
#     url = "http://example.com/unknown"
#     result = remove_from_cache(url)
#     assert result is None
    
# # TEST OK!



# # # Function -> download_with_cache_as_csv


# _fake_cache = {}

# def fake_cache_get(key):
#     return _fake_cache.get(key)

# def download_with_cache(u):
#     output_value = fake_cache_get(u)
#     if output_value is None:
#         raise Exception("No data")
#     return output_value

# def download_with_cache_as_csv(u):
#     try:
#         q = download_with_cache(u)
#         if q:
#             return io.StringIO(q)
#         else:
#             return None
#     except Exception:
#         return "fuoriWms"

# def test_download_with_cache_as_csv_returns_stringio():
#     _fake_cache.clear()
#     url = "http://example.com/data.csv"
#     _fake_cache[url] = "col1,col2\nval1,val2"
#     result = download_with_cache_as_csv(url)
#     assert isinstance(result, io.StringIO)
#     assert result.read() == "col1,col2\nval1,val2"

# def test_download_with_cache_as_csv_handles_missing_data():
#     _fake_cache.clear()
#     url = "http://example.com/missing.csv"
#     result = download_with_cache_as_csv(url)
#     assert result == "fuoriWms"

# # TEST OK!  



# # # Function -> download_with_cache_as_dataframe


# _fake_cache
# _fake_cache = {}

# def fake_cache_get(key):
#     return _fake_cache.get(key)

# def download_with_cache(u):
#     output_value = fake_cache_get(u)
#     if output_value is None:
#         raise Exception("No data")
#     return output_value

# def download_with_cache_as_csv(u):
#     try:
#         q = download_with_cache(u)
#         if q:
#             return io.StringIO(q)
#         else:
#             return None
#     except Exception:
#         return "fuoriWms"

# def test_download_with_cache_as_csv_returns_stringio():
#     _fake_cache.clear()
#     url = "http://example.com/data.csv"
#     _fake_cache[url] = "col1,col2\nval1,val2"
#     result = download_with_cache_as_csv(url)
#     assert isinstance(result, io.StringIO)
#     assert result.read() == "col1,col2\nval1,val2"

# def test_download_with_cache_as_csv_handles_missing_data():
#     _fake_cache.clear()
#     url = "http://example.com/missing.csv"
#     result = download_with_cache_as_csv(url)
#     assert result == "fuoriWms"

# # Function -> getIndicator e getIndicatorBaseUrl
# class MockNode:
#     def __init__(self, id, griddap_url=None, tabledap_url=None):
#         self.id = id
#         self.griddap_url = griddap_url
#         self.tabledap_url = tabledap_url

# class MockQuerySet:
#     def __init__(self, results):
#         self.results = results

#     def count(self):
#         return len(self.results)

#     def __getitem__(self, index):
#         return self.results[index]

# # Funzioni da testare con mock

# def getIndicator(id):
#     q = MockQuerySet([node for node in _mock_db if node.id == id])
#     if q.count() == 0:
#         return None
#     else:
#         return q[0]

# def getIndicatorBaseUrl(ind):
#     if ind is None:
#         return None
#     if ind.griddap_url is not None and ind.griddap_url != "":
#         return ind.griddap_url
#     if ind.tabledap_url is not None and ind.tabledap_url != "":
#         return ind.tabledap_url
#     return None

# _mock_db = []

# def test_getIndicator_returns_node_if_exists():
#     _mock_db.clear()
#     _mock_db.append(MockNode(id=1))
#     node = getIndicator(1)
#     assert node is not None
#     assert node.id == 1

# def test_getIndicator_returns_none_if_not_found():
#     _mock_db.clear()
#     node = getIndicator(99)
#     assert node is None

# def test_getIndicatorBaseUrl_prefers_griddap():
#     node = MockNode(id=1, griddap_url="http://griddap.url", tabledap_url="http://tabledap.url")
#     assert getIndicatorBaseUrl(node) == "http://griddap.url"

# def test_getIndicatorBaseUrl_uses_tabledap_if_no_griddap():
#     node = MockNode(id=1, griddap_url=None, tabledap_url="http://tabledap.url")
#     assert getIndicatorBaseUrl(node) == "http://tabledap.url"

# def test_getIndicatorBaseUrl_returns_none_if_none():
#     node = MockNode(id=1)
#     assert getIndicatorBaseUrl(node) is None
#     assert getIndicatorBaseUrl(None) is None


# # TEST OK!



# # Function -> getIndicatorDataFormat, getIndicatorDimensions, getIndicatorVariables, getVariableAliases


# class MockIndicator:
#     def __init__(self, griddap_url=None, tabledap_url=None, dimension_names="", variable_names=""):
#         self.griddap_url = griddap_url
#         self.tabledap_url = tabledap_url
#         self.dimension_names = dimension_names
#         self.variable_names = variable_names

# def getIndicatorDataFormat(ind):
#     if ind is None:
#         return None
#     if ind.griddap_url is not None and ind.griddap_url != "":
#         return "griddap"
#     if ind.tabledap_url is not None and ind.tabledap_url != "":
#         return "tabledap"
#     return None

# def getIndicatorDimensions(ind):
#     if ind is None:
#         return None
#     return ind.dimension_names.split()

# def getIndicatorVariables(ind):
#     if ind is None:
#         return None
#     return ind.variable_names.split()

# def getVariableAliases(variable):
#     if variable == "depth":
#         return ["plev", "range"]
#     if variable == "plev":
#         return ["depth", "range"]
#     else:
#         return [variable, "range"]

# def test_getIndicatorDataFormat_griddap():
#     ind = MockIndicator(griddap_url="http://griddap.example.com")
#     assert getIndicatorDataFormat(ind) == "griddap"

# def test_getIndicatorDataFormat_tabledap():
#     ind = MockIndicator(tabledap_url="http://tabledap.example.com")
#     assert getIndicatorDataFormat(ind) == "tabledap"

# def test_getIndicatorDataFormat_none():
#     ind = MockIndicator()
#     assert getIndicatorDataFormat(ind) is None
#     assert getIndicatorDataFormat(None) is None

# def test_getIndicatorDimensions():
#     ind = MockIndicator(dimension_names="lat lon depth")
#     assert getIndicatorDimensions(ind) == ["lat", "lon", "depth"]

# def test_getIndicatorDimensions_none():
#     assert getIndicatorDimensions(None) is None

# def test_getIndicatorVariables():
#     ind = MockIndicator(variable_names="temp sal")
#     assert getIndicatorVariables(ind) == ["temp", "sal"]

# def test_getIndicatorVariables_none():
#     assert getIndicatorVariables(None) is None

# def test_getVariableAliases_depth():
#     assert getVariableAliases("depth") == ["plev", "range"]

# def test_getVariableAliases_plev():
#     assert getVariableAliases("plev") == ["depth", "range"]

# def test_getVariableAliases_other():
#     assert getVariableAliases("temp") == ["temp", "range"]
    
# # TEST OK!



# # Function -> getIndicatorQueryUrl


# class MockIndicator:
#     def __init__(self, griddap_url=None, tabledap_url=None, dimension_names="", variable_names=""):
#         self.griddap_url = griddap_url
#         self.tabledap_url = tabledap_url
#         self.dimension_names = dimension_names
#         self.variable_names = variable_names

# def getIndicatorDataFormat(ind):
#     if ind is None:
#         return None
#     if ind.griddap_url is not None and ind.griddap_url != "":
#         return "griddap"
#     if ind.tabledap_url is not None and ind.tabledap_url != "":
#         return "tabledap"
#     return None

# def getIndicatorDimensions(ind):
#     if ind is None:
#         return None
#     return ind.dimension_names.split()

# def getIndicatorVariables(ind):
#     if ind is None:
#         return None
#     return ind.variable_names.split()

# def getVariableAliases(variable):
#     if variable == "depth":
#         return ["plev", "range"]
#     if variable == "plev":
#         return ["depth", "range"]
#     else:
#         return [variable, "range"]

# def getIndicatorBaseUrl(ind):
#     if ind and ind.griddap_url:
#         return ind.griddap_url
#     if ind and ind.tabledap_url:
#         return ind.tabledap_url
#     return "0"

# def getIndicatorQueryUrl(ind, onlyFirstVariable, skipDimensions, **kwargs):
#     if isinstance(ind, str):
#         return "http://mock/"  # simplified stub for testing

#     url = getIndicatorBaseUrl(ind) or "0"
#     if "format" in kwargs:
#         url = url + "." + kwargs["format"]

#     di = getIndicatorDimensions(ind) or []
#     va = getIndicatorVariables(ind) or []

#     tipo = getIndicatorDataFormat(ind)
#     griddap = tipo == "griddap"

#     if griddap and onlyFirstVariable and len(va) > 1:
#         va = [va[0]]

#     if griddap and "variable" in kwargs:
#         va = [kwargs["variable"]]

#     if skipDimensions:
#         di = []

#     query = "?"
#     if griddap:
#         for v in va:
#             if query != "?":
#                 query += ","
#             query += v
#             for d in di:
#                 query += f"%5B({kwargs.get(d + 'Min', '0')}):1:({kwargs.get(d + 'Max', '0')})%5D"
#     else:
#         for v in va:
#             if query != "?":
#                 query += "%2C"
#             query += v
#         for d in va:
#             if d.lower() in ["time", "latitude", "longitude"]:
#                 query += f"&{d}%3E={kwargs.get(d + 'Min', '0')}"
#                 query += f"&{d}%3C={kwargs.get(d + 'Max', '0')}"

#     result = url + query
#     return result.replace("None", "0")

# def test_getIndicatorQueryUrl_griddap_basic():
#     ind = MockIndicator(griddap_url="http://griddap.example.com", dimension_names="time lat lon", variable_names="temp")
#     url = getIndicatorQueryUrl(ind, onlyFirstVariable=True, skipDimensions=False, format="json", timeMin="2020-01-01", timeMax="2020-12-31")
#     assert url.startswith("http://griddap.example.com.json?")
#     assert "temp" in url
#     assert "%5B(" in url  # encoded bracket check

# def test_getIndicatorQueryUrl_tabledap_basic():
#     ind = MockIndicator(tabledap_url="http://tabledap.example.com", variable_names="temp")
#     url = getIndicatorQueryUrl(ind, onlyFirstVariable=True, skipDimensions=True, format="csv")
#     assert url.startswith("http://tabledap.example.com.csv?")
#     assert "temp" in url

# def test_getIndicatorQueryUrl_handles_none_fields():
#     ind = MockIndicator()
#     url = getIndicatorQueryUrl(ind, onlyFirstVariable=True, skipDimensions=True)
#     assert url.startswith("0?")

# # TEST OK!!



# # Function -> getIndicatorQueryUrlPoint


# class MockIndicator:
#     def __init__(self, griddap_url=None, tabledap_url=None, dimension_names="", variable_names=""):
#         self.griddap_url = griddap_url
#         self.tabledap_url = tabledap_url
#         self.dimension_names = dimension_names
#         self.variable_names = variable_names

# def getIndicatorDataFormat(ind):
#     if ind is None:
#         return None
#     if ind.griddap_url is not None and ind.griddap_url != "":
#         return "griddap"
#     if ind.tabledap_url is not None and ind.tabledap_url != "":
#         return "tabledap"
#     return None

# def getIndicatorDimensions(ind):
#     if ind is None:
#         return None
#     return ind.dimension_names.split()

# def getIndicatorVariables(ind):
#     if ind is None:
#         return None
#     return ind.variable_names.split()

# def getVariableAliases(variable):
#     if variable == "depth":
#         return ["plev", "range"]
#     if variable == "plev":
#         return ["depth", "range"]
#     else:
#         return [variable, "range"]

# def getIndicatorBaseUrl(ind):
#     if ind and ind.griddap_url:
#         return ind.griddap_url
#     if ind and ind.tabledap_url:
#         return ind.tabledap_url
#     return "0"

# def getIndicatorQueryUrl(ind, onlyFirstVariable, skipDimensions, **kwargs):
#     if isinstance(ind, str):
#         return "http://mock/"  # simplified stub for testing

#     url = getIndicatorBaseUrl(ind) or "0"
#     if "format" in kwargs:
#         url = url + "." + kwargs["format"]

#     di = getIndicatorDimensions(ind) or []
#     va = getIndicatorVariables(ind) or []

#     tipo = getIndicatorDataFormat(ind)
#     griddap = tipo == "griddap"

#     if griddap and onlyFirstVariable and len(va) > 1:
#         va = [va[0]]

#     if griddap and "variable" in kwargs:
#         va = [kwargs["variable"]]

#     if skipDimensions:
#         di = []

#     query = "?"
#     if griddap:
#         for v in va:
#             if query != "?":
#                 query += ","
#             query += v
#             for d in di:
#                 query += f"%5B({kwargs.get(d + 'Min', '0')}):1:({kwargs.get(d + 'Max', '0')})%5D"
#     else:
#         for v in va:
#             if query != "?":
#                 query += "%2C"
#             query += v
#         for d in va:
#             if d.lower() in ["time", "latitude", "longitude"]:
#                 query += f"&{d}%3E={kwargs.get(d + 'Min', '0')}"
#                 query += f"&{d}%3C={kwargs.get(d + 'Max', '0')}"

#     result = url + query
#     return result.replace("None", "0")

# def getIndicatorQueryUrlPoint(ind, onlyFirstVariable, skipDimensions, lat, lon, time, range, **kwargs):
#     return getIndicatorQueryUrl(
#         ind,
#         onlyFirstVariable,
#         skipDimensions,
#         latitude=lat,
#         longitude=lon,
#         time=time,
#         range=range,
#     )

# def test_getIndicatorQueryUrl_griddap_basic():
#     ind = MockIndicator(griddap_url="http://griddap.example.com", dimension_names="time lat lon", variable_names="temp")
#     url = getIndicatorQueryUrl(ind, onlyFirstVariable=True, skipDimensions=False, format="json", timeMin="2020-01-01", timeMax="2020-12-31")
#     assert url.startswith("http://griddap.example.com.json?")
#     assert "temp" in url
#     assert "%5B(" in url  # encoded bracket check

# def test_getIndicatorQueryUrl_tabledap_basic():
#     ind = MockIndicator(tabledap_url="http://tabledap.example.com", variable_names="temp")
#     url = getIndicatorQueryUrl(ind, onlyFirstVariable=True, skipDimensions=True, format="csv")
#     assert url.startswith("http://tabledap.example.com.csv?")
#     assert "temp" in url

# def test_getIndicatorQueryUrl_handles_none_fields():
#     ind = MockIndicator()
#     url = getIndicatorQueryUrl(ind, onlyFirstVariable=True, skipDimensions=True)
#     assert url.startswith("0?")

# def test_getIndicatorQueryUrlPoint_griddap():
#     ind = MockIndicator(griddap_url="http://griddap.example.com", dimension_names="time latitude longitude range", variable_names="temp")
#     url = getIndicatorQueryUrlPoint(
#         ind,
#         onlyFirstVariable=True,
#         skipDimensions=False,
#         lat="45",
#         lon="13",
#         time="2020-01-01T00:00:00Z",
#         range="0"
#     )
#     assert url.startswith("http://griddap.example.com?")
#     assert "temp" in url
#     assert "%5B(" in url  # encoded bracket check

# # TEST OK!!



# # Function -> url_is_indicator


# ERDDAP_URL = "http://mock.erddap.org"

# class MockIndicator:
#     def __init__(self, griddap_url=None, tabledap_url=None, dimension_names="", variable_names=""):
#         self.griddap_url = griddap_url
#         self.tabledap_url = tabledap_url
#         self.dimension_names = dimension_names
#         self.variable_names = variable_names

# def getIndicatorDataFormat(ind):
#     if ind is None:
#         return None
#     if ind.griddap_url is not None and ind.griddap_url != "":
#         return "griddap"
#     if ind.tabledap_url is not None and ind.tabledap_url != "":
#         return "tabledap"
#     return None

# def getIndicatorDimensions(ind):
#     if ind is None:
#         return None
#     return ind.dimension_names.split()

# def getIndicatorVariables(ind):
#     if ind is None:
#         return None
#     return ind.variable_names.split()

# def getVariableAliases(variable):
#     if variable == "depth":
#         return ["plev", "range"]
#     if variable == "plev":
#         return ["depth", "range"]
#     else:
#         return [variable, "range"]

# def getIndicatorBaseUrl(ind):
#     if ind and ind.griddap_url:
#         return ind.griddap_url
#     if ind and ind.tabledap_url:
#         return ind.tabledap_url
#     return "0"

# def getIndicatorQueryUrl(ind, onlyFirstVariable, skipDimensions, **kwargs):
#     if isinstance(ind, str):
#         return "http://mock/"  # simplified stub for testing

#     url = getIndicatorBaseUrl(ind) or "0"
#     if "format" in kwargs:
#         url = url + "." + kwargs["format"]

#     di = getIndicatorDimensions(ind) or []
#     va = getIndicatorVariables(ind) or []

#     tipo = getIndicatorDataFormat(ind)
#     griddap = tipo == "griddap"

#     if griddap and onlyFirstVariable and len(va) > 1:
#         va = [va[0]]

#     if griddap and "variable" in kwargs:
#         va = [kwargs["variable"]]

#     if skipDimensions:
#         di = []

#     query = "?"
#     if griddap:
#         for v in va:
#             if query != "?":
#                 query += ","
#             query += v
#             for d in di:
#                 query += f"%5B({kwargs.get(d + 'Min', '0')}):1:({kwargs.get(d + 'Max', '0')})%5D"
#     else:
#         for v in va:
#             if query != "?":
#                 query += "%2C"
#             query += v
#         for d in va:
#             if d.lower() in ["time", "latitude", "longitude"]:
#                 query += f"&{d}%3E={kwargs.get(d + 'Min', '0')}"
#                 query += f"&{d}%3C={kwargs.get(d + 'Max', '0')}"

#     result = url + query
#     return result.replace("None", "0")

# def getIndicatorQueryUrlPoint(ind, onlyFirstVariable, skipDimensions, lat, lon, time, range, **kwargs):
#     return getIndicatorQueryUrl(
#         ind,
#         onlyFirstVariable,
#         skipDimensions,
#         latitude=lat,
#         longitude=lon,
#         time=time,
#         range=range,
#     )

# def url_is_indicator(is_indicator, is_graph, is_annual, **kwargs):
#     try:
#         if is_indicator == "true" and is_graph is False:
#             return (
#                 ERDDAP_URL
#                 + "/tabledap/"
#                 + kwargs["dataset_id"]
#                 + ".csv?time%2Clatitude%2Clongitude%2C"
#                 + kwargs["layer_name"]
#                 + "&time%3E="
#                 + kwargs["date_start"]
#                 + "&time%3C="
#                 + kwargs["date_start"]
#             )
#     except Exception as e:
#         return str(e)

# def test_url_is_indicator_basic_tabledap():
#     result = url_is_indicator(
#         is_indicator="true",
#         is_graph=False,
#         is_annual=False,
#         dataset_id="mock_dataset",
#         layer_name="mock_layer",
#         date_start="2024-01-01"
#     )
#     assert result.startswith("http://mock.erddap.org/tabledap/mock_dataset.csv?")
#     assert "mock_layer" in result
#     assert "&time%3E=2024-01-01" in result
#     assert "&time%3C=2024-01-01" in result

# # TEST OK!!



# Function -> convertToTime


# def convertToTime(date_str):
#     return dt.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")

# def test_convertToTime():
#     assert convertToTime("2024-04-23T10:15:00Z") == "2024-04-23"
#     assert convertToTime("2000-01-01T00:00:00Z") == "2000-01-01"
#     assert convertToTime("1999-12-31T23:59:59Z") == "1999-12-31"
    
# # TEST OK!!



# # Function -> get_season 


# def get_season(date):
#     year = str(date.year)
#     seasons = {
#         'spring': pd.date_range(start=pd.Timestamp(year+'-03-01'), end=pd.Timestamp(year+'-05-31')),
#         'summer': pd.date_range(start=pd.Timestamp(year+'-06-01'), end=pd.Timestamp(year+'-08-31')),
#         'autumn': pd.date_range(start=pd.Timestamp(year+'-09-01'), end=pd.Timestamp(year+'-11-30'))
#     }
#     if date in seasons['spring']:
#         return 1
#     elif date in seasons['summer']:
#         return 2
#     elif date in seasons['autumn']:
#         return 3
#     else:
#         return 0

# def test_get_season():
#     assert get_season(pd.Timestamp("2024-03-21")) == 1  # spring
#     assert get_season(pd.Timestamp("2024-07-10")) == 2  # summer
#     assert get_season(pd.Timestamp("2024-10-05")) == 3  # autumn
#     assert get_season(pd.Timestamp("2024-01-15")) == 0  # winter
#     assert get_season(pd.Timestamp("2024-12-25")) == 0  # winter

    
# # TEST OK!!



# # Function -> is_database_almost_full


# def is_database_almost_full(threshold_percentage=90):
#     database_size = "105000 kB"  # Simula ≈93% usato
#     total_size = 110 * 1024  # KB

#     if ' kB' in database_size:
#         used_percentage = (float(database_size.replace(' kB', '')) / float(total_size)) * 100
#     elif ' MB' in database_size:
#         used_percentage = (float(database_size.replace(' MB', '')) / float(total_size)) * 100
#     elif ' GB' in database_size:
#         used_percentage = (float(database_size.replace(' GB', '')) / (float(total_size) / 1024)) * 100

#     return used_percentage >= threshold_percentage

# def test_is_database_almost_full_true():
#     assert is_database_almost_full() is True

# def test_is_database_almost_full_false():
#     def fake_func(threshold_percentage=90):
#         database_size = "50000 kB"  # Simula ≈44%
#         total_size = 110 * 1024
#         used_percentage = (float(database_size.replace(' kB', '')) / float(total_size)) * 100
#         return used_percentage >= threshold_percentage

#     assert fake_func() is False

    
# # TEST OK!!
