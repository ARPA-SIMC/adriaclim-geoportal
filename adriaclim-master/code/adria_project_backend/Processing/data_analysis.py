import numpy as np
import pandas as pd

from scipy import stats
from .utils import percentile_new
from statistics import mean, median, stdev
from .indicator_manager import url_is_indicator
from AdriaProject.logger_config import setup_logger
from .utils import read_erddap_data

from .time_processing import get_season, seasons, check_dates_format_trend
from AdriaProject.settings import ERDDAP_URL


logger = setup_logger(__name__)


def aggregateGraphicValues(vals, operation):
    """
    Aggrega una lista di valori numerici in base all'operazione richiesta.
    Operazioni supportate: mediana, percentile_10, percentile_90, max, min, avg.
    
    :param vals: Lista di valori numerici
    :param operation: Operazione di aggregazione
    :return: Valore aggregato o None
    """
    if not vals:
        return None

    vals_sorted = sorted(vals)  # Sorting required for percentiles and median

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

    logger.warning(f"Operazione non riconosciuta: {operation}")
    return None


def percentileFunction(array, perc):
    """
    Calcola un percentile personalizzato su un array numerico ordinato manualmente.
    
    :param array: Lista di valori numerici
    :param perc: Percentile da calcolare (0-100)
    :return: Valore del percentile
    """
    array_sorted = sorted(array)  # Sorting required
    k = (len(array_sorted) - 1) * perc / 100
    f = int(k)
    c = min(f + 1, len(array_sorted) - 1)

    if f == c:
        return array_sorted[int(k)]

    # Linear interpolation between the two nearest points
    d0 = array_sorted[f] * (c - k)
    d1 = array_sorted[c] * (k - f)
    return d0 + d1


def subtract_mean_trend(dates, values, timeperiod):
    """
    Sottrae la media del periodo temporale (mensile, giornaliero o stagionale)
    dai valori forniti. Usata per rimuovere la stagionalità nei dati.

    :param dates: Lista di date (stringhe o datetime)
    :param values: Lista di valori numerici
    :param timeperiod: Tipo di periodo da usare per la media ('monthly', 'daily', 'seasonal')
    :return: Array numpy dei valori detrended
    """
    df = pd.DataFrame({
        "date": pd.to_datetime(dates),
        "value": values
    })

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

    # Compute the mean per period and subtract it
    df["mean_timeperiod"] = df.groupby(groupby_col)["value"].transform("mean")
    df["value"] -= df["mean_timeperiod"]

    return df["value"].values


def calculate_trend(dates, values, **kwargs):
    """
    Calcola la pendenza della retta di regressione temporale (trend lineare).
    Se viene passato 'timeperiod' in kwargs (es. monthly), sottrae la stagionalità.

    :param dates: Lista di date
    :param values: Lista di valori numerici
    :param kwargs: timeperiod (facoltativo)
    :return: Coefficiente di tendenza lineare (per anno) o stringa d'errore
    """
    try:
        y = np.array(values)

        # Remove seasonal trend, if specified
        if kwargs.get("timeperiod") and kwargs["timeperiod"] != "yearly":
            y = subtract_mean_trend(dates, y, kwargs["timeperiod"])

        # Convert dates to timestamps
        dates = check_dates_format_trend(dates)
        days = np.array([d.timestamp() for d in dates])

        # Linear regression between days and values
        slope, _, _, _, _ = stats.linregress(days, y)

        # Return the yearly change (daily slope * seconds in one year)
        return slope * 86400 * 365.25

    except Exception as e:
        logger.error(f"Errore in calculate_trend: {e}")
        return str(e)

