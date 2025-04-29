import json
# import time
import pandas as pd
# import requests
import numpy as np
# import re
# import asyncio

from django.forms.models import model_to_dict
# from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from celery.result import AsyncResult
from rest_framework.decorators import api_view

from Dataset.models import Node, Polygon, Indicator
from .dataset_manager import getMetadata, getMetadataOfASpecificDataset
# from AdriaProject.settings import ERDDAP_URL
# from myFunctions.database_operations import is_database_almost_full, delete_all
# from myFunctions.utils import download_with_cache_as_csv
from myFunctions.geospatial_processing import getDataGraphicGeneric, getDataPolygonNew
from myFunctions.data_analysis import updateStatistics
# from myFunctions.views_datasets import getDataVectorialNew

@api_view(['GET','POST'])
def getAllDatasets(request):
    if request.method == 'GET' or request.method == 'POST':
        getAllDatasets()
        return HttpResponse("Ok")

def dataset_id_wrong(request):
    return render(request, "wrongIdPassed.html")

def getDataTable(request):
    if request.method == 'GET' or request.method == 'POST':
        idMeta = request.POST.get("idMeta")
        timeMin = request.POST.get("timeMin")
        timeMax = request.POST.get("timeMax")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        variable = request.POST.get("variable")
        range_value = request.POST.get("range_value")
        layer_name = request.POST.get("layer_name")
        operation = request.POST.get("operation")
        is_indicator = request.POST.get("is_indicator")

        data = getDataTableNew(
            idMeta, timeMin, timeMax, latitude, longitude, variable, range_value,
            layer_name, operation, is_indicator
        )

        return render(request, "getData.html", {"data": data})

@api_view(['GET','POST'])
def getAllNodes(request):
    if request.method == 'GET' or request.method == 'POST':
        try:
            nodes = Node.objects.all()
            nodes_list = [model_to_dict(node) for node in nodes]
            return JsonResponse(nodes_list, safe=False)
        except Exception as e:
            return JsonResponse(str(e), safe=False)

@api_view(['GET','POST'])
def getMetadataNew(request):
    if request.method == 'GET' or request.method == 'POST':
        idMeta = request.POST.get("idMeta")
        try:
            metadata = getMetadata(idMeta)
            return JsonResponse(metadata, safe=False)
        except Exception as e:
            print(e)

@api_view(['GET','POST'])
def get_metadata_table(request):
    if request.method == 'GET' or request.method == 'POST':
        idMeta = request.POST.get("idMeta")
        metadata = getMetadataOfASpecificDataset(idMeta)
        return JsonResponse(metadata, safe=False)

@api_view(['GET','POST'])
def getDataTableNew(request):
    if request.method == 'GET' or request.method == 'POST':
        try:
            dataset_id = request.POST.get("idMeta")
            lat = request.POST.get("latitude")
            lon = request.POST.get("longitude")
            time_start = request.POST.get("timeMin")
            time_end = request.POST.get("timeMax")
            variable = request.POST.get("variable")
            range_value = request.POST.get("range_value")
            layer_name = request.POST.get("layer_name")
            operation = request.POST.get("operation")
            is_indicator = request.POST.get("is_indicator")

            data = getDataGraphicGeneric(
                dataset_id,
                None,
                layer_name,
                time_start,
                time_end,
                lat,
                lon,
                None,
                range_value,
                is_indicator,
                "no",
                "no",
                "no",
                "no",
                operation=operation
            )
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse(str(e), safe=False)


@api_view(['GET','POST'])
def getDataGraphicNewCanvas(request):
    if request.method == 'GET' or request.method == 'POST':
        try:
            idMeta = request.POST.get("idMeta")
            latitude = request.POST.get("latitude")
            longitude = request.POST.get("longitude")
            time_start = request.POST.get("timeMin")
            time_end = request.POST.get("timeMax")
            variable = request.POST.get("variable")
            range_value = request.POST.get("range_value")
            layer_name = request.POST.get("layer_name")
            is_indicator = request.POST.get("is_indicator")
            operation = request.POST.get("operation")

            data = getDataGraphicGeneric(
                idMeta,
                None,
                layer_name,
                time_start,
                time_end,
                latitude,
                longitude,
                None,
                range_value,
                is_indicator,
                "no",
                "no",
                "no",
                "no",
                operation=operation
            )
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse(str(e), safe=False)


