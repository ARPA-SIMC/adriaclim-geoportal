from django.http import JsonResponse, HttpResponse
from django.forms.models import model_to_dict
from django.shortcuts import render
from rest_framework.decorators import api_view
from celery.result import AsyncResult
from operator import itemgetter
import json
import pandas as pd

from Dataset.models import Node, Polygon, Indicator
from .dataset_manager import getMetadata, getMetadataOfASpecificDataset, getAllDatasets
from .geospatial_processing import getDataGraphicGeneric, getDataPolygonNew
from myFunctions.data_analysis import updateStatistics
from myFunctions.getDataFunctions import functionPoint 
from myFunctions import compareStatistics

@api_view(['GET','POST'])
def allDatasets(request):
    if request.method in ['GET', 'POST']:
        getAllDatasets()
        return HttpResponse("Ok")

def dataset_id_wrong(request):
    return render(request, "wrongIdPassed.html")

def getDataTable(request):
    if request.method in ['GET', 'POST']:
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
    try:
        nodes = Node.objects.all()
        nodes_list = [model_to_dict(node) for node in nodes]
        return JsonResponse({"nodes": nodes_list})
    except Exception as e:
        return JsonResponse({"error": str(e)})

@api_view(['GET','POST'])
def getMetadataNew(request):
    idMeta = request.POST.get("idMeta")
    try:
        metadata = getMetadata(idMeta)
        return JsonResponse(metadata, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET','POST'])
def get_metadata_table(request):
    idMeta = request.POST.get("idMeta")
    metadata = getMetadataOfASpecificDataset(idMeta)
    return JsonResponse(metadata, safe=False)

@api_view(['GET','POST'])
def getDataTableNew(request):
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
            "no", "no", "no", "no",
            operation=operation
        )
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse(str(e), safe=False)

@api_view(['GET','POST'])
def getDataGraphicNewCanvas(request):
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
            "no", "no", "no", "no",
            operation=operation
        )
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse(str(e), safe=False)

@api_view(['GET','POST'])
def getDataVectorialNew(request):
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
    from myFunctions.data_analysis import discover_how_mb_indicator_are
    dataset_id = request.GET.get("dataset_id")
    result = discover_how_mb_indicator_are(dataset_id)
    return JsonResponse(result, safe=False)

@api_view(['GET','POST'])
def updateStatistics(request):
    dates = json.loads(request.POST.get("dates"))
    values = json.loads(request.POST.get("values"))
    is_polygon = request.POST.get("is_polygon")
    time_period = request.POST.get("time_period")

    data = updateStatistics(dates, values, is_polygon, time_period)
    return JsonResponse(data, safe=False)

@api_view(['GET','POST'])
def compareDatasets(request):
    try:
        compare_obj = request.data
        context = "one"
        operation = "default"
        latitude = str(compare_obj.get('latlng')["lat"])
        longitude = str(compare_obj.get('latlng')["lng"])

        first_dataset = compare_obj.get('firstDataset')["name"]
        first_dataset_id = first_dataset["id"]
        first_dataset_timeperiod = first_dataset["adriaclim_timeperiod"]
        first_dataset_layer_name = str(compare_obj.get('firstVarSel'))
        first_dataset_time_start = first_dataset["time_start"]
        first_dataset_time_end = first_dataset["time_end"]
        first_dataset_param = str(compare_obj.get('firstValue'))

        first_result = functionPoint.getDataGraphicGeneric(
            first_dataset_id, first_dataset_timeperiod, first_dataset_layer_name,
            first_dataset_time_start, first_dataset_time_end,
            latitude, longitude, 0, first_dataset_param, 0,
            "no", "no", "no", "no",
            operation=operation, context=context
        )
        first_list = first_result[first_dataset_layer_name]
        all_values_first = list(map(float, map(itemgetter('y'), first_list)))

        second_dataset = compare_obj.get('secondDataset')["name"]
        second_dataset_id = second_dataset["id"]
        second_dataset_timeperiod = second_dataset["adriaclim_timeperiod"]
        second_dataset_layer_name = str(compare_obj.get('secondVarSel'))
        second_dataset_time_start = second_dataset["time_start"]
        second_dataset_time_end = second_dataset["time_end"]
        second_dataset_param = str(compare_obj.get('secondValue'))

        second_result = functionPoint.getDataGraphicGeneric(
            second_dataset_id, second_dataset_timeperiod, second_dataset_layer_name,
            second_dataset_time_start, second_dataset_time_end,
            latitude, longitude, 0, second_dataset_param, 0,
            "no", "no", "no", "no",
            operation=operation, context=context
        )
        second_list = second_result[second_dataset_layer_name]
        all_values_second = list(map(float, map(itemgetter('y'), second_list)))

        mean_diff_avg = compareStatistics.mean_difference_avg(all_values_first, all_values_second, False)
        mean_diff_avg_abs = compareStatistics.mean_difference_avg(all_values_first, all_values_second, True)
        root_squared_diff = compareStatistics.root_mean_squared_difference(all_values_first, all_values_second)

        allData = {
            "firstResult": first_result,
            "secondResult": second_result,
            "meanDiffAvg": mean_diff_avg,
            "meanDiffAvgAbs": mean_diff_avg_abs,
            "rootSquaredDiff": root_squared_diff,
        }

        return JsonResponse({"compareResult": allData})
    except Exception as e:
        print("Eccezione", e)
        return HttpResponse("Errore", status=400)



