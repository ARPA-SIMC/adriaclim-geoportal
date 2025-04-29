import time
import datetime as dt
import pandas as pd
import json
import numpy as np
from django.db.models import Q
from django.contrib.gis.geos import Polygon as GeosPolygon
from django.contrib.gis.geos import Point
from shapely.geometry import Polygon as ShapelyPolygon, Point as ShapelyPoint
import shapely.speedups
from django.core.cache import cache
from Dataset.models import Polygon, Node
from myFunctions.data_analysis import calculate_trend, operation_before_after_cache, processOperation, packageGraphData
from myFunctions.utils import download_with_cache_as_csv
# from myFunctions.time_processing import convertToTime 
from myFunctions.indicator_manager import getIndicatorQueryUrl
# from myFunctions.database_operations import is_database_almost_full


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
    print("STARTED getDataPolygonNew!")

    vertices = [(float(lat_lng["lat"]), float(lat_lng["lng"])) for lat_lng in lat_lng_obj]
    vertices_geos_poly = [(float(lat_lng["lng"]), float(lat_lng["lat"])) for lat_lng in lat_lng_obj]

    shapely_polygon = ShapelyPolygon(vertices)
    shapely_polygon_inverse = ShapelyPolygon(vertices_geos_poly)
    shapely.speedups.enable()

    try:
        geos_polygon = GeosPolygon.from_ewkt(shapely_polygon_inverse.wkt)
    except Exception as e:
        print("Error creating GEOS Polygon:", e)
        return str(e)

    pol_vertices_str = str(vertices[0][0]).replace(" ", "")
    key_cached = dataset_id + "_" + pol_vertices_str

    cache_result = cache.get(key=key_cached)
    
    if cache_result is not None:
        print("CACHE HIT!")
        pol_from_cache = json.loads(cache_result)
        df = pd.DataFrame.from_dict(pol_from_cache["dataBeforeOp"]).dropna()
        df["date_value"] = pd.to_datetime(df["date_value"])
        pol_from_cache["dataPol"] = operation_before_after_cache(df, statistic, time_op)

        values = pol_from_cache["dataPol"]["y"] if "y" in pol_from_cache["dataPol"] else []
        if values:
            pol_from_cache["mean"] = np.mean(values)
            pol_from_cache["median"] = np.median(values)
            pol_from_cache["stdev"] = np.std(values)
            pol_from_cache["trend_yr"] = calculate_trend(df["date_value"].tolist(), values)
        return pol_from_cache

    print("CACHE MISS, checking DB...")
    polygons = Polygon.objects.filter(dataset_id=dataset_id, coordinate__within=geos_polygon)
    
    if polygons.exists():
        try:
            print("DB HIT!")
            allData = {"dataTable": []}

            for pol in polygons:
                entry = {
                    "time": pol.date_value,
                    "latitude": pol.latitude,
                    "longitude": pol.longitude,
                    layer_name: pol.value_0 if not pd.isna(pol.value_0) else "Value not defined"
                }
                if parametro_agg != "None":
                    entry[parametro_agg] = pol.parametro_agg if not pd.isna(pol.parametro_agg) else "Value not defined"
                allData["dataTable"].append(entry)

            df = pd.DataFrame(
                [p.__dict__ for p in polygons]
            ).drop(columns=["_state", "coordinate"], errors='ignore').drop_duplicates()

            allData["dataBeforeOp"] = df.to_dict(orient="records")
            df["date_value"] = pd.to_datetime(df["date_value"])

            if time_op == "default":
                values = df["value_0"].tolist()
                if len(values) > 1:
                    trend_value = calculate_trend(df["date_value"].tolist(), values, timeperiod=adriaclim_timeperiod)
                else:
                    trend_value = values[0] if values else 0
                allData["mean"] = np.mean(values)
                allData["median"] = np.median(values)
                allData["stdev"] = np.std(values)
                allData["trend_yr"] = trend_value

            cache.set(key_cached, json.dumps(allData), timeout=43200)
            allData["dataPol"] = operation_before_after_cache(df, statistic, time_op)

            print("DB TIME: {:.2f} seconds".format(time.time() - start_time))
            return allData

        except Exception as e:
            print("Error during DB handling:", e)
            return str(e)

    else:
        print("NO CACHE, NO DB! Fetching external data...")
        return "External data fetching not yet implemented here"
    
    

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
        x = 1000  # Campionamento massimo di 1000 punti
        onlyone = 0
        use_cache = 0

        if kwargs.get("context") == "one":
            onlyone = 1
        if kwargs.get("cache") == "yes":
            use_cache = 1

        operation = kwargs.get("operation")
        output = kwargs.get("output")

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
            print("Error reading CSV:", e)
            return "fuoriWms"

        if df.empty or layer_name not in df.columns:
            return "fuoriWms"

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

        if n_values <= x:  # All data
            df_iter = df.iterrows()
        else:  # One point every n
            every_nth = int(n_values / x)
            df_iter = df[::every_nth].iterrows()

        onlylat = onlylong = None

        for _, row in df_iter:
            if onlyone and onlylat is None:
                onlylat = row["latitude"]
                onlylong = row["longitude"]

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
                i += 1

        allData = [values, dates, unit, layerName, lats, longs]

        if operation is None:
            return allData
        else:
            try:
                processed = processOperation(operation, values, dates, unit, layerName, lats, longs)
                packaged = packageGraphData(processed, output=output, operation=operation, adriaclim_timeperiod=adriaclim_timeperiod)
                return packaged
            except Exception as e:
                print("Error in processOperation or packageGraphData:", e)
                return str(e)

    except Exception as e:
        print("General exception in getDataGraphicGeneric:", e)
        return str(e)
    




