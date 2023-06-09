from celery import shared_task
import numpy as np

@shared_task
def task_get_data_polygon(request_data):
    try:
        from myFunctions import allFunctions
        dataset = request_data["dataset"]
        dataset_id = request_data["dataset"]['id']
        date_start = request_data["dataset"]['time_start']
        date_end = request_data["dataset"]['time_end']
        layer_name = request_data['selVar']
        adriaclim_timeperiod = request_data['dataset']['adriaclim_timeperiod']
        range = str(request_data['range'])
        num_param = request_data["dataset"]['dimensions']
        parametro_agg = str(request_data['parametro_agg'])
        lat_min = request_data["dataset"]['lat_min']
        lat_max = request_data["dataset"]['lat_max']
        lng_min = request_data["dataset"]['lng_min']
        lng_max = request_data["dataset"]['lng_max']
        time_op = request_data['operation']
        statistic = request_data['statistic']
        circle_coords = request_data['circleCoords']
        lat_lng_obj = request_data['latLngObj']
        is_indicator = request_data['isIndicator']
        dataVect = allFunctions.getDataPolygonNew(dataset_id,adriaclim_timeperiod,layer_name,date_start,date_end,lat_lng_obj,statistic,time_op,num_param,range,is_indicator,lat_min,lat_max,lng_min,lng_max,parametro_agg,circle_coords)
        return dataVect
    except Exception as e:
        print("eccezione task",e)
        return str(e)
