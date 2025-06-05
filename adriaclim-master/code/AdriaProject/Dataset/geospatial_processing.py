import time
import datetime as dt
import pandas as pd
import json
import numpy as np
import logging  # Aggiunto
from typing import List, Dict, Any, Union
from django.db.models import Q
from django.contrib.gis.geos import Polygon as GeosPolygon
from shapely.geometry import Polygon as ShapelyPolygon
import shapely.speedups
from django.core.cache import cache
from Dataset.models import Polygon
from myFunctions.data_analysis import calculate_trend, operation_before_after_cache, processOperation, packageGraphData
from myFunctions.utils import download_with_cache_as_csv
from myFunctions.indicator_manager import getIndicatorQueryUrl

logger = logging.getLogger(__name__)  # Inizializzazione logger

# Constants
CACHE_TIMEOUT = 43200  # 12 hours
MAX_SAMPLING_POINTS = 1000

def log_error(message: str, exception: Exception) -> None:
    """Log errors with a consistent format."""
    logger.error(f"{message}: {exception}")

def create_geos_polygon(vertices: List[tuple]) -> Union[GeosPolygon, str]:
    """Create a GEOS polygon from vertices."""
    shapely_polygon_inverse = ShapelyPolygon(vertices)
    shapely.speedups.enable()
    try:
        return GeosPolygon.from_ewkt(shapely_polygon_inverse.wkt)
    except Exception as e:
        log_error("Error creating GEOS Polygon", e)
        return str(e)

def fetch_from_cache(key: str) -> Union[Dict[str, Any], None]:
    """Fetch data from cache."""
    cache_result = cache.get(key=key)
    if cache_result is not None:
        logger.info("CACHE HIT!")
        return json.loads(cache_result)
    logger.info("CACHE MISS!")
    return None

def save_to_cache(key: str, data: Dict[str, Any]) -> None:
    """Save data to cache."""
    cache.set(key, json.dumps(data), timeout=CACHE_TIMEOUT)

def calculate_statistics(df: pd.DataFrame, values: List[float], time_op: str, adriaclim_timeperiod: str) -> Dict[str, Any]:
    """Calculate statistics like mean, median, standard deviation, and trend."""
    stats = {}
    if values:
        stats["mean"] = np.mean(values)
        stats["median"] = np.median(values)
        stats["stdev"] = np.std(values)
        stats["trend_yr"] = calculate_trend(df["date_value"].tolist(), values, timeperiod=adriaclim_timeperiod)
    return stats

def getDataPolygonNew(
    dataset_id: str,
    adriaclim_timeperiod: str,
    layer_name: str,
    date_start: str,
    date_end: str,
    lat_lng_obj: List[Any],  # <-- cambiato da Dict a Any per gestire anche liste
    statistic: str,
    time_op: str,
    num_param: int,
    range_value: float,
    is_indicator: bool,
    lat_min: float,
    lat_max: float,
    lng_min: float,
    lng_max: float,
    parametro_agg: str,
    circle_coords: List[Dict[str, float]],
) -> Union[Dict[str, Any], str]:
    """
    Fetch polygon data based on the given parameters.
    """
    start_time = time.time()
    logger.info("STARTED getDataPolygonNew!")

    # ✅ Fix per gestire input in formato lista di liste
    if lat_lng_obj and isinstance(lat_lng_obj[0], list):
        lat_lng_obj = [{"lng": p[0], "lat": p[1]} for p in lat_lng_obj]

    # ✅ Ora funziona correttamente il parsing
    vertices = [(float(lat_lng["lat"]), float(lat_lng["lng"])) for lat_lng in lat_lng_obj]
    vertices_geos_poly = [(float(lat_lng["lng"]), float(lat_lng["lat"])) for lat_lng in lat_lng_obj]

    geos_polygon = create_geos_polygon(vertices_geos_poly)
    if isinstance(geos_polygon, str):  # Error occurred
        return geos_polygon

    key_cached = f"{dataset_id}_{str(vertices[0][0]).replace(' ', '')}"
    cached_data = fetch_from_cache(key_cached)
    if cached_data:
        df = pd.DataFrame.from_dict(cached_data["dataBeforeOp"]).dropna()
        df["date_value"] = pd.to_datetime(df["date_value"])
        cached_data["dataPol"] = operation_before_after_cache(df, statistic, time_op)
        cached_data.update(calculate_statistics(df, cached_data["dataPol"].get("y", []), time_op, adriaclim_timeperiod))
        return cached_data

    logger.info("CACHE MISS, checking DB...")
    polygons = Polygon.objects.filter(dataset_id=dataset_id, coordinate__within=geos_polygon)
    if polygons.exists():
        try:
            logger.info("DB HIT!")
            allData = {"dataTable": []}
            for pol in polygons:
                entry = {
                    "time": pol.date_value,
                    "latitude": pol.latitude,
                    "longitude": pol.longitude,
                    layer_name: pol.value_0 if not pd.isna(pol.value_0) else "Value not defined",
                }
                if parametro_agg != "None":
                    entry[parametro_agg] = pol.parametro_agg if not pd.isna(pol.parametro_agg) else "Value not defined"
                allData["dataTable"].append(entry)

            df = pd.DataFrame([p.__dict__ for p in polygons]).drop(columns=["_state", "coordinate"], errors="ignore").drop_duplicates()
            allData["dataBeforeOp"] = df.to_dict(orient="records")
            df["date_value"] = pd.to_datetime(df["date_value"])

            if time_op == "default":
                values = df["value_0"].tolist()
                trend_value = calculate_trend(df["date_value"].tolist(), values, timeperiod=adriaclim_timeperiod) if len(values) > 1 else (values[0] if values else 0)
                allData.update({
                    "mean": np.mean(values),
                    "median": np.median(values),
                    "stdev": np.std(values),
                    "trend_yr": trend_value,
                })

            save_to_cache(key_cached, allData)
            allData["dataPol"] = operation_before_after_cache(df, statistic, time_op)
            logger.info(f"DB TIME: {time.time() - start_time:.2f} seconds")
            return allData

        except Exception as e:
            log_error("Error during DB handling", e)
            return str(e)

    logger.warning("NO CACHE, NO DB! Fetching external data...")
    return "External data fetching not yet implemented here"