def updateStatisticsNew(new_dates,new_values,timeperiod,polygon):
    try:
        
        allData = {}
        if polygon is None:
            allData["mean"] = mean(new_values)
            allData["stdev"] = stdev(new_values)
            allData["median"] = median(new_values)
            allData["trend"] = calculate_trend(new_dates,new_values,timeperiod=timeperiod)
        else:
            #is a polygon so we need to calculate mean, stdev, median and trend
            df_stats = pd.DataFrame({"date":new_dates, "value":new_values})
            allData["mean"] = mean(df_stats["value"].tolist())
            allData["stdev"] = stdev(df_stats["value"].tolist())
            allData["median"] = median(df_stats["value"].tolist())
            mean_trend = df_stats.groupby("date")["value"].mean().tolist()
            df_stats = df_stats.drop_duplicates(subset=["date"], keep="first") 
            allData["trend"] = calculate_trend(df_stats["date"].tolist(),mean_trend,timeperiod=timeperiod)
        return allData
    except Exception as e:
        if str(e) == "variance requires at least two data points":
            allData["mean"] = new_values
            allData["stdev"] = new_values
            allData["median"] = new_values
            allData["trend"] = new_values
            return allData

def packageGraphData(allData, **kwargs):
    """
    Prepara i dati per output grafico o CSV. Calcola statistiche base se richiesto.

    :param allData: Lista [values, dates, unit, layerName, lats, longs]
    :param kwargs: Argomenti opzionali come 'operation', 'output', 'adriaclim_timeperiod'
    :return: Dict per grafico oppure stringa CSV
    """
    try:
        values, dates, unit, layerName, lats, longs = allData
        data = {"unit": unit, "entries": []}

        if kwargs.get("operation") == "default":
            try:
                # Compute statistics only if requested
                data.update({
                    "mean": mean(values),
                    "median": median(values),
                    "stdev": stdev(values),
                    "trend_yr": calculate_trend(
                        dates, values, timeperiod=kwargs.get("adriaclim_timeperiod")
                    ),
                })
            except Exception as e:
                if str(e) == "variance requires at least two data points":
                    logger.warning("Solo un dato disponibile, statistiche semplificate.")
                    data.update({key: values for key in ["mean", "stdev", "median", "trend_yr"]})
                else:
                    logger.error(f"Errore nel calcolo delle statistiche: {e}")

        # Output CSV if requested
        if kwargs.get("output") == "csv":
            csv_output = "Date,Dataset,Latitude,Longitude,Value\n"
            csv_output += "\n".join(
                f"{dates[n]},{layerName[n]},{lats[n]},{longs[n]},{values[n]}"
                for n in range(len(values))
            )
            return csv_output

        # Output JSON for chart visualization
        for n in range(len(values)):
            entry = {"x": dates[n], "y": values[n]}
            data.setdefault(layerName[n], []).append(entry)
            data["entries"].append(layerName[n])

        return data

    except Exception as e:
        logger.error(f"Exception in packageGraphData: {e}")
        return str(e)


def processOperation(operation, values, dates, unit, layerName, lats, longs):
    """
    Applica operazioni predefinite sui dati (es. media mensile annuale).
    
    :param operation: Stringa (es. "default", "annualMonth")
    :return: Lista con valori trasformati secondo l'operazione
    """
    import re

    if operation == "default":
        return [values, dates, unit, layerName, lats, longs]

    values2, dates2, layerName2, lats2, longs2 = [], [], [], [], []

    if operation == "annualMonth":
        pattern = re.compile(r"\d{4}-(\d{2})-\S*")
        months = [f"{i:02}" for i in range(1, 13)]
        for mon in months:
            # Create a dummy date for the output
            dat = f"0000-{mon}-01T00:00:00Z"
            # Extract values for the current month
            vals = [
                v for n, v in enumerate(values)
                if pattern.match(dates[n]) and pattern.match(dates[n]).group(1) == mon
            ]
            if vals:
                dates2.append(dat)
                lats2.append(0)
                longs2.append(0)
                layerName2.append(layerName[0])
                values2.append(aggregateGraphicValues(vals, "avg"))

    return [values2, dates2, unit, layerName2, lats2, longs2]