@api_view(['GET','POST'])
def getDataVectorialNew(request):
    if request.method == 'GET' or request.method == 'POST':
        try:
            idMeta = request.POST.get("idMeta")
            selVar = request.POST.get("selVar")
            selDate = request.POST.get("selDate")
            isIndicator = request.POST.get("isIndicator")

            data = getDataVectorialNew(idMeta, selVar, selDate, isIndicator)
            return JsonResponse({"dataVect": data})
        except Exception as e:
            return JsonResponse(str(e), safe=False)


@api_view(['GET','POST'])
def getDataPolygonNew(request):
    if request.method == 'GET' or request.method == 'POST':
        dataset_id = request.POST.get("dataset_id")
        adriaclim_timeperiod = request.POST.get("adriaclim_timeperiod")
        layer_name = request.POST.get("layer_name")
        date_start = request.POST.get("date_start")
        date_end = request.POST.get("date_end")
        lat_lng_obj = json.loads(request.POST.get("lat_lng_obj"))
        statistic = request.POST.get("statistic")
        time_op = request.POST.get("time_op")
        num_param = request.POST.get("num_param")
        range_value = request.POST.get("range_value")
        is_indicator = request.POST.get("is_indicator")
        lat_min = request.POST.get("lat_min")
        lat_max = request.POST.get("lat_max")
        lng_min = request.POST.get("lng_min")
        lng_max = request.POST.get("lng_max")
        parametro_agg = request.POST.get("parametro_agg")
        circle_coords = json.loads(request.POST.get("circle_coords"))

        data = getDataPolygonNew(
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
        )

        return JsonResponse(data, safe=False)


@api_view(['GET','POST'])
def check_task_status(request):
    task_id = request.GET.get("task_id")
    task = AsyncResult(task_id)
    response_data = {"state": task.state}
    if task.state == "SUCCESS":
        response_data["result"] = task.result
    return JsonResponse(response_data)


@api_view(['GET','POST'])
def discover_mb_indicator(request):
    from .data_analysis import discover_how_mb_indicator_are
    dataset_id = request.GET.get("dataset_id")
    result = discover_how_mb_indicator_are(dataset_id)
    return JsonResponse(result, safe=False)


@api_view(['GET','POST'])
def updateStatistics(request):
    if request.method == 'GET' or request.method == 'POST':
        dates = json.loads(request.POST.get("dates"))
        values = json.loads(request.POST.get("values"))
        is_polygon = request.POST.get("is_polygon")
        time_period = request.POST.get("time_period")

        data = updateStatistics(dates, values, is_polygon, time_period)
        return JsonResponse(data, safe=False)


@api_view(['GET','POST'])
def compareDatasets(request):
    if request.method == 'GET' or request.method == 'POST':
        try:
            dataset_id_1 = request.POST.get("dataset_id_1")
            dataset_id_2 = request.POST.get("dataset_id_2")
            lat = request.POST.get("latitude")
            lon = request.POST.get("longitude")
            time_start = request.POST.get("timeMin")
            time_end = request.POST.get("timeMax")
            variable = request.POST.get("variable")
            range_value = request.POST.get("range_value")
            layer_name = request.POST.get("layer_name")
            operation = request.POST.get("operation")

            data1 = getDataGraphicGeneric(
                dataset_id_1,
                None,
                layer_name,
                time_start,
                time_end,
                lat,
                lon,
                None,
                range_value,
                False,
                "no",
                "no",
                "no",
                "no",
                operation=operation
            )

            data2 = getDataGraphicGeneric(
                dataset_id_2,
                None,
                layer_name,
                time_start,
                time_end,
                lat,
                lon,
                None,
                range_value,
                False,
                "no",
                "no",
                "no",
                "no",
                operation=operation
            )

            values1 = [float(v) for v in data1[0]]
            values2 = [float(v) for v in data2[0]]

            mean_difference = np.mean(np.array(values1) - np.array(values2))
            mean_absolute_difference = np.mean(np.abs(np.array(values1) - np.array(values2)))
            rmse = np.sqrt(np.mean((np.array(values1) - np.array(values2)) ** 2))

            result = {
                "mean_difference_avg": mean_difference,
                "mean_difference_avg_abs": mean_absolute_difference,
                "root_mean_squared_difference": rmse,
                "data1": data1,
                "data2": data2,
            }

            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
