import time
import json
import numpy as np
import pandas as pd
import shapely.speedups

from celery import shared_task

from django.db.models import Q
from django.core.cache import cache
from django.forms import model_to_dict
from django.contrib.gis.geos import Point, Polygon as GeosPolygon

from Processing.time_processing import convertToTime
from Processing.indicator_manager import url_is_indicator
from Processing.utils import read_erddap_data

from Processing.database_operations import is_database_almost_full
from Processing.data_analysis import operation_before_after_cache, calculate_trend

from AdriaProject.logger_config import setup_logger

from Dataset.models import Node, Polygon
from Dataset.geospatial_processing import getDataPolygonNew

from shapely.geometry import Point as ShapelyPoint, Polygon as ShapelyPolygon




logger = setup_logger(__name__)


# @shared_task(bind=True)
# def task_get_data_polygon(self,request_data):
#     try:
        
#         dataset = request_data["dataset"]
#         dataset_id = dataset["id"]
#         date_start = dataset["time_start"]
#         date_start = request_data["dataset"]['time_start']
#         date_end = request_data["dataset"]['time_end']
#         layer_name = request_data['selVar']
#         adriaclim_timeperiod = request_data['dataset']['adriaclim_timeperiod']
#         range_value = str(request_data['range'])
#         num_param = request_data["dataset"]['dimensions']
#         parametro_agg = str(request_data['parametro_agg'])
#         lat_min = request_data["dataset"]['lat_min']
#         lat_max = request_data["dataset"]['lat_max']
#         lng_min = request_data["dataset"]['lng_min']
#         lng_max = request_data["dataset"]['lng_max']
#         time_op = request_data['operation']
#         statistic = request_data['statistic']
#         circle_coords = request_data['circleCoords']
#         lat_lng_obj = request_data['latLngObj']
#         is_indicator = request_data['isIndicator']
#         result = getDataPolygonNew(
#         dataset_id=dataset_id,
#         adriaclim_timeperiod=adriaclim_timeperiod,
#         layer_name=layer_name,
#         date_start=date_start,
#         date_end=date_end,
#         lat_lng_obj=lat_lng_obj,
#         statistic=statistic,
#         time_op=time_op,
#         num_param=num_param,
#         range_value=range_value,
#         is_indicator=is_indicator,
#         lat_min=lat_min,
#         lat_max=lat_max,
#         lng_min=lng_min,
#         lng_max=lng_max,
#         parametro_agg=parametro_agg,
#         circle_coords=circle_coords
#         )
#         start_time = time.time()
#         vertices = []
#         vertices_geos_poly = []

#         for lat_lng in lat_lng_obj:
#             vertices.append((float(lat_lng["lat"]), float(lat_lng["lng"])))
#             vertices_geos_poly.append((float(lat_lng["lng"]), float(lat_lng["lat"])))

#         shapely_polygon = ShapelyPolygon(vertices)
#         shapely_polygon_inverse = ShapelyPolygon(vertices_geos_poly)
    
#         try:
#             geos_polygon = GeosPolygon.from_ewkt(shapely_polygon_inverse.wkt)
#         except Exception as e:
#             return str(e)
    
#         shapely.speedups.enable()
#         pol_vertices_str = str(vertices[0][0]).replace(" ", "")
#         key_cached = dataset_id + "_" + pol_vertices_str # Cache key
#         current = 10
#         total = 100
#         self.update_state(state='PROGRESS',
#                             meta={'current': current, 'total': total})
#         xmin = None
#         ymin = None
#         xmax = None
#         ymax = None
#         area = None
#         circ = None

#         cache_result = cache.get(key=key_cached)
#         if cache_result is not None:
#             pol_from_cache = json.loads(cache_result)
#             dataframe_from_dict = pd.DataFrame.from_dict(pol_from_cache["dataBeforeOp"])
#             dataframe_from_dict = dataframe_from_dict.dropna(how="any")
#             dataframe_from_dict["date_value"] = pd.to_datetime(dataframe_from_dict["date_value"])
#             pol_from_cache["dataPol"] = operation_before_after_cache(dataframe_from_dict,statistic,time_op)
#             if parametro_agg != "None":
#                 pol_from_cache["dataTable"][0][parametro_agg] = (
#                     pol_from_cache["dataTable"][0][parametro_agg]
#                     if not pd.isna(pol_from_cache["dataTable"][0][parametro_agg])
#                     else "Value not defined"
#                     )
            
