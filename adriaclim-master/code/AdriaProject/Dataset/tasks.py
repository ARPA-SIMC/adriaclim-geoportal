import time
import json
import pandas as pd
import numpy as np
from django.db.models import Q
from django.core.cache import cache
from django.contrib.gis.geos import Point, Polygon as GeosPolygon
from shapely.geometry import Point as ShapelyPoint, Polygon as ShapelyPolygon
import shapely.speedups
from django.forms import model_to_dict
from celery import shared_task
import logging

from Dataset.models import Node, Polygon
from myFunctions.data_analysis import operation_before_after_cache, calculate_trend
from myFunctions.indicator_manager import url_is_indicator
from myFunctions.time_processing import convertToTime
from myFunctions.database_operations import is_database_almost_full

# ✅ Configura il logger
logger = logging.getLogger(__name__)

@shared_task(bind=True)
def task_get_data_polygon(self, request_data):
    try:
        dataset = request_data["dataset"]
        dataset_id = dataset["id"]
        date_start = dataset["time_start"]
        date_end = dataset["time_end"]
        layer_name = request_data["selVar"]
        adriaclim_timeperiod = dataset["adriaclim_timeperiod"]
        range_value = str(request_data["range"])
        num_param = dataset["dimensions"]
        parametro_agg = str(request_data["parametro_agg"])
        lat_min = dataset["lat_min"]
        lat_max = dataset["lat_max"]
        lng_min = dataset["lng_min"]
        lng_max = dataset["lng_max"]
        time_op = request_data["operation"]
        statistic = request_data["statistic"]
        circle_coords = request_data["circleCoords"]
        lat_lng_obj = request_data["latLngObj"]
        is_indicator = request_data["isIndicator"]

        start_time = time.time()
        logger.info("Started getDataPolygonNew")

        vertices = [(float(p["lat"]), float(p["lng"])) for p in lat_lng_obj]
        vertices_geos_poly = [(float(p["lng"]), float(p["lat"])) for p in lat_lng_obj]

        shapely_polygon = ShapelyPolygon(vertices)
        shapely_polygon_inverse = ShapelyPolygon(vertices_geos_poly)
        shapely.speedups.enable()

        try:
            geos_polygon = GeosPolygon.from_ewkt(shapely_polygon_inverse.wkt)
        except Exception as e:
            logger.error("Error creating GEOS polygon", exc_info=e)
            return str(e)

        pol_vertices_str = str(vertices[0][0]).replace(" ", "")
        key_cached = f"{dataset_id}_{pol_vertices_str}"

        self.update_state(state='PROGRESS', meta={'current': 10, 'total': 100})
        cache_result = cache.get(key_cached)

        if cache_result:
            logger.info("CACHE HIT!")
            pol_from_cache = json.loads(cache_result)
            df = pd.DataFrame.from_dict(pol_from_cache["dataBeforeOp"]).dropna(how="any")
            df["date_value"] = pd.to_datetime(df["date_value"])
            pol_from_cache["dataPol"] = operation_before_after_cache(df, statistic, time_op)

            if parametro_agg != "None":
                pol_from_cache["dataTable"][0][parametro_agg] = (
                    pol_from_cache["dataTable"][0].get(parametro_agg, "Value not defined")
                )

            self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100})
            return pol_from_cache

        logger.info("CACHE MISS, checking DB...")
        polygons = Polygon.objects.filter(dataset_id=dataset_id, coordinate__within=geos_polygon)

        if polygons.exists():
            logger.info("DB HIT!")
            self.update_state(state='PROGRESS', meta={'current': 80, 'total': 100})

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

            df = pd.DataFrame([
                model_to_dict(p, fields=[f.name for f in p._meta.fields])
                for p in polygons
            ]).drop(columns=["coordinate"], errors="ignore").drop_duplicates()

            df["date_value"] = pd.to_datetime(df["date_value"])
            allData["dataBeforeOp"] = df.to_dict(orient="records")

            if time_op == "default":
                values = df["value_0"].tolist()
                trend_value = calculate_trend(df["date_value"].tolist(), values, timeperiod=adriaclim_timeperiod) if len(values) > 1 else (values[0] if values else 0)
                allData.update({
                    "mean": np.mean(values),
                    "median": np.median(values),
                    "stdev": np.std(values),
                    "trend_yr": trend_value,
                })

            cache.set(key_cached, json.dumps(allData), timeout=43200)
            allData["dataPol"] = operation_before_after_cache(df, statistic, time_op)

            logger.info(f"DB TIME: {time.time() - start_time:.2f} seconds")
            self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100})
            return allData

        logger.info("CACHE MISS AND DB MISS: External fetch not yet implemented")
        return "External fetch not yet implemented"

    except Exception as e:
        logger.error("Unexpected error in task_get_data_polygon", exc_info=e)
        return str(e)