def operation_before_after_cache(df_polygon, statistic, time_op):
    """
    Applica operazioni statistiche su un DataFrame in base al tipo di aggregazione temporale.

    :param df_polygon: DataFrame con colonna 'date_value' e 'value_0'
    :param statistic: Tipo di statistica da applicare
    :param time_op: Tipo di raggruppamento temporale (default, annualMonth, annualSeason, annualDay)
    :return: Lista di dizionari pronti per la visualizzazione
    """
    try:
        # Supported statistics map
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
            groupby_col = df_polygon["date_month"]  # ← Warning: 'date_month' must already exist

        # Determine aggregation functions
        if ops[statistic] == "min_mean_max":
            agg_func = ["min", "mean", "max"]
        elif ops[statistic] == "min_10thPerc_median_90thPerc_max":
            agg_func = ["min", percentile_new(10), "median", percentile_new(90), "max"]
        else:
            agg_func = ops[statistic]

        res_values = df_polygon.groupby(groupby_col)["value_0"].agg(agg_func)
        df_polygon = df_polygon.drop_duplicates(subset=["date_value"], keep="first")

        # Prepare list of time labels
        if time_op == "default":
            list_time = list(res_values.index.strftime('%Y-%m-%dT%H:%M:%SZ'))
        elif time_op == "annualMonth":
            list_time = [str(month) for month in res_values.index.tolist()]
        elif time_op == "annualDay":
            list_time = list(res_values.index.strftime("%d/%m"))
        elif time_op == "annualSeason":
            list_time = [seasons[index] for index in res_values.index.tolist()]

        # Build final data list
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

# def getDataVectorial(
#     dataset_id,
#     layer_name,
#     date_start,
#     latitude_start,
#     latitude_end,
#     longitude_start,
#     longitude_end,
#     num_param,
#     range_value,
#     is_indicator,
# ):
    
#     try:
#         url = url_is_indicator(
#             is_indicator,
#             False,
#             True,
#             dataset_id=dataset_id,
#             layer_name=layer_name,
#             date_start=date_start,
#             latitude_start=latitude_start,
#             latitude_end=latitude_end,
#             longitude_start=longitude_start,
#             longitude_end=longitude_end,
#             num_param=num_param,
#             range_value=range_value,
#         )
#         df = read_erddap_data(url)
#         logger.warning(f"[DEBUG] URL getDataVectorial: {url}")
#         logger.warning(f"[DEBUG] Columns: {df.columns.tolist()}")
#         logger.warning(f"[DEBUG] First rows:\n{df.head(5)}")

#         allData = []
#         values = []
#         lat_coordinates = []
#         long_coordinates = []
#         df = df.dropna(how="any", axis=0)
#         if df.empty:
#             print("DEBUG_EMPTY_ON_SELECTED_DATE")
#         i = 0
#         for index, row in df.iterrows():
#             try:
#                 value = float(row[layer_name])
#             except ValueError:
#                 value = 0.0
#             values.insert(i, value)
#             lat_coordinates.insert(i, row["latitude"])
#             long_coordinates.insert(i, row["longitude"])
#             i += 1
        
#         if values:
#             value_min = min(values)
#             value_max = max(values)
#         else:
#             value_min = 0.0 # Default value if no valid values are available
#             value_max = 0.0 # Default value if no valid values are available
            
#         allData = [values, lat_coordinates, long_coordinates, value_min, value_max]