#             current = 100
#             self.update_state(state='PROGRESS',
#                             meta={'current': current, 'total': total})
#             return pol_from_cache

#         else:

#             polygons = Polygon.objects.filter(
#                 Q(dataset_id=dataset_id) & Q(coordinate__within=(geos_polygon)))
#             if polygons.exists():
#                  # Here we are in the case where the polygon exists for this dataset ID and contains points within the selected polygon
#                 try:
#                     current = 80
#                     self.update_state(state='PROGRESS',
#                                 meta={'current': current, 'total': total})
#                     allData = {}
#                     data_table_list = []
#                     for pol in polygons:
#                         # Check whether this dataset point is inside the selected polygon
#                         # Inside the selected polygon 
#                         data_table = {}
#                         data_table["time"] = pol.date_value
#                         data_table["latitude"] = pol.latitude
#                         data_table["longitude"] = pol.longitude
#                         data_table[layer_name] = pol.value_0 if not pd.isna(pol.value_0) else "Value not defined"
                        
#                         if parametro_agg != "None":
#                             data_table[parametro_agg] = pol.parametro_agg if not pd.isna(pol.parametro_agg) else "Value not defined"
#                         data_table_list.append(data_table)
#                     allData[
#                         "dataTable"
#                     ] = data_table_list  

#                     df_polygon_model = pd.DataFrame(
#                         [
#                             model_to_dict(p, fields=[field.name for field in p._meta.fields])
#                             for p in polygons
#                         ]
#                     )
#                     df_polygon_model = df_polygon_model.drop("coordinate",axis=1)
#                     df_polygon_model = df_polygon_model.drop_duplicates(
#                         subset=["date_value", "latitude", "longitude", "value_0"], keep="first"
#                     )
#                     df_polygon_model = df_polygon_model.dropna(how="all", axis=1)
#                     allData["dataBeforeOp"] = df_polygon_model.to_dict(orient="records")

#                     if time_op == "default":
#                         date_value_to_list = df_polygon_model.copy()
#                         date_value_to_list = date_value_to_list.drop_duplicates(subset="date_value",keep="first")
#                         date_value_to_list["date_value"] = pd.to_datetime(date_value_to_list["date_value"])

#                         # Apply the operation based on the values of operation and time_op
#                         df_polygon_model["date_value"] = pd.to_datetime(df_polygon_model["date_value"])

#                         pol_from_db_values = df_polygon_model["value_0"].tolist()
#                         trend_value_mean = df_polygon_model.groupby("date_value")["value_0"].mean().tolist()
#                         if len(pol_from_db_values) == 1:
#                             mean = pol_from_db_values[0]
#                             median = pol_from_db_values[0]
#                             std_dev = pol_from_db_values[0]
#                             trend_value = pol_from_db_values[0]
#                         else:
#                             if len(trend_value_mean) == 1:
#                                 trend_value = trend_value_mean[0]
#                             else:
#                                 trend_value = calculate_trend(date_value_to_list["date_value"].tolist(),trend_value_mean,timeperiod=adriaclim_timeperiod)
                                
#                             mean = df_polygon_model["value_0"].mean()
#                             median = df_polygon_model["value_0"].median()
#                             std_dev = df_polygon_model["value_0"].std()
                        
#                         allData["mean"] = mean
#                         allData["median"] = median
#                         allData["stdev"] = std_dev
#                         allData["trend_yr"] = trend_value
                    
#                     cache.set(key=key_cached,value=json.dumps(allData),timeout=43200) # Store it in the cache for 12 hours
#                     allData["dataPol"] = operation_before_after_cache(
#                         df_polygon_model, statistic, time_op
#                     )
#                     current = 100
#                     self.update_state(state='PROGRESS',
#                             meta={'current': current, 'total': total})
#                     return allData
#                 except Exception as e:
#                     return str(e)

