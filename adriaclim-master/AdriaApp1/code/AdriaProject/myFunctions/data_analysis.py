import numpy as np
import pandas as pd
import datetime as dt
from .utils import percentile_new
from .time_processing import get_season, seasons, check_dates_format_trend
# from myFunctions.data_analysis import operation_before_after_cache, calculate_trend
from statistics import mean, median, stdev
from scipy import stats



def aggregateGraphicValues(vals, operation):
    if not vals:
        return None
    vals_sorted = sorted(vals)
    if operation == "mediana":
        return np.median(vals_sorted)
    elif operation == "percentile_10":
        return np.percentile(vals_sorted, 10)
    elif operation == "percentile_90":
        return np.percentile(vals_sorted, 90)
    elif operation == "max":
        return max(vals_sorted)
    elif operation == "min":
        return min(vals_sorted)
    elif operation == "avg":
        return sum(vals_sorted) / len(vals_sorted)
    return None

def percentileFunction(array, perc):
    array_sorted = sorted(array)
    k = (len(array_sorted) - 1) * perc / 100
    f = int(k)
    c = min(f + 1, len(array_sorted) - 1)
    if f == c:
        return array_sorted[int(k)]
    d0 = array_sorted[f] * (c - k)
    d1 = array_sorted[c] * (k - f)
    return d0 + d1

def subtract_mean_trend(dates, values, timeperiod):
    # Creation of a dataframe with dates and values
    df_mean_trend = pd.DataFrame({"date": dates, "value": values})
    df_mean_trend["date"] = pd.to_datetime(df_mean_trend["date"])

    if timeperiod == "monthly":
        groupby_col = df_mean_trend["date"].dt.month
    elif timeperiod == "daily":
        df_mean_trend["day_month"] = df_mean_trend["date"].dt.strftime('%m-%d')
        groupby_col = df_mean_trend["day_month"]
    elif timeperiod == "seasonal":
        df_mean_trend["season"] = df_mean_trend["date"].apply(get_season)
        groupby_col = df_mean_trend["season"]

    # Group by the timeperiod scale and calculate the mean
    df_mean_trend["mean_timeperiod"] = df_mean_trend.groupby(groupby_col)["value"].transform("mean")

    # Subtract the mean of the respective time period from the value
    df_mean_trend["value"] = df_mean_trend["value"] - df_mean_trend["mean_timeperiod"]

    return df_mean_trend["value"].values

def calculate_trend(dates, values, **kwargs):
    try:
        y = np.array(values)
        if "timeperiod" in kwargs and kwargs["timeperiod"] != "yearly":
            y = subtract_mean_trend(dates, y, kwargs["timeperiod"])

        # Check and format the dates
        dates = check_dates_format_trend(dates)
        days = np.array([d.timestamp() for d in dates])
        
        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(days, y)
        return slope * 86400 * 365.25  # Convert slope to yearly trend
    except Exception as e:
        print("Errore in calculate_trend:", e)
        return str(e)

def updateStatistics(new_dates, new_values, timeperiod, polygon):
    try:
        allData = {}
        if polygon is None:  # Single point
            allData["mean"] = mean(new_values)
            allData["stdev"] = stdev(new_values)
            allData["median"] = median(new_values)
            allData["trend"] = calculate_trend(new_dates, new_values, timeperiod=timeperiod)
        else:  # Polygon (area)
            df_stats = pd.DataFrame({"date": new_dates, "value": new_values})
            allData["mean"] = mean(df_stats["value"].tolist())
            allData["stdev"] = stdev(df_stats["value"].tolist())
            allData["median"] = median(df_stats["value"].tolist())
            mean_trend = df_stats.groupby("date")["value"].mean().tolist()
            df_stats = df_stats.drop_duplicates(subset=["date"], keep="first")
            allData["trend"] = calculate_trend(df_stats["date"].tolist(), mean_trend, timeperiod=timeperiod)

        return allData
    except Exception as e:
        if str(e) == "variance requires at least two data points":
            allData["mean"] = new_values
            allData["stdev"] = new_values
            allData["median"] = new_values
            allData["trend"] = new_values
        return allData

def packageGraphData(allData, **kwargs):
    try:
        values = allData[0]
        dates = allData[1]
        unit = allData[2]
        layerName = allData[3]
        lats = allData[4]
        longs = allData[5]
        data = {"unit": unit, "entries": []}
        
        # Perform operation if requested
        if "operation" in kwargs:
            if kwargs["operation"] == "default":
                try:
                    mean_result = mean(values)
                    median_result = median(values)
                    stdev_result = stdev(values)
                    trend_result = calculate_trend(dates, values, timeperiod=kwargs["adriaclim_timeperiod"])
                    data["mean"] = mean_result
                    data["median"] = median_result
                    data["stdev"] = stdev_result
                    data["trend_yr"] = trend_result
                except Exception as e:
                    if str(e) == "variance requires at least two data points":
                        data["mean"] = values
                        data["stdev"] = values
                        data["median"] = values
                        data["trend_yr"] = values

        # Handle CSV output if requested
        if "output" in kwargs and kwargs["output"] == "csv":
            out = "Date,Dataset,Latitude,Longitude,Value\n"
            for n in range(len(values)):
                out += f"{dates[n]},{layerName[n]},{lats[n]},{longs[n]},{values[n]}\n"
            return out

        # Construct the data for each entry
        for n in range(len(values)):
            dictKey = layerName[n]
            dictValue = data.get(dictKey, [])
            data[dictKey] = dictValue
            data["entries"].append(dictKey)
            entry = {"x": dates[n], "y": values[n]}
            dictValue.append(entry)

        return data
    except Exception as e:
        print("Exception in packageGraphData:", str(e))
        return str(e)