#         print("DEBUG_GETDATAVECTORIAL", url, df.columns.tolist(), df.head(5).to_dict("records"))
#         return allData
#     except Exception as e:
#         return str(e)

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

        df = read_erddap_data(url)

        values = []
        lat_coordinates = []
        long_coordinates = []

        df = df.dropna(how="any", axis=0)

        if df.empty:
            return {
                "status": "no_data",
                "message": "No data available for the selected date.",
                "values": [],
                "latitudes": [],
                "longitudes": [],
                "value_min": None,
                "value_max": None,
            }

        for _, row in df.iterrows():
            try:
                value = float(row[layer_name])
            except (ValueError, TypeError):
                continue

            values.append(value)
            lat_coordinates.append(row["latitude"])
            long_coordinates.append(row["longitude"])

        if not values:
            return {
                "status": "no_data",
                "message": "No valid values available for the selected date.",
                "values": [],
                "latitudes": [],
                "longitudes": [],
                "value_min": None,
                "value_max": None,
            }

        return {
            "status": "ok",
            "message": "",
            "values": values,
            "latitudes": lat_coordinates,
            "longitudes": long_coordinates,
            "value_min": min(values),
            "value_max": max(values),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "values": [],
            "latitudes": [],
            "longitudes": [],
            "value_min": None,
            "value_max": None,
        }

def getVerticalProfileTimeseries(
    dataset_id,
    layer_name,
    time_start,
    time_end,
    latitude,
    longitude,
    selected_depth=None,
):
    try:
        depth_value = 0 if selected_depth in [None, "", "null"] else selected_depth

        # Query for the selected depth only (used for the graph)
        url = (
            ERDDAP_URL
            + "/griddap/"
            + dataset_id
            + ".csv?"
            + layer_name
            + "%5B("
            + time_start
            + "):1:("
            + time_end
            + ")%5D%5B("
            + str(depth_value)
            + "):1:("
            + str(depth_value)
            + ")%5D%5B("
            + str(latitude)
            + "):1:("
            + str(latitude)
            + ")%5D%5B("
            + str(longitude)
            + "):1:("
            + str(longitude)
            + ")%5D"
        )

        # Query for all depths (used only to populate the depth selector)
        depth_url = (
            ERDDAP_URL
            + "/griddap/"
            + dataset_id
            + ".csv?"
            + layer_name
            + "%5B("
            + time_start
            + "):1:("
            + time_end
            + ")%5D%5B(0):1:(103)%5D%5B("
            + str(latitude)
            + "):1:("
            + str(latitude)
            + ")%5D%5B("
            + str(longitude)
            + "):1:("
            + str(longitude)
            + ")%5D"
        )

        # Read all depths first
        depth_df = read_erddap_data(depth_url)
        available_depths = []

        if depth_df is not None and not depth_df.empty:
            depth_df = depth_df[pd.to_numeric(depth_df["depth"], errors="coerce").notnull()]
            depth_df["depth"] = pd.to_numeric(depth_df["depth"], errors="coerce")
            depth_df[layer_name] = pd.to_numeric(depth_df[layer_name], errors="coerce")
            depth_df = depth_df.dropna(subset=["depth", layer_name])

            if not depth_df.empty:
                available_depths = sorted(depth_df["depth"].dropna().unique().tolist())

        # Read selected depth data for the graph
        df = read_erddap_data(url)

        if df is None or df.empty:
            return {
                "status": "no_data",
                "rows": [],
                "available_depths": available_depths,
                "selected_depth": float(depth_value),
            }

        df = df.dropna(subset=[layer_name])
        df = df[pd.to_numeric(df["depth"], errors="coerce").notnull()]

        if df.empty:
            return {
                "status": "no_data",
                "rows": [],
                "available_depths": available_depths,
                "selected_depth": float(depth_value),
            }

        df = df[["time", "depth", layer_name]]
        df["depth"] = pd.to_numeric(df["depth"], errors="coerce")
        df[layer_name] = pd.to_numeric(df[layer_name], errors="coerce")
        df = df.dropna(subset=["depth", layer_name])

        rows = []
        for _, row in df.iterrows():
            rows.append({
                "time": row["time"],
                "depth": float(row["depth"]),
                "value": float(row[layer_name]),
            })

        return {
            "status": "ok",
            "rows": rows,
            "available_depths": available_depths,
            "selected_depth": float(depth_value),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "rows": [],
            "available_depths": [],
            "selected_depth": float(selected_depth) if selected_depth not in [None, "", "null"] else 0.0,
        }