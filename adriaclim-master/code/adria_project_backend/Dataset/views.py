import json
import pandas as pd

from django.http import JsonResponse, HttpResponse
from django.forms.models import model_to_dict
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from celery.result import AsyncResult
from operator import itemgetter
from django.http import JsonResponse
import logging
import logging, math

from Metadata.metadata_manager import getMetadata, getMetadataOfASpecificDataset
from .geospatial_processing import getDataGraphicGeneric
from .tasks import task_get_data_polygon

from Dataset.models import Node

from Processing.data_analysis import updateStatisticsNew, getDataVectorial
from Processing import compareStatistics
from Processing.functionTable import getDataFunctionsTable




@api_view(['GET'])
def allDatasets(request):
    datasets = Node.objects.exclude(wms_url="").values('id', 'title', 'wms_url')
    return JsonResponse({"datasets": list(datasets)})

def dataset_id_wrong(request):
    return render(request, "wrongIdPassed.html")

def getDataTable(request,dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value):
    data=getDataTable(dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value)
    headers=[col for col in data.fieldnames]
    out=[[row[h] for h in headers] for row in data]
    return HttpResponse(render(request,"getData.html",{"data":out,"headers":headers}))

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
    idMeta = request.data.get("idMeta")
    try:
        metadata = getMetadata(idMeta)
        return JsonResponse({'metadata': metadata})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET','POST'])
def get_metadata_table(request):
    idMeta = request.data.get("idMeta")
    metadata = getMetadataOfASpecificDataset(idMeta)
    return JsonResponse(metadata, safe=False)

@api_view(['GET','POST'])
def getDataTableNew(request):
    dataset_id = request.data.get("idMeta")
    latitude = request.data.get("lat")
    longitude = request.data.get("lng")
    time_start = request.data.get("dateStart")
    time_finish = request.data.get("dateEnd")
    layer_name = request.data.get("variable")
    num_parameters = request.data.get("dimensions")
    range_value = request.data.get("range")
    data = getDataFunctionsTable(dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value)
    return JsonResponse({"data":data})

@api_view(['GET','POST'])
def getDataGraphicNewCanvas(request):
    try:
        dataset_id = request.data.get("idMeta")
        dataset = request.data.get('dataset')
        adriaclim_timeperiod = dataset.get('adriaclim_timeperiod')
        latitude = str(request.data.get("lat"))
        longitude = str(request.data.get("lng"))
        time_start = str(request.data.get("dateStart"))
        time_finish = str(request.data.get("dateEnd"))
        layer_name = request.data.get("variable")
        num_parameters = request.data.get("dimensions")
        range_value = str(request.data.get("range"))
        lat_min = str(request.data.get("lat_min"))
        lat_max =str(request.data.get("lat_max"))
        lng_min = str(request.data.get("lng_min"))
        lng_max =str(request.data.get("lng_max"))
        operation = request.data.get("operation") #default or type of operation
        context = request.data.get("context") #one or poylgon
        allData = getDataGraphicGeneric(dataset_id,adriaclim_timeperiod,layer_name,time_start,time_finish,latitude,longitude,0,range_value,0,lat_min,lng_min,lat_max,lng_max,operation=operation,context=context)
        if allData == "fuoriWms":
            return JsonResponse({"allData":allData})
        else:
            return JsonResponse({'allData':allData})
    except Exception as e:
        return "fuoriWms"


@api_view(['GET','POST'])
def getDataVectorialNew(request):
    try:

        dataset = request.data.get("dataset")
        dataset_id = dataset.get('id')
        sel_date = str(request.data.get('selDate'))
        layer_name = request.data.get('selVar')
        num_param = dataset.get('variables')
        num_dimensions = dataset.get('dimensions')
        lat_min = dataset.get('lat_min')
        lat_max = dataset.get('lat_max')
        lng_min = dataset.get('lng_min')
        lng_max = dataset.get('lng_max')
        is_indicator = request.data.get('isIndicator')
        if is_indicator == "false":
            num_param = int(num_dimensions)
        dataVect=getDataVectorial(dataset_id,layer_name,sel_date,lat_min,lat_max,lng_min,lng_max,num_param,0,is_indicator)
        return JsonResponse({'dataVect': dataVect})
    except Exception as e:
        return str(e)
        

@api_view(['GET','POST'])
def getDataPolygonNew_view(request):
    try:
        request_data = request.data
        #call celery task
        task = task_get_data_polygon.apply_async(args=[request_data],queue="my_queue")
        return JsonResponse({'task_id':task.id})
    except Exception as e:
        return str(e)

