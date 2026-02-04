import time
import json
import numpy as np
import pandas as pd
import datetime as dt
import geopandas as gpd
from shapely.prepared import prep
from shapely import Point
import shapely.speedups # type: ignore
import urllib.request
import re

from django.db.models import Q
from django.core.cache import cache
from django.forms import model_to_dict
from django.contrib.gis.geos import Point as GEOSPoint
from django.contrib.gis.geos import Polygon as GeosPolygon
from Processing.utils import read_erddap_data
from AdriaProject.settings import ERDDAP_URL


from Dataset.models import Node, Polygon

from typing import List, Dict, Any, Tuple, Union

from AdriaProject.logger_config import setup_logger

from Processing.utils import download_with_cache_as_csv
from Processing.time_processing import convertToTime, get_season
from Processing.database_operations import is_database_almost_full
from Processing.indicator_manager import getIndicatorQueryUrl, url_is_indicator
from Processing.data_analysis import calculate_trend, operation_before_after_cache, processOperation, packageGraphData


from shapely.geometry import Polygon as ShapelyPolygon, Point as ShapelyPoint # type: ignore

# logger = setup_logger(__name__) 
logger = setup_logger("")



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
    dataset_id,
    adriaclim_timeperiod,
    layer_name,
    date_start,
    date_end,
    lat_lng_obj,
    statistic,
    time_op,
    num_param,
    range_value,
    is_indicator,
    lat_min,
    lat_max,
    lng_min,
    lng_max,
    parametro_agg,
    circle_coords,
):
    start_time = time.time()
    logger.debug("STARTED getDataPolygonNew")

    vertices = [(float(p["lat"]), float(p["lng"])) for p in lat_lng_obj]
    vertices_geos_poly = [(float(p["lng"]), float(p["lat"])) for p in lat_lng_obj]

    shapely_polygon = ShapelyPolygon(vertices)
    shapely_polygon_inverse = ShapelyPolygon(vertices_geos_poly)

    try:
        geos_polygon = GeosPolygon.from_ewkt(shapely_polygon_inverse.wkt)
    except Exception as e:
        logger.error("Error creating GeosPolygon: %s", e)
        return str(e)

    shapely.speedups.enable()
    pol_vertices_str = str(vertices[0][0]).replace(" ", "")
    key_cached = dataset_id + "_" + pol_vertices_str

    cache_result = cache.get(key=key_cached)
    if cache_result is not None:
        logger.debug("CACHE HIT")
        pol_from_cache = json.loads(cache_result)
        dataframe = pd.DataFrame.from_dict(pol_from_cache["dataBeforeOp"]).dropna(how="any")
        dataframe["date_value"] = pd.to_datetime(dataframe["date_value"])
        pol_from_cache["dataPol"] = operation_before_after_cache(dataframe, statistic, time_op)
        # --- FIX: handle multi-column statistics (boxPlot, min_10thPerc_median_90thPerc_max, etc.)
        multi_stats = ("min_mean_max", "min_10thPerc_median_90thPerc_max")
        if statistic not in multi_stats:
            df = pd.DataFrame(pol_from_cache["dataPol"])
            values = df["y"].tolist()
            if len(values) == 1:
                mean = median = std_dev = trend_value = values[0]
            else:
                trend_value = calculate_trend(df["x"].tolist(), df["y"].tolist())
                mean, median, std_dev = df["y"].mean(), df["y"].median(), df["y"].std()

            pol_from_cache.update({
                "mean": mean,
                "median": median,
                "stdev": std_dev,
                "trend_yr": trend_value,
            })
        else:
            # For multi-column statistics, skip computing y
            pol_from_cache.update({
                "mean": None,
                "median": None,
                "stdev": None,
                "trend_yr": None,
            })
        # --- END FIX

        if parametro_agg != "None":
            if pd.isna(pol_from_cache["dataTable"][0][parametro_agg]):
                pol_from_cache["dataTable"][0][parametro_agg] = "Value not defined"
        return pol_from_cache

    logger.debug("CACHE MISS: checking DB")
    polygons = Polygon.objects.filter(
        Q(dataset_id=dataset_id) & Q(coordinate__within=geos_polygon)
    )

    if polygons.exists():
        logger.debug("DB HIT")

        try:
            allData = {"dataTable": []}
            for pol in polygons:
                row = {
                    "time": pol.date_value,
                    "latitude": pol.latitude,
                    "longitude": pol.longitude,
                    layer_name: pol.value_0 if not pd.isna(pol.value_0) else "Value not defined"
                }
                if parametro_agg != "None":
                    row[parametro_agg] = pol.parametro_agg if not pd.isna(pol.parametro_agg) else "Value not defined"
                allData["dataTable"].append(row)

            df = pd.DataFrame([
                model_to_dict(p, fields=[f.name for f in p._meta.fields]) for p in polygons
            ])
            df = df.drop(["coordinate"], axis=1).drop_duplicates(
                subset=["date_value", "latitude", "longitude", "value_0"], keep="first"
            ).dropna(how="all", axis=1)

            allData["dataBeforeOp"] = df.to_dict(orient="records")

            if time_op == "default":
                df["date_value"] = pd.to_datetime(df["date_value"])
                date_value_list = df.drop_duplicates("date_value")
                trend_mean = df.groupby("date_value")["value_0"].mean().tolist()

                values = df["value_0"].tolist()
                if len(values) == 1:
                    trend_value = mean = median = std_dev = values[0]
                else:
                    trend_value = trend_mean[0] if len(trend_mean) == 1 else calculate_trend(date_value_list["date_value"].tolist(), trend_mean, adriaclim_timeperiod)
                    mean, median, std_dev = df["value_0"].mean(), df["value_0"].median(), df["value_0"].std()

                allData.update({
                    "mean": mean,
                    "median": median,
                    "stdev": std_dev,
                    "trend_yr": trend_value,
                })

            cache.set(key=key_cached, value=json.dumps(allData), timeout=43200)
            allData["dataPol"] = operation_before_after_cache(df, statistic, time_op)
            logger.debug("DB TIME: %.2f seconds", time.time() - start_time)
            # --- FIX: validate data structure before return ---
            if not allData.get("dataPol") or not isinstance(allData["dataPol"], list) or len(allData["dataPol"]) == 0:
                logger.warning("[FIX] The data is not compliant → empty or invalid structure detected")
                return {"error": "data_not_compliant"}
            # --- END FIX ---
            return allData
        except Exception as e:
            logger.error("DB processing error: %s", e)
            return str(e)


    # --- DB AND CACHE MISS -> BULK attempt (single call) ---
    logger.debug("DB AND CACHE MISS")

    try:
        # import locali per il blocco BULK
      
        import urllib.request, re, math
        import numpy as np
        from shapely.prepared import prep
        from shapely.geometry import Point, box as shapely_box

        # 1) bounds da shapely
        xmin, ymin, xmax, ymax = shapely_polygon.bounds
        lat_min_f = float(xmin); lat_max_f = float(xmax)
        lon_min_f = float(ymin); lon_max_f = float(ymax)
        if lat_min_f > lat_max_f:
            lat_min_f, lat_max_f = lat_max_f, lat_min_f
        if lon_min_f > lon_max_f:
            lon_min_f, lon_max_f = lon_max_f, lon_min_f
        logger.debug("BBOX shapely (float) -> lat[%.6f, %.6f] lon[%.6f, %.6f]", lat_min_f, lat_max_f, lon_min_f, lon_max_f)

        # 2) # Clamp ONLY for griddap (indicator == "false") via .das
        def _get_axis_bounds_from_das(erddap_url: str, ds_id: str):
            try:
                with urllib.request.urlopen(f"{erddap_url}/griddap/{ds_id}.das", timeout=8) as resp:
                    text = resp.read().decode("utf-8", errors="ignore")
            except Exception:
                return (None, None)
            def _bounds(varname: str):
                m = re.search(rf"{varname}\s*\{{[^}}]*?actual_range\s*([-\d\.Ee+]+)\s*,\s*([-\d\.Ee+]+)", text, re.S)
                if not m:
                    return None
                a = float(m.group(1)); b = float(m.group(2))
                lo, hi = (a, b) if a <= b else (b, a)
                return lo, hi
            return _bounds("latitude"), _bounds("longitude")

        if is_indicator == "false":
            lat_bounds, lon_bounds = _get_axis_bounds_from_das(ERDDAP_URL, dataset_id)
            if lat_bounds:
                lat_lo, lat_hi = lat_bounds
                lat_min_f = max(lat_min_f, lat_lo)
                lat_max_f = min(lat_max_f, lat_hi)
            if lon_bounds:
                lon_lo, lon_hi = lon_bounds
                lon_min_f = max(lon_min_f, lon_lo)
                lon_max_f = min(lon_max_f, lon_hi)
            logger.debug("BBOX clampato (float) -> lat[%.6f, %.6f] lon[%.6f, %.6f]", lat_min_f, lat_max_f, lon_min_f, lon_max_f)

        # 3) Validate area > 0 and convert strings
        if lat_min_f >= lat_max_f or lon_min_f >= lon_max_f:
            raise ValueError("BBOX fuori dall'estensione del dataset dopo clamp")

        latMin  = f"{lat_min_f:.4f}"
        latMax  = f"{lat_max_f:.4f}"
        longMin = f"{lon_min_f:.4f}"
        longMax = f"{lon_max_f:.4f}"
        logger.debug("BBOX finale -> lat[%s,%s] lon[%s,%s]", latMin, latMax, longMin, longMax)

        # 4) Build URL (stride only for griddap)
        if is_indicator == "true":
            bulk_url = url_is_indicator(
                "true",
                True,   # is_graph
                False,  # is_annual
                dataset_id=dataset_id,
                layer_name=layer_name,
                time_start=date_start,
                time_finish=date_end,
                latMin=latMin, latMax=latMax,
                longMin=longMin, longMax=longMax,
            )
        else:
            TIME_STRIDE = 1
            LAT_STRIDE  = 8
            LON_STRIDE  = 8
            bulk_url = url_is_indicator(
                "false",
                False,  # is_graph
                False,  # is_annual
                dataset_id=dataset_id,
                layer_name=layer_name,
                time_start=date_start,
                time_finish=date_end,
                latitude_start=latMin, latitude_end=latMax,
                longitude_start=longMin, longitude_end=longMax,
                num_param=num_param, range_value=range_value,
                time_stride=TIME_STRIDE, lat_stride=LAT_STRIDE, lon_stride=LON_STRIDE,
            )
            logger.info("BULK strides -> time:%s lat:%s lon:%s", TIME_STRIDE, LAT_STRIDE, LON_STRIDE)

        logger.info("Provo BULK URL (bbox): %s", bulk_url)
        df_bulk = read_erddap_data(bulk_url)

        # === CLEAN BULK BLOCK + GEOMETRIC FILTER ===

        from shapely.geometry import Point, box as shapely_box
        import numpy as np

        # Convert columns
        df_bulk["latitude"] = pd.to_numeric(df_bulk["latitude"], errors="coerce")
        df_bulk["longitude"] = pd.to_numeric(df_bulk["longitude"], errors="coerce")
        df_bulk = df_bulk.dropna(subset=["latitude", "longitude"])

        # Check required columns (once, here)
        required_cols = {"time", "latitude", "longitude", layer_name}
        if df_bulk is None or df_bulk.empty or not required_cols.issubset(set(df_bulk.columns)):
            raise ValueError("Bulk ERDDAP empty/invalid schema")

        # Polygon bounding box
        xmin, ymin, xmax, ymax = shapely_polygon.bounds

        # Unique (lat/lon) points in the bulk
        unique_points = df_bulk[["latitude", "longitude"]].drop_duplicates()
        logger.warning(f"[DEBUG FILTER] → VALORI UNICI LAT/LON: {unique_points.to_dict('records')}")

        # Infer grid step
        lat_uni = np.array(sorted(unique_points["latitude"].unique()))
        lon_uni = np.array(sorted(unique_points["longitude"].unique()))

        def _step(arr: np.ndarray):
            if arr.size >= 2:
                diffs = np.diff(arr)
                diffs = diffs[diffs > 0]
                if diffs.size:
                    return float(np.median(diffs))
            return None

        res_lat = _step(lat_uni) or 1.0
        res_lon = _step(lon_uni) or 1.0

        # Half-step + extra margin
        pad_lat = res_lat / 2.0 + 0.25
        pad_lon = res_lon / 2.0 + 0.25

        logger.warning("[DEBUG FILTER] step_lat=%.3f step_lon=%.3f pad_lat=%.3f pad_lon=%.3f",
                    res_lat, res_lon, pad_lat, pad_lon)

        if len(unique_points) == 1:
            # Single-cell-center dataset
            lat = float(unique_points.iloc[0]["latitude"])
            lon = float(unique_points.iloc[0]["longitude"])

            # Estimated cell with resolution + margin
            cell = shapely_box(lon - pad_lon, lat - pad_lat, lon + pad_lon, lat + pad_lat)

            if cell.intersects(shapely_polygon_inverse):
                df_bulk_filtered = df_bulk
                logger.warning("[DEBUG FILTER] Punto unico → cella (%.2fx%.2f + margine) interseca → uso BULK",
                            res_lat, res_lon)
            else:
                # Force usage: if data exists anyway, use it
                if not df_bulk.empty:
                    df_bulk_filtered = df_bulk
                    logger.warning("[DEBUG FILTER] Punto unico → cella NON interseca, ma dati presenti → forzato uso BULK")
                else:
                    logger.warning("[DEBUG FILTER] Punto unico: nessun dato → fallback")
                    raise ValueError("bulk_filter_empty")

        else:
            # Gridded dataset: keep only cells intersecting the polygon
            keep = set()
            for lat, lon in unique_points.itertuples(index=False):
                lat = float(lat); lon = float(lon)
                cell = shapely_box(lon - pad_lon, lat - pad_lat, lon + pad_lon, lat + pad_lat)
                if cell.intersects(shapely_polygon_inverse):
                    keep.add((lat, lon))
            if not keep:
                logger.warning("[DEBUG FILTER] Nessuna cella interseca il poligono — fallback")
                raise ValueError("bulk_filter_empty")


            # Filter dataframe to kept (lat, lon) only
            df_bulk["lat_lng_key"] = list(zip(df_bulk["latitude"].astype(float), df_bulk["longitude"].astype(float)))
            df_bulk_filtered = df_bulk[df_bulk["lat_lng_key"].isin(keep)].copy()
            df_bulk_filtered.drop(columns=["lat_lng_key"], inplace=True)

        logger.warning(f"[DEBUG FILTER] BULK post-filter shape: {df_bulk_filtered.shape}")
        df_bulk = df_bulk_filtered

        # === END CLEAN BULK BLOCK + GEOMETRIC FILTER ===


        # ===== VECTOR BULK (no loop, no DB, sanitize) =====
        def _json_sanitize(obj):
            if isinstance(obj, dict):
                return {k: _json_sanitize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_json_sanitize(v) for v in obj]
            if isinstance(obj, float):
                if math.isnan(obj) or math.isinf(obj):
                    return None
                return obj
            return obj

        # 1) Working dataframe
        cols_base = ["time", "latitude", "longitude", layer_name]
        df_work = df_bulk[cols_base].copy()
        has_param_agg = (parametro_agg != "None") and (parametro_agg in df_bulk.columns)
        if has_param_agg:
            df_work[parametro_agg] = df_bulk[parametro_agg]

        # 2) df_polygon (dataBeforeOp / dataPol)
        df_polygon = pd.DataFrame({
            "date_value": df_work["time"],
            "lat_lng": "(" + df_work["latitude"].astype(str) + "," + df_work["longitude"].astype(str) + ")",
            "value_0": pd.to_numeric(df_work[layer_name], errors="coerce"),
        })
        logger.warning("[DEBUG CHECK] time_op=%s, statistic=%s, righe df_polygon=%d", time_op, statistic, len(df_polygon))
        logger.warning("[DEBUG CHECK] date_value sample: %s", df_polygon["date_value"].head().tolist())
        logger.warning("[DEBUG CHECK] value_0 sample: %s", df_polygon["value_0"].head().tolist())
        df_polygon = df_polygon.drop_duplicates(
            subset=["date_value", "lat_lng", "value_0"], keep="first"
        ).dropna(how="all", axis=1)

        allData = {}
        allData["dataBeforeOp"] = df_polygon.to_dict(orient="records")

        # 3) stats
        if time_op == "default":
            df_tmp = df_polygon.copy()
            df_tmp["date_value"] = pd.to_datetime(df_tmp["date_value"], errors="coerce")
            df_tmp = df_tmp.dropna(subset=["date_value"])
            s_vals = df_tmp["value_0"]
            mean    = float(s_vals.mean(skipna=True)) if not s_vals.empty else None
            median  = float(s_vals.median(skipna=True)) if not s_vals.empty else None
            std_dev = float(s_vals.std(skipna=True)) if not s_vals.empty else None
            g = df_tmp.groupby("date_value")["value_0"].mean()
            if g.size <= 1:
                trend_value = float(g.iloc[0]) if g.size == 1 else None
            else:
                trend_value = calculate_trend(g.index.tolist(), g.values.tolist(), timeperiod=adriaclim_timeperiod)
            allData.update({
                "mean": mean,
                "median": median,
                "stdev": std_dev,
                "trend_yr": trend_value,
            })

        # 4) dataTable (limit table only for heavy JSON payloads)
        df_table = df_work[["time", "latitude", "longitude", layer_name]].copy()
        df_table[layer_name] = df_table[layer_name].where(pd.notnull(df_table[layer_name]), "Value not defined")
        if has_param_agg:
            df_table[parametro_agg] = df_work[parametro_agg].where(pd.notnull(df_work[parametro_agg]), "Value not defined")

        DATA_TABLE_MAX_ROWS = 8000
        total_rows = len(df_table)
        if total_rows > DATA_TABLE_MAX_ROWS:
            df_table = df_table.iloc[:DATA_TABLE_MAX_ROWS]
            allData["dataTable_truncated"] = True
            allData["dataTable_total_rows"] = int(total_rows)

        allData["dataTable"] = df_table.to_dict(orient="records")

        # 5) dataPol + cache (with datetime normalization before the operation)
        df_for_op = df_polygon.copy()
        df_for_op["date_value"] = pd.to_datetime(df_for_op["date_value"], utc=True, errors="coerce").dt.tz_localize(None)

        allData["dataPol"] = operation_before_after_cache(df_for_op, statistic, time_op)

        allData_sanit = _json_sanitize(allData)
        cache.set(key=key_cached, value=json.dumps(allData_sanit), timeout=43200)

        logger.debug("Completed getDataPolygonNew (BULK/VECT) in %.2f seconds", time.time() - start_time)
        return allData_sanit


    except Exception as e_bulk:
        logger.warning("BULK fallito: %s — procedo con fallback per-punto", e_bulk)

    # ===== Per-point fallback (original code) =====

    xmin, ymin, xmax, ymax = shapely_polygon.bounds
    circ = shapely_polygon.length
    area = shapely_polygon.area

    step = 0.3 if area > 2 else 0.2 if area > 1 else 0.1

    points_inside_polygon = []
    try:
        if circle_coords:
            for coord in circle_coords:
                point = ShapelyPoint(coord["lat"], coord["lng"])
                if point.within(shapely_polygon):
                    points_inside_polygon.append((coord["lat"], coord["lng"]))
        else:
            for x in range(int(xmin / step), int(xmax / step)):
                for y in range(int(ymin / step), int(ymax / step)):
                    point = ShapelyPoint(x * step, y * step)
                    if point.within(shapely_polygon):
                        points_inside_polygon.append((x * step, y * step))
    except Exception as e:
        logger.error("Polygon generation error: %s", e)
        return str(e)

    logger.debug("POINTS INSIDE POLYGON: %d", len(points_inside_polygon))
    df_polygon = pd.DataFrame(columns=["date_value", "lat_lng", "value_0"])
    dataTable = []
    i = 0

    total_elapsed_time = 0

    for latlng in points_inside_polygon:
        try:
            logger.info("Inizio download per punto: %s", latlng)

            start_time = time.time()  # Start time

            url = url_is_indicator(
                is_indicator,
                True,
                is_indicator != "false",
                boolNostraFunzione = False,
                dataset_id=dataset_id,
                layer_name=layer_name,
                time_start=date_start,
                time_finish=date_end,
                latitude=str(latlng[0]),
                longitude=str(latlng[1]),
                num_parameters=num_param,
                range_value=range_value,
            )
            df = read_erddap_data(url)

            end_time = time.time()  # End time
            elapsed_time = end_time - start_time
            total_elapsed_time += elapsed_time

            logger.info("Completato per %s in %.2f secondi", latlng, elapsed_time)

        except Exception as e:
            logger.error("Error downloading data at point %s: %s", latlng, e)
            continue

        logger.info("Tempo totale per tutti i punti: %.2f secondi", total_elapsed_time)

        try:
            for index, row in enumerate(df.to_dict(orient="records")):
                dat_tab = {
                    "time": convertToTime(row["time"]) if index > 0 else row["time"],
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    layer_name: row[layer_name] if not pd.isna(row[layer_name]) else "Value not defined"
                }

                if parametro_agg != "None":
                    dat_tab[parametro_agg] = row[parametro_agg] if not pd.isna(row[parametro_agg]) else "Value not defined"

                dataTable.append(dat_tab)

                df_polygon.loc[i] = [
                    row["time"],
                    f"({row['latitude']},{row['longitude']})",
                    row[layer_name],
                ]

                defaults = {
                    "value_0": float(row[layer_name]),
                    "pol_vertices_str": pol_vertices_str
                }

                if parametro_agg != "None":
                    defaults["parametro_agg"] = row[parametro_agg]

                if not is_database_almost_full():
                    try:
                        Polygon.objects.update_or_create(
                            dataset_id=Node.objects.get(id=dataset_id),
                            date_value=convertToTime(row["time"]),
                            latitude=float(row["latitude"]),
                            longitude=float(row["longitude"]),
                            coordinate=GEOSPoint(float(row["longitude"]), float(row["latitude"])),
                            defaults=defaults,
                        )
                    except Exception as e:
                        logger.warning("DB save skipped for point %s: %s", latlng, e)
        except Exception as e:
            logger.error("Error parsing data at point %s: %s", latlng, e)
            i += 1
                
        except Exception as e:
            logger.error("Data processing exception: %s", e)
            return str(e)

    try:
        df_polygon = df_polygon.drop_duplicates(
            subset=["date_value", "lat_lng", "value_0"], keep="first"
        ).dropna(how="all", axis=1)

        allData = {}
        df_polygon["value_0"] = pd.to_numeric(df_polygon["value_0"], errors='coerce')
        allData["dataBeforeOp"] = df_polygon.to_dict(orient="records")

        if time_op == "default":
            df_polygon["date_value"] = pd.to_datetime(df_polygon["date_value"])
            date_value_to_list = df_polygon.drop_duplicates(subset="date_value", keep="first")
            trend_value_mean = df_polygon.groupby("date_value")["value_0"].mean().tolist()
            pol_values = df_polygon["value_0"].tolist()

            if len(pol_values) == 1:
                trend_value = mean = median = std_dev = pol_values[0]
            else:
                if len(trend_value_mean) == 1:
                    trend_value = trend_value_mean[0]
                else:
                    trend_value = calculate_trend(
                        date_value_to_list["date_value"].tolist(),
                        trend_value_mean,
                        timeperiod=adriaclim_timeperiod,
                    )
                mean = df_polygon["value_0"].mean()
                median = df_polygon["value_0"].median()
                std_dev = df_polygon["value_0"].std()

            allData.update({
                "mean": mean,
                "median": median,
                "stdev": std_dev,
                "trend_yr": trend_value,
            })

        data_table_list = []
        for item in dataTable:
            data = {
                "time": item["time"],
                "latitude": item["latitude"],
                "longitude": item["longitude"],
                layer_name: item[layer_name],
            }
            if parametro_agg != "None":
                data[parametro_agg] = item[parametro_agg]
            data_table_list.append(data)

        allData["dataTable"] = data_table_list
        cache.set(key=key_cached, value=json.dumps(allData), timeout=43200)

        df_for_op = df_polygon.copy()
        df_for_op["date_value"] = pd.to_datetime(df_for_op["date_value"], utc=True, errors="coerce").dt.tz_localize(None)
        allData["dataPol"] = operation_before_after_cache(df_for_op, statistic, time_op)

       # Final DataFrame log
        try:
            logger.warning("[DEBUG FINAL] df_bulk finale → shape: %s", df_bulk.shape)
            logger.warning("[DEBUG FINAL] df_bulk finale → valori:\n%s", df_bulk[[ "time", layer_name, "latitude", "longitude" ]].to_string(index=False))
        except Exception as e:
            logger.error("Errore nel log finale df_bulk: %s", e)

        logger.debug("Completed getDataPolygonNew in %.2f seconds", time.time() - start_time)
        # --- FIX: validate data structure before return + fallback ---
        if not allData.get("dataPol") or not isinstance(allData["dataPol"], list) or len(allData["dataPol"]) == 0:
            logger.warning("[FIX] The data is not compliant → empty or invalid structure detected")

            # Automatic fallback attempt: recompute in 'default' mode
            try:
                if time_op != "default":
                    logger.warning("[FIX] Retrying operation_before_after_cache with time_op='default'")
                    df_retry = pd.DataFrame(allData.get("dataBeforeOp", []))
                    if not df_retry.empty:
                        allData["dataPol"] = operation_before_after_cache(df_retry, statistic, "default")
                        if allData["dataPol"]:
                            logger.warning("[FIX] Fallback 'default' riuscito, restituisco dati validi")
                            return allData
            except Exception as e:
                logger.error("[FIX] Fallback default fallito: %s", e)

            # If the fallback also fails
            return {"error": "data_not_compliant"}
        # --- END FIX ---
        return allData

    except Exception as e:
        logger.error("Final aggregation error: %s", e)
        return str(e)


