import numpy as np
import pandas as pd
import logging  # Aggiunto logger
from statistics import mean, median, stdev
from scipy import stats
from .utils import percentile_new
from .time_processing import get_season, seasons, check_dates_format_trend

logger = logging.getLogger(__name__)  # Inizializzazione logger

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
    df = pd.DataFrame({"date": pd.to_datetime(dates), "value": values})
    if timeperiod == "monthly":
        groupby_col = df["date"].dt.month
    elif timeperiod == "daily":
        df["day_month"] = df["date"].dt.strftime('%m-%d')
        groupby_col = df["day_month"]
    elif timeperiod == "seasonal":
        df["season"] = df["date"].apply(get_season)
        groupby_col = df["season"]
    else:
        raise ValueError(f"Invalid timeperiod: {timeperiod}")

    df["mean_timeperiod"] = df.groupby(groupby_col)["value"].transform("mean")
    df["value"] -= df["mean_timeperiod"]

    return df["value"].values

def calculate_trend(dates, values, **kwargs):
    try:
        y = np.array(values)
        if kwargs.get("timeperiod") and kwargs["timeperiod"] != "yearly":
            y = subtract_mean_trend(dates, y, kwargs["timeperiod"])

        dates = check_dates_format_trend(dates)
        days = np.array([d.timestamp() for d in dates])

        slope, _, _, _, _ = stats.linregress(days, y)
        return slope * 86400 * 365.25
    except Exception as e:
        logger.error(f"Errore in calculate_trend: {e}")
        return str(e)

def updateStatistics(new_dates, new_values, polygon, timeperiod):
    try:
        allData = {}
        if polygon is None:
            allData["mean"] = mean(new_values)
            allData["stdev"] = stdev(new_values)
            allData["median"] = median(new_values)
            allData["trend"] = calculate_trend(new_dates, new_values, timeperiod=timeperiod)
        else:
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
            return {key: new_values for key in ["mean", "stdev", "median", "trend"]}
        return {}

def packageGraphData(allData, **kwargs):
    try:
        values, dates, unit, layerName, lats, longs = allData
        data = {"unit": unit, "entries": []}

        if kwargs.get("operation") == "default":
            try:
                data.update({
                    "mean": mean(values),
                    "median": median(values),
                    "stdev": stdev(values),
                    "trend_yr": calculate_trend(dates, values, timeperiod=kwargs.get("adriaclim_timeperiod")),
                })
            except Exception as e:
                if str(e) == "variance requires at least two data points":
                    data.update({key: values for key in ["mean", "stdev", "median", "trend_yr"]})

        if kwargs.get("output") == "csv":
            csv_output = "Date,Dataset,Latitude,Longitude,Value\n"
            csv_output += "\n".join(
                f"{dates[n]},{layerName[n]},{lats[n]},{longs[n]},{values[n]}" for n in range(len(values))
            )
            return csv_output

        for n in range(len(values)):
            entry = {"x": dates[n], "y": values[n]}
            data.setdefault(layerName[n], []).append(entry)
            data["entries"].append(layerName[n])

        return data
    except Exception as e:
        logger.error(f"Exception in packageGraphData: {e}")
        return str(e)

def processOperation(operation, values, dates, unit, layerName, lats, longs):
    import re
    if operation == "default":
        return [values, dates, unit, layerName, lats, longs]

    values2, dates2, layerName2, lats2, longs2 = [], [], [], [], []
    if operation == "annualMonth":
        pattern = re.compile(r"\d{4}-(\d{2})-\S*")
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
            df_polygon["day_month"] = df_polygon["date_value"].dt.strftime('%m-%d')
            groupby_col = df_polygon["date_month"]

        if ops[statistic] == "min_mean_max":
            agg_func = ["min", "mean", "max"]
        elif ops[statistic] == "min_10thPerc_median_90thPerc_max":
            agg_func = ["min", percentile_new(10), "median", percentile_new(90), "max"]
        else:
            agg_func = ops[statistic]

        res_values = df_polygon.groupby(groupby_col)["value_0"].agg(agg_func)
        df_polygon = df_polygon.drop_duplicates(subset=["date_value"], keep="first")

        if time_op == "default":
            list_time = list(res_values.index.strftime('%Y-%m-%dT%H:%M:%SZ'))
        elif time_op == "annualMonth":
            list_time = [str(month) for month in res_values.index.tolist()]
        elif time_op == "annualDay":
            list_time = list(res_values.index.strftime("%d/%m"))
        elif time_op == "annualSeason":
            list_time = [seasons[index] for index in res_values.index.tolist()]

        data_pol_list = []

        if ops[statistic] == "min_mean_max":
            for i in range(len(list_time)):
                data_pol_list.append({
                    "x": list_time[i],
                    "Minimum": res_values["min"].tolist()[i],
                    "Mean": res_values["mean"].tolist()[i],
                    "Maximum": res_values["max"].tolist()[i],
                })
        elif ops[statistic] == "min_10thPerc_median_90thPerc_max":
            for i in range(len(list_time)):
                data_pol_list.append({
                    "x": list_time[i],
                    "Minimum": res_values["min"].tolist()[i],
                    "10th Percentile": res_values["percentile_10"].tolist()[i],
                    "Median": res_values["median"].tolist()[i],
                    "90th Percentile": res_values["percentile_90"].tolist()[i],
                    "Maximum": res_values["max"].tolist()[i],
                })
        else:
            for i in range(len(list_time)):
                data_pol_list.append({
                    "x": list_time[i],
                    "y": list(res_values.values)[i],
                })

        return data_pol_list
    except Exception as e:
        logger.error(f"Exception in operation_before_after_cache: {e}")
        return str(e)