#             else:
#               # Define polygon bounds
#               # Circle coordinates case
#                 xmin, ymin, xmax, ymax = shapely_polygon.bounds
#                 circ = shapely_polygon.length
#                 area = shapely_polygon.area
#                 if area > 2:
#                     step = 0.3
#                 elif area < 2 and area > 1:
#                     step = 0.2
#                 else:
#                     step = 0.1
#                 # Save all coordinates of points inside the polygon
#                 points_inside_polygon = []
#                 try:
#                     if len(circle_coords) > 0:
#                         # This is the case without WMS
#                         for coord in circle_coords:
#                             point = ShapelyPoint(coord["lat"], coord["lng"])
#                             if point.within(shapely_polygon):
#                                 points_inside_polygon.append((coord["lat"], coord["lng"]))
#                     else:
#                         # Case with WMS
#                         for x in range(int(xmin / step), int(xmax / step)):
#                             for y in range(int(ymin / step), int(ymax / step)):
#                                 point = ShapelyPoint(x * step, y * step)
#                                 if point.within(shapely_polygon):
#                                     points_inside_polygon.append((x * step, y * step))
#                 except Exception as coord:
#                     return str(coord)

#                 # Display the coordinates of points inside the polygon
#                 current = 20
#                 self.update_state(state='PROGRESS',
#                             meta={'current': current, 'total': total})
#                 df_polygon = pd.DataFrame(columns=["date_value", "lat_lng", "value_0"])
#                 points_len = len(points_inside_polygon)
#                 eight_length = points_len // 8 #25 0.125 40
#                 six_length = points_len // 6 #30 #0.166 45
#                 two_eight_len = 2 * points_len // 8 #35 0.25 50
#                 two_six_len = 2 * points_len // 6 #40 0.33 55
#                 three_eight_len = 3 * points_len // 8 #45 0.375 60
#                 half_len = round(points_len / 2) #50 0.5 65
#                 five_eight_len = 5 * points_len // 8 #55 0.625 70
#                 four_six_len = 4 * points_len // 6 #60 0.667 75
#                 six_eight_len = 6 * points_len // 8 #65 0.75 80
#                 five_six_len = 5 * points_len // 6 #70 0.83 85
#                 seven_eight_len = 7 * points_len // 8 #75 0.87 90


#                 i = 0
#                 dataTable = []
#                 for index, point in enumerate(points_inside_polygon):
#                     if index == eight_length:
#                         current = 40
#                         self.update_state(state='PROGRESS',
#                                     meta={'current': current, 'total': total})
                        
#                     if index == six_length:
#                         # It is at one-sixth
#                         current = 45
#                         self.update_state(state='PROGRESS',
#                                     meta={'current': current, 'total': total})
                        
#                     if index == two_eight_len:
#                         # It is at two-eighths (i.e., one-fourth)
#                         current = 50
#                         self.update_state(state='PROGRESS',
#                                     meta={'current': current, 'total': total})
                        
#                     elif index == two_six_len: 
#                         current = 55
#                         self.update_state(state='PROGRESS',
#                                     meta={'current': current, 'total': total})
                        
#                     elif index == three_eight_len: 
#                         current = 60
#                         self.update_state(state='PROGRESS',
#                                     meta={'current': current, 'total': total})
                        
#                     elif index == half_len: 
#                         current = 65
#                         self.update_state(state='PROGRESS',
#                                     meta={'current': current, 'total': total})
                        
#                     elif index == five_eight_len:
#                         current = 70
#                         self.update_state(state='PROGRESS',
#                                     meta={'current': current, 'total': total})
                        
#                     elif index == four_six_len:
#                         current = 75
#                         self.update_state(state='PROGRESS',
#                                     meta={'current': current, 'total': total})  
                        
#                     elif index == six_eight_len:
#                         current = 80
#                         self.update_state(state='PROGRESS',
#                                     meta={'current': current, 'total': total})
                        
#                     elif index == five_six_len:
#                         current = 85
#                         self.update_state(state='PROGRESS',
#                                     meta={'current': current, 'total': total})   

#                     elif index == seven_eight_len:
#                         current = 90
#                         self.update_state(state='PROGRESS',
#                                     meta={'current': current, 'total': total})    
#                     try:
#                         if is_indicator == "false":
#                             url = url_is_indicator(
#                                 is_indicator,
#                                 True,
#                                 False,
#                                 dataset_id=dataset_id,
#                                 layer_name=layer_name,
#                                 time_start=date_start,
#                                 time_finish=date_end,
#                                 latitude=str(point[0]),
#                                 longitude=str(point[1]),
#                                 num_parameters=num_param,
#                                 range_value=range_value,
#                             )
#                             df = read_erddap_data(url)