x = 500000
months = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}
seasons = {
    0: "Winter",
    1: "Spring",
    2: "Summer",
    3: "Autumn",
}

season_trend = {
    "01": "Winter",
    "02": "Spring",
    "03": "Summer",
    "04": "Autumn",
}

def getDataGraphicGeneric(
    dataset_id,
    adriaclim_timeperiod,
    layer_name,
    time_start,
    time_finish,
    latitude,
    longitude,
    num_parameters,
    range_value,
    is_indicator,
    lat_start,
    long_start,
    lat_end,
    long_end,
    **kwargs
):
    
    try:
        onlyone = 0
        cache = 0
        if "context" in kwargs and kwargs["context"] == "one":
            onlyone = 1
        if "cache" in kwargs and kwargs["cache"] == "yes":
            cache = 1
        onlylat = None
        onlylong = None
        operation = None

        if "operation" in kwargs and kwargs["operation"] != "":
            operation = kwargs["operation"]

        if lat_start == "no":
            lat_start = latitude
        if lat_end == "no":
            lat_end = latitude
        if long_start == "no":
            long_start = longitude
        if long_end == "no":
            long_end = longitude
        url = getIndicatorQueryUrl(
            dataset_id,
            False,
            False,
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

        if cache == 1:
            url = download_with_cache_as_csv(url)
        if url == "fuoriWms":
            return url
        try:
            df = read_erddap_data(url)

        except Exception as e:
            return "fuoriWms"
        if df[layer_name] is not None:
            unit = df[layer_name][0]
        else:
            unit = layer_name
        unit = ""
        df = df.iloc[1:, :]
        n_values = len(df)
        allData = []
        values = []
        dates = []
        layerName = []
        lats = []
        longs = []
        i = 0
        if n_values <= x:  # all the data
            for index, row in df.iterrows():
                if onlyone == 1 and onlylat is None:
                    onlylat = row["latitude"]
                    onlylong = row["longitude"]
                if (
                    row[layer_name] == row[layer_name]
                    and row[layer_name] != "NaN"
                    and (
                        onlyone == 0
                        or (onlylat == row["latitude"] and onlylong == row["longitude"])
                    )
                ):
                    lats.insert(i, row["latitude"])
                    longs.insert(i, row["longitude"])
                    layerName.insert(i, layer_name)
                    values.insert(i, float(row[layer_name]))
                    dates.insert(i, row["time"])
                    i += 1
        else:  # one every nvalues/x data
            every_nth_rows = int(n_values / x)
            df = df[::every_nth_rows]
            for index, row in df.iterrows():
                if (
                    row[layer_name] == row[layer_name]
                    and row[layer_name] != "NaN"
                    and (
                        onlyone == 0
                        or (onlylat == row["latitude"] and onlylong == row["longitude"])
                    )
                ):
                    lats.insert(i, row["latitude"])
                    longs.insert(i, row["longitude"])
                    layerName.insert(i, layer_name)
                    values.insert(i, float(row[layer_name]))
                    dates.insert(i, row["time"])
                    i += 1
        allData = [values, dates, unit, layerName, lats, longs]
        if operation is None:
            return allData
        else:
            try:
                output = None
                if "output" in kwargs:
                    output = kwargs["output"]

                return packageGraphData(
                    processOperation(operation, values, dates, unit, layerName, lats, longs),
                    output=output,
                    operation=operation,
                    adriaclim_timeperiod=adriaclim_timeperiod,
                )
            except Exception as e:
                return str(e)
    except Exception as e:
        return str(e)


def check_dates_format_trend(dates):
    if type(dates[0]) is str:
        if dates[0].startswith("0000"):
                #annual month by month point
            try:
                dates = [dt.datetime.strptime(d.replace("0000","2000"), "%Y-%m-%dT%H:%M:%SZ") for d in dates]
            except Exception as e: 
                return 'Invalid date format: '+ str(e)
                # dates = [dt.datetime.strptime(d.replace('0000',"2000"), "%Y-%m-%d") for d in dates]
        elif len(dates[0].split("-")) == 2: 
                 #annual day by day point
            for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%SZ', '%d/%m/%Y'):
                try:
                    dates = [dt.datetime.strptime("2000-" + d, fmt) for d in dates]
                except ValueError:
                    pass
        elif dates[0] == "Jan":
                #annual month by month polygon
            create_dates = []
            for d in dates:
            #annual month by month polygon
                for key, val in months.items():
                    if val ==  d:
                        month_number = key
                        create_dates.append(dt.datetime.strptime("2000-01-" + str(month_number), "%Y-%d-%m"))

            dates = list(create_dates)
        elif dates[0] == "Winter" or dates[0] == "Spring" or dates[0] == "Summer" or dates[0] == "Autumn":
            #annual season by season polygon
            create_dates = []
            for d in dates:
                for key, val in season_trend.items():
                    if val == d:
                        season_number = key
                        create_dates.append(dt.datetime.strptime("2000-01-" + str(season_number), "%Y-%d-%m"))
            
            dates = list(create_dates)
        else:
            for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%SZ', '%d/%m/%Y'):
                try:
                    dates = [dt.datetime.strptime(str(d), fmt) for d in dates]
                except ValueError:
                    pass
             
    return dates

def subtract_mean_trend(dates,values,timeperiod):
    #creation of a dataFrame with dates and values
    df_mean_trend = pd.DataFrame({"date":dates,"value":values})
    df_mean_trend["date"] = pd.to_datetime(df_mean_trend["date"])
    if timeperiod == "monthly":
        groupby_col = df_mean_trend["date"].dt.month
    if timeperiod == "daily":
        df_mean_trend["day_month"] = df_mean_trend["date"].dt.strftime('%m-%d')
        groupby_col = df_mean_trend["day_month"]
    if timeperiod == "seasonal":
        df_mean_trend["season"] = df_mean_trend["date"].apply(get_season)
        groupby_col = df_mean_trend["season"]
    
    # Group them by the dataset time scale and compute the average
    df_mean_trend["mean_timeperiod"] = df_mean_trend.groupby(groupby_col)["value"].transform("mean")

    # Subtract the computed mean from each date (month, season, or day)
    df_mean_trend["value"] = df_mean_trend["value"] - df_mean_trend["mean_timeperiod"]

    return df_mean_trend["value"].values