def processOperation(operation, values, dates, unit, layerName, lats, longs):
    if operation == "default":
        return [values, dates, unit, layerName, lats, longs]
    
    values2 = []
    dates2 = []
    layerName2 = []
    lats2 = []
    longs2 = []
    i = 0
    vals = []
    lastDate = None

    if operation == "annualMonth":
        pattern = re.compile("\d\d\d\d-(\d\d)-\S*")
        months = [f"{i:02}" for i in range(1, 13)]
        for mon in months:
            dat = f"0000-{mon}-01T00:00:00Z"
            vals = [v for n, v in enumerate(values) if pattern.match(dates[n]).group(1) == mon]
            if vals:
                dates2.append(dat)
                lats2.append(0)
                longs2.append(0)
                layerName2.append(layerName[0])
                values2.append(aggregateGraphicValues(vals, "avg"))

        return [values2, dates2, unit, layerName2, lats2, longs2]

    # Additional operations can be added (annualDay, annualSeason, etc.)
    # Follow the same structure as annualMonth, modify as needed

    return [values2, dates2, unit, layerName2, lats2, longs2]

def operation_before_after_cache(df_polygon, statistic, time_op):
    try:
        ops = {
            "avg": "mean",
            "min": "min",
            "max": "max",
            "sum": "sum",
            "median": "median",
            "10thPerc": percentile_new(10),
            "90thPerc": percentile_new(90),
            "min_mean_max": "min_mean_max",
            "min_10thPerc_median_90thPerc_max": "min_10thPerc_median_90thPerc_max",
        }
        if time_op == "annualSeason":
            df_polygon["date_value"] = pd.to_datetime(df_polygon["date_value"])
            df_polygon["season"] = df_polygon["date_value"].apply(get_season)
        
        if time_op == "default":
            groupby_col = "date_value"
        elif time_op == "annualMonth":
            groupby_col = df_polygon["date_value"].dt.month
        elif time_op == "annualSeason":
            groupby_col = df_polygon["season"]
        else: 
            #group by day and month
            df_polygon["day_month"] = df_polygon["date_value"].dt.strftime('%m-%d')
            groupby_col = df_polygon["date_month"]

            

        if ops[statistic] == "min_mean_max":
            agg_func = ["min", "mean", "max"]
        elif ops[statistic] == "min_10thPerc_median_90thPerc_max":
            agg_func = ["min", percentile_new(10), "median", percentile_new(90), "max"]
        else:
            agg_func = ops[statistic]
        # AGG IS USED TO APPLY AN AGGREGATE FUNCTION AND YOU NEED TO PASS IT THE NAME OF THE FUNCTION (min,avg,max etc)!!!

        res_values = df_polygon.groupby(groupby_col)["value_0"].agg(
            agg_func
        )  # AGG IS USED TO APPLY AN AGGREGATE FUNCTION
        # print("res_values", res_values)
        df_polygon = df_polygon.drop_duplicates(subset=["date_value"], keep="first")
        if time_op == "default":
            # list_time = list(res_values.index.strftime("%d/%m/%Y"))
            list_time = list(res_values.index.strftime('%Y-%m-%dT%H:%M:%SZ'))
        elif time_op == "annualMonth":
            list_time = [months[index] for index in res_values.index.tolist()]
        elif time_op == "annualDay":
            list_time = list(res_values.index.strftime("%d/%m"))
        elif time_op == "annualSeason":
            list_time = [seasons[index] for index in res_values.index.tolist()]

        data_pol_list = []

        if ops[statistic] == "min_mean_max":
            list_min = res_values["min"].tolist()
            list_max = res_values["max"].tolist()
            list_mean = res_values["mean"].tolist()
            for i in range(len(list_time)):
                data_pol = {}
                data_pol["x"] = list_time[i]
                data_pol["Minimum"] = list_min[i]
                data_pol["Mean"] = list_mean[i]
                data_pol["Maximum"] = list_max[i]
                data_pol_list.append(data_pol)

        elif ops[statistic] == "min_10thPerc_median_90thPerc_max":
            list_10th_perc = res_values["percentile_10"].tolist()
            list_90th_perc = res_values["percentile_90"].tolist()
            list_min = res_values["min"].tolist()
            list_max = res_values["max"].tolist()
            list_median = res_values["median"].tolist()
            for i in range(len(list_time)):
                data_pol = {}
                data_pol["x"] = list_time[i]
                data_pol["Minimum"] = list_min[i]
                data_pol["10th Percentile"] = list_10th_perc[i]
                data_pol["90th Percentile"] = list_90th_perc[i]
                data_pol["Median"] = list_median[i]
                data_pol["Maximum"] = list_max[i]
                data_pol_list.append(data_pol)
        else:
            list_value = list(res_values.values)
            for i in range(len(list_time)):
                data_pol = {}
                data_pol["x"] = list_time[i]
                data_pol["y"] = list_value[i]
                data_pol_list.append(data_pol)

        # vale per entrambi allo stesso modo data_table_list e anche di allData
        return data_pol_list
    except Exception as e:
        print("eccezione========", e)
        return str(e)