# @api_view(['GET','POST'])
# def check_task_status(request):
#     try:
#         task = AsyncResult(request.data.get('task_id'))
#         response = {'status': task.status}
#         if task.status == 'SUCCESS':
#             response['result'] = task.result
#         if task.state == "PROGRESS":
#             response["progressBar"] = task.info.get('current')
#         return JsonResponse({"dataVect":response})
#     except Exception as e:
#         response["error"] = str(e)
#         return JsonResponse({"dataVect":response})


logger = logging.getLogger(__name__)

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

@api_view(['GET', 'POST'])
def check_task_status(request):
    task_id = None
    try:
        task_id = getattr(request, "data", {}).get('task_id') or request.GET.get('task_id')
        task = AsyncResult(task_id)
        status = task.status

        # Base response
        response = {'status': status, 'task_id': task_id}

        if status == 'SUCCESS':
            result = _json_sanitize(task.result)

            # 1) mantieni la chiave "result" come prima
            response['result'] = result

            # 2) FLATTEN: copia le chiavi del risultato direttamente in dataVect
            #    così il frontend può leggere dataVect.dataPol / dataVect.dataTable / ecc.
            if isinstance(result, dict):
                response.update(result)

            logger.info("check_task_status(%s) -> SUCCESS (keys: %s)", task_id, list(result.keys()) if isinstance(result, dict) else type(result).__name__)
            return JsonResponse({"dataVect": response}, json_dumps_params={'allow_nan': False})

        elif status == 'PROGRESS' and isinstance(task.info, dict):
            response["progressBar"] = task.info.get('current')

        elif status in ('FAILURE', 'REVOKED'):
            try:
                response['error'] = str(task.result)
            except Exception:
                response['error'] = 'Task failed (no result)'
            tb = getattr(task, 'traceback', None)
            if tb:
                response['traceback'] = tb[-800:]

        logger.info("check_task_status(%s) -> %s", task_id, status)
        return JsonResponse({"dataVect": response}, json_dumps_params={'allow_nan': False})

    except Exception as e:
        logger.exception("check_task_status error (task_id=%s)", task_id)
        return JsonResponse({"dataVect": {'status': 'ERROR', 'error': str(e), 'task_id': task_id}}, json_dumps_params={'allow_nan': False})
    
@api_view(['GET','POST'])
def updateStatistics(request):
    new_dates = request.data.get("dates")
    new_values = request.data.get("values")
    dataset = request.data.get("dataset")
    polygon = request.data.get("polygon")
    adriaclim_timeperiod = dataset.get("adriaclim_timeperiod")
    new_values_calculated = updateStatisticsNew(new_dates,new_values,adriaclim_timeperiod,polygon)
    return JsonResponse({"newValues":new_values_calculated})

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
        first_result = getDataGraphicGeneric(first_dataset_id,first_dataset_timeperiod,first_dataset_layer_name,first_dataset_time_start,first_dataset_time_end,latitude,longitude,0,first_dataset_param,0,"no","no","no","no",operation=operation,context=context)
        first_list = first_result[first_dataset_layer_name]
        all_values_first =  list(map(float, map(itemgetter('y'), first_list))) #prendo tutti i valori del primo dataset
        second_dataset = compare_obj.get('secondDataset')["name"]
        second_dataset_id = second_dataset["id"]
        second_dataset_timeperiod = second_dataset["adriaclim_timeperiod"]
        second_dataset_layer_name = str(compare_obj.get('secondVarSel'))
        second_dataset_time_start = second_dataset["time_start"]
        second_dataset_time_end = second_dataset["time_end"]
        second_dataset_param = str(compare_obj.get('secondValue'))
        second_result = getDataGraphicGeneric(second_dataset_id,second_dataset_timeperiod,second_dataset_layer_name,second_dataset_time_start,second_dataset_time_end,latitude,longitude,0,second_dataset_param,0,"no","no","no","no",operation=operation,context=context)
        second_list = second_result[second_dataset_layer_name]
        all_values_second =  list(map(float, map(itemgetter('y'), second_list))) #prendo tutti i valori del secondo dataset
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
        return HttpResponse("Errore",status=400)
    
@api_view(['GET','POST'])
def getDataPolygonNew(request):
    try:
        request_data = request.data
        #call celery task
        task = task_get_data_polygon.apply_async(args=[request_data],queue="my_queue")
        return JsonResponse({'task_id':task.id})
    except Exception as e:
        return str(e)



