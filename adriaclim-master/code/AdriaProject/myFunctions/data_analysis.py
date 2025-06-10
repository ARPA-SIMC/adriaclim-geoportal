from datetime import time
import numpy as np
import pandas as pd
import logging  # Aggiunto logger
from statistics import mean, median, stdev
from scipy import stats
from .utils import percentile_new
from .time_processing import get_season, seasons, check_dates_format_trend
from .indicator_manager import url_is_indicator

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

def updateStatistics(new_dates,new_values,timeperiod,polygon):
    try:
        allData = {}
        if polygon is None:
            #single point!
            allData["mean"] = mean(new_values)
            allData["stdev"] = stdev(new_values)
            allData["median"] = median(new_values)
            allData["trend"] = calculate_trend(new_dates,new_values,timeperiod=timeperiod)
        else:
            #is a polygon so we need to calculate mean, stdev, median and trend
            # print("new_values:",new_values)
            df_stats = pd.DataFrame({"date":new_dates, "value":new_values})
            # print("df_stats:",df_stats.head())
            allData["mean"] = mean(df_stats["value"].tolist())
            allData["stdev"] = stdev(df_stats["value"].tolist())
            allData["median"] = median(df_stats["value"].tolist())
            mean_trend = df_stats.groupby("date")["value"].mean().tolist()
            df_stats = df_stats.drop_duplicates(subset=["date"], keep="first") 
            # print("DF_STATS:",df_stats.head(30))
            # df_stats["date"] = pd.to_datetime(df_stats["date"])
            allData["trend"] = calculate_trend(df_stats["date"].tolist(),mean_trend,timeperiod=timeperiod)

        return allData
    except Exception as e:
        if str(e) == "variance requires at least two data points":
            allData["mean"] = new_values
            allData["stdev"] = new_values
            allData["median"] = new_values
            allData["trend"] = new_values
            # print("Errore in update",e)
            return allData

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

def getDataVectorial(
    dataset_id,
    layer_name,
    date_start,
    latitude_start,
    latitude_end,
    longitude_start,
    longitude_end,
    num_param,
    range_value,
    is_indicator,
):
    
    try:
        # print("DATASET ID =", dataset_id)
        # print("LAYER NAME =", layer_name)
        # print("DATE START =", date_start)
        # print("LATITUDE START =", latitude_start)
        # print("LATITUDE END =", latitude_end)
        # print("LONGITUDE START =", longitude_start)
        # print("LONGITUDE END =", longitude_end)
        # print("NUM PARAM =", num_param)
        # print("RANGE VALUE =", range_value)
        # print("IS INDICATOR =", is_indicator)
        # https://erddap.cmcc-opa.eu/erddap/tabledap/ARPAE_f903_2ae5_11cb.htmlTable?time%2Clatitude%2Clongitude%2Ca_95_BO_9_m&time%3E=2022-11-24&time%3C=2022-12-01&latitude%3E=44.214583&latitude%3C=44.214583&longitude%3E=12.47585&longitude%3C=12.47585
        url = url_is_indicator(
            is_indicator,
            False,
            True,
            dataset_id=dataset_id,
            layer_name=layer_name,
            date_start=date_start,
            latitude_start=latitude_start,
            latitude_end=latitude_end,
            longitude_start=longitude_start,
            longitude_end=longitude_end,
            num_param=num_param,
            range_value=range_value,
        )
        print("LAYER NAME =", layer_name)
        print("URL =", url)
        # start_time = time.time()
        df = pd.read_csv(url, dtype="unicode")
        print("DATAFRAME =", df)
        allData = []
        values = []
        lat_coordinates = []
        long_coordinates = []
        df = df.dropna(how="any", axis=0) # per la seconda prova la riga è da scommentare
        # df = df.dropna(subset=[layer_name])
        i = 0
        for index, row in df.iterrows():

            try:
                value = float(row[layer_name])
            except ValueError:
                value = 0.0

            values.insert(i, value)

            # values.insert(i, row[layer_name])
            lat_coordinates.insert(i, row["latitude"])
            long_coordinates.insert(i, row["longitude"])
            i += 1
        
        if values:
            value_min = min(values)
            value_max = max(values)
        else:
            value_min = 0.0 # valore predefinito se non ci sono valori validi
            value_max = 0.0 # valore predefinito se non ci sono valori validi

        # per la seconda prova questi if sono da commentare
        # if 'degrees_north' in lat_coordinates:
        #     lat_coordinates.remove('degrees_north')
        # if 'degrees_east' in long_coordinates:
        #     long_coordinates.remove('degrees_east')
            
        allData = [values, lat_coordinates, long_coordinates, value_min, value_max]

        return allData
    except Exception as e:
        print("ECCEZIONE VETTORIALE", e)
        return str(e)