def getDataGraphicGeneric(
    dataset_id: str,
    adriaclim_timeperiod: str,
    layer_name: str,
    time_start: str,
    time_finish: str,
    latitude: float,
    longitude: float,
    num_parameters: int,
    range_value: float,
    is_indicator: bool,
    lat_start: Union[str, float],
    long_start: Union[str, float],
    lat_end: Union[str, float],
    long_end: Union[str, float],
    **kwargs,
) -> Union[List[Any], str]:
    """
    Fetch generic graphic data based on the given parameters.
    """
    try:
        onlyone = kwargs.get("context") == "one"
        use_cache = kwargs.get("cache") == "yes"
        operation = kwargs.get("operation")
        output = kwargs.get("output")

        lat_start = latitude if lat_start == "no" else lat_start
        lat_end = latitude if lat_end == "no" else lat_end
        long_start = longitude if long_start == "no" else long_start
        long_end = longitude if long_end == "no" else long_end

        url = getIndicatorQueryUrl(
            dataset_id,
            is_indicator=False,
            is_graph=False,
            latitude=latitude,
            longitude=longitude,
            latitudeMin=lat_start,
            latitudeMax=lat_end,
            longitudeMin=long_start,
            longitudeMax=long_end,
            range=range_value,
            variable=layer_name,
            format="csv",
            timeMin=time_start,
            timeMax=time_finish,
        )

        if use_cache:
            url = download_with_cache_as_csv(url)
        if url == "fuoriWms":
            return url

        try:
            df = pd.read_csv(url, dtype="unicode")
        except Exception as e:
            logger.error("ERRORE pd.read_csv: %s", e)
            return f"ERRORE LETTURA CSV: {str(e)}"

        if df.empty or layer_name not in df.columns:
            return "fuoriWms"

        df = df.iloc[1:, :]  # Skip header row
        n_values = len(df)
        every_nth = max(1, n_values // MAX_SAMPLING_POINTS)
        df_iter = df[::every_nth].iterrows() if n_values > MAX_SAMPLING_POINTS else df.iterrows()

        values, dates, lats, longs, layerName = [], [], [], [], []
        onlylat = onlylong = None

        for _, row in df_iter:
            if onlyone and onlylat is None:
                onlylat, onlylong = row["latitude"], row["longitude"]

            if (
                pd.notna(row[layer_name])
                and row[layer_name] != "NaN"
                and (not onlyone or (onlylat == row["latitude"] and onlylong == row["longitude"]))
            ):
                lats.append(row["latitude"])
                longs.append(row["longitude"])
                layerName.append(layer_name)
                values.append(float(row[layer_name]))
                dates.append(row["time"])

        allData = [values, dates, "", layerName, lats, longs]

        if operation is None:
            return allData
        else:
            try:
                processed = processOperation(operation, values, dates, "", layerName, lats, longs)
                return packageGraphData(processed, output=output, operation=operation, adriaclim_timeperiod=adriaclim_timeperiod)
            except Exception as e:
                log_error("Error in processOperation or packageGraphData", e)
                return str(e)

    except Exception as e:
        log_error("General exception in getDataGraphicGeneric", e)
        return str(e)