#                         else:
#                                 url = url_is_indicator(
#                                     is_indicator,
#                                     True,
#                                     True,
#                                     dataset_id=dataset_id,
#                                     layer_name=layer_name,
#                                     time_start=date_start,
#                                     time_finish=date_end,
#                                     latitude=str(point[0]),
#                                     longitude=str(point[1]),
#                                     num_parameters=num_param,
#                                     range_value=range_value,
#                                 )
#                                 df = read_erddap_data(url)


#                     except Exception as e:
#                         continue
#                     try:
#                         for index,row in enumerate(df.to_dict(orient="records")):
#                             if parametro_agg != "None":
#                                 if len(dataTable) == 0:
#                                     dat_tab = {}
#                                     dat_tab["time"] = row["time"]
#                                     dat_tab["latitude"] = row["latitude"]
#                                     dat_tab["longitude"] = row["longitude"]
#                                     dat_tab[parametro_agg] = (
#                                         row[parametro_agg]
#                                         if not pd.isna(row[parametro_agg])
#                                         else "Value not defined"
#                                     )
#                                     dat_tab[layer_name] = (
#                                         row[layer_name]
#                                         if not pd.isna(row[layer_name])
#                                         else "Value not defined"
#                                     )
#                                     dataTable.append(dat_tab)
#                                 if index > 0:
#                                     dat_tab = {}
#                                     dat_tab["time"] = convertToTime(row["time"])
#                                     dat_tab["latitude"] = row["latitude"]
#                                     dat_tab["longitude"] = row["longitude"]
#                                     dat_tab[parametro_agg] = (
#                                         row[parametro_agg]
#                                         if not pd.isna(row[parametro_agg])
#                                         else "Value not defined"
#                                     )
#                                     dat_tab[layer_name] = (
#                                         row[layer_name]
#                                         if not pd.isna(row[layer_name])
#                                         else "Value not defined"
#                                     )
#                                     dataTable.append(dat_tab)
#                                     if not pd.isna(row[layer_name]):
#                                         # Not NaN, insert it
#                                         df_polygon.loc[i] = [
#                                             row["time"],
#                                             "(" + row["latitude"] + "," + row["longitude"] + ")",
#                                             row[layer_name],
#                                         ]
#                                         defaults = {
#                                             "value_0": float(row[layer_name]),
#                                             "pol_vertices_str": pol_vertices_str,
#                                             "parametro_agg": row[parametro_agg],
#                                         }
#                                         if not is_database_almost_full():
#                                             Polygon.objects.update_or_create(
#                                                             dataset_id=Node.objects.get(id=dataset_id),
#                                                             date_value=convertToTime(row["time"]),
#                                                             latitude=float(row["latitude"]),
#                                                             longitude=float(row["longitude"]),
#                                                             coordinate = Point(float(row["longitude"]), float(row["latitude"])),
#                                                             defaults=defaults,
#                                                                             )
#                                     i += 1
#                             else:
#                                 if len(dataTable) == 0:
#                                     dat_tab = {}
#                                     dat_tab["time"] = row["time"]
#                                     dat_tab["latitude"] = row["latitude"]
#                                     dat_tab["longitude"] = row["longitude"]
#                                     dat_tab[layer_name] = (
#                                         row[layer_name]
#                                         if not pd.isna(row[layer_name])
#                                         else "Value not defined"
#                                     )
#                                     dataTable.append(dat_tab)
#                                 if index > 0:
#                                     dat_tab = {}
#                                     dat_tab["time"] = convertToTime(row["time"])
#                                     dat_tab["latitude"] = row["latitude"]
#                                     dat_tab["longitude"] = row["longitude"]
#                                     dat_tab[layer_name] = (
#                                         row[layer_name]
#                                         if not pd.isna(row[layer_name])
#                                         else "Value not defined"
#                                     )
#                                     dataTable.append(dat_tab)
#                                     if not pd.isna(row[layer_name]):
#                                         df_polygon.loc[i] = [
#                                             row["time"],
#                                             "(" + row["latitude"] + "," + row["longitude"] + ")",
#                                             row[layer_name],
#                                         ]

#                                         defaults = {
#                                             "value_0": float(row[layer_name]),
#                                             "pol_vertices_str": pol_vertices_str,
#                                         }
#                                         if not is_database_almost_full():
#                                             Polygon.objects.update_or_create(
#                                                             dataset_id=Node.objects.get(id=dataset_id),
#                                                             date_value=convertToTime(row["time"]),
#                                                             latitude=float(row["latitude"]),
#                                                             longitude=float(row["longitude"]),
#                                                             coordinate = Point(float(row["longitude"]), float(row["latitude"])),
#                                                             defaults=defaults,
#                                                                             )
#                                             i += 1
#                     except Exception as e:
#                         return str(e)
                
#                 current = 100
#                 self.update_state(state='PROGRESS',
#                             meta={'current': current, 'total': total})

#                 try:
#                     df_polygon = df_polygon.drop_duplicates(
#                         subset=["date_value", "lat_lng", "value_0"], keep="first"
#                     )
#                     df_polygon = df_polygon.dropna(how="all", axis=1)
#                     allData = {}
                    
#                     df_polygon["value_0"] = pd.to_numeric(df_polygon["value_0"])
#                     allData["dataBeforeOp"] = df_polygon.to_dict(orient="records")
#                     # Compute the mean of all values grouped by date

#                     # Apply the operation based on the values of operation and time_op
#                     if time_op == "default":
#                         date_value_to_list = df_polygon.copy()
#                         date_value_to_list = date_value_to_list.drop_duplicates(subset="date_value",keep="first")
#                         date_value_to_list["date_value"] = pd.to_datetime(date_value_to_list["date_value"])

                    
#                         # Apply the operation based on the values of operation and time_op
#                         df_polygon["date_value"] = pd.to_datetime(df_polygon["date_value"])
#                         pol_values = df_polygon["value_0"].tolist()
#                         trend_value_mean = df_polygon.groupby("date_value")["value_0"].mean().tolist()
#                         if len(pol_values) == 1:
#                             trend_value = pol_values[0]
#                             mean = pol_values[0]
#                             median = pol_values[0]
#                             std_dev = pol_values[0]
#                         else:
#                             if len(trend_value_mean) == 1:
#                                 trend_value = trend_value_mean[0]
#                             else:
#                                 trend_value = calculate_trend(date_value_to_list["date_value"].tolist(),trend_value_mean,timeperiod=adriaclim_timeperiod)
            
#                             mean = df_polygon["value_0"].mean()
#                             median = df_polygon["value_0"].median()
#                             std_dev = df_polygon["value_0"].std()
                        
#                         allData["mean"] = mean
#                         allData["median"] = median
#                         allData["stdev"] = std_dev
#                         allData["trend_yr"] = trend_value

#                     data_table_list = []
#                     for i in range(len(dataTable)):
#                         data_table = {}
#                         data_table["time"] = dataTable[i]["time"]
#                         data_table["latitude"] = dataTable[i]["latitude"]
#                         data_table["longitude"] = dataTable[i]["longitude"]
#                         data_table[layer_name] = dataTable[i][layer_name]
#                         if parametro_agg != "None":
#                             data_table[parametro_agg] = dataTable[i][parametro_agg]
#                         data_table_list.append(data_table)

#                     allData["dataTable"] = data_table_list
#                     # Set the cache before performing the requested operation, using all dates and values
#                     cache.set(key=key_cached,value=json.dumps(allData),timeout=43200) # 12-hour cache
#                     allData["dataPol"] = operation_before_after_cache(
#                         df_polygon, statistic, time_op
#                     )
#                 except Exception as e:
#                     return str(e)
                
#                 return allData
#     except Exception as e:
#         return str(e)

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

        self.update_state(
            state="PROGRESS",
            meta={"current": 10, "total": 100}
        )

        result = getDataPolygonNew(
            dataset_id=dataset_id,
            adriaclim_timeperiod=adriaclim_timeperiod,
            layer_name=layer_name,
            date_start=date_start,
            date_end=date_end,
            lat_lng_obj=lat_lng_obj,
            statistic=statistic,
            time_op=time_op,
            num_param=num_param,
            range_value=range_value,
            is_indicator=is_indicator,
            lat_min=lat_min,
            lat_max=lat_max,
            lng_min=lng_min,
            lng_max=lng_max,
            parametro_agg=parametro_agg,
            circle_coords=circle_coords,
        )

        self.update_state(
            state="PROGRESS",
            meta={"current": 100, "total": 100}
        )

        return result

    except Exception:
        logger.exception("task_get_data_polygon failed")
        raise
