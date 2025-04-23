from django.forms import model_to_dict
from django.http import response,request,Http404
from django.http.response import HttpResponse, JsonResponse,ResponseHeaders
from django.conf import settings
from django.shortcuts import render
from django.db.models import Q
from .tasks import task_get_data_polygon

# import allFunctions
from myFunctions import allFunctions
from myFunctions.getDataFunctions import functionPoint, functionPolygon, functionTable
from myFunctions import compareStatistics
from operator import itemgetter

from .forms import DatasetForm
import requests
import os
import json
from .models import Node,Indicator
from AdriaProject.settings import ERDDAP_URL
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.core import serializers
from asgiref.sync import sync_to_async
from celery.result import AsyncResult
from datetime import datetime



# Create your views here.


@api_view(['GET','POST'])
def getAllDatasets(request):

    allNodes = allFunctions.getAllDatasets()
    return HttpResponse("Ok", status=200)


def dataset_id_wrong(request):
    return render(request,"wrongIdPassed.html")

def getDataTable(request,dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value):
    data=allFunctions.getDataTable(dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value)
    headers=[col for col in data.fieldnames]
    out=[[row[h] for h in headers] for row in data]
    return HttpResponse(render(request,"getData.html",{"data":out,"headers":headers}))



@api_view(['GET', 'POST'])
def getAllNodes(request):
    try:
        all_nodes = Node.objects.all()
        data = [model_to_dict(i) for i in all_nodes]
        return JsonResponse({"nodes": data})
    except Exception as e:
        print("ERRORE GET ALL NODES =", e)
        return str(e)


@api_view(['GET', 'POST'])
def getMetadataNew(request):
    try:
        idMeta = request.data.get('idMeta')
        metadata=allFunctions.getMetadata(idMeta)
        return JsonResponse({'metadata': metadata})
    except Exception as e:
        print("ERROR ==", e)


#New function for 2D layers!
def layers2DNew(request):
    service=request.GET['service']
    request1=request.GET['request']
    layers=request.GET['layers']
    styles=request.GET['styles']
    format=request.GET['format']
    transparent=request.GET['transparent']
    version=request.GET['version']
    width=request.GET['width']
    height=request.GET['height']
    crs=request.GET['crs']
    bbox=request.GET['bbox']
    time=request.GET['time']
    bgcolor=request.GET['bgcolor']
    dataset_id=layers.partition(":")[0]
    url=ERDDAP_URL+"/wms/"+dataset_id+"/request?&service="+service+"&request="+request1+"&layers="+layers+"&styles="+styles+"&format="+format+"&transparent="+transparent+"&version="+version+"&bgcolor="+bgcolor+"&time="+time+"&width="+width+"&height="+height+"&crs="+crs+"&bbox="+bbox
    requests_response = requests.get(url)
    django_response = HttpResponse(
            content=requests_response.content,
            status=requests_response.status_code,
            content_type=requests_response.headers['Content-Type']
        )
    # return JsonResponse({'ciao':'ciao'})
        
    return django_response

#New function for 3D Layers!
def layers3DNew(request,parameter):
    service=request.GET['service']
    request1=request.GET['request']
    layers=request.GET['layers']
    styles=request.GET['styles']
    format=request.GET['format']
    transparent=request.GET['transparent']
    version=request.GET['version']
    width=request.GET['width']
    height=request.GET['height']
    crs=request.GET['crs']
    bbox=request.GET['bbox']
    time=request.GET['time']
    bgcolor=request.GET['bgcolor']
    value_param=request.GET[parameter]
    dataset_id=layers.partition(":")[0]
    url=ERDDAP_URL+"/wms/"+dataset_id+"/request?&service="+service+"&request="+request1+"&layers="+layers+"&styles="+styles+"&format="+format+"&transparent="+transparent+"&version="+version+"&bgcolor="+bgcolor+"&time="+time+"&"+parameter+"="+value_param+"&width="+width+"&height="+height+"&crs="+crs+"&bbox="+bbox
    requests_response = requests.get(url)
    django_response = HttpResponse(
            content=requests_response.content,
            status=requests_response.status_code,
            content_type=requests_response.headers['Content-Type']
        )
        
    return django_response


#This is for the overlays!!
def overlaysNew(request,dataset_id):
    service=request.GET['service']
    request1=request.GET['request']
    layers=request.GET['layers']
    styles=request.GET['styles']
    format=request.GET['format']
    transparent=request.GET['transparent']
    version=request.GET['version']
    width=request.GET['width']
    height=request.GET['height']
    crs=request.GET['crs']
    bbox=request.GET['bbox']
    bgcolor=request.GET['bgcolor']
    url=ERDDAP_URL+"/wms/"+dataset_id+"/request?&service="+service+"&request="+request1+"&layers="+layers+"&styles="+styles+"&format="+format+"&transparent="+transparent+"&version="+version+"&bgcolor="+bgcolor+"&width="+width+"&height="+height+"&crs="+crs+"&bbox="+bbox
    requests_response = requests.get(url)

    django_response = HttpResponse(
            content=requests_response.content,
            status=requests_response.status_code,
            content_type=requests_response.headers['Content-Type']
        )
        
    return django_response

@api_view(['GET','POST'])
def get_metadata_table(request):
    dataset_id = request.data.get("idMeta")
    metadata=allFunctions.getMetadataOfASpecificDataset(dataset_id)
    return JsonResponse({"metadata":metadata})

# @api_view(['GET','POST'])
# def getDataTableNew(request):
#     dataset_id = request.data.get("idMeta")
#     latitude = request.data.get("lat")
#     longitude = request.data.get("lng")
#     time_start = request.data.get("dateStart")
#     time_finish = request.data.get("dateEnd")
#     layer_name = request.data.get("variable")
#     num_parameters = request.data.get("dimensions")
#     range_value = request.data.get("range")
#     data = allFunctions.getDataTable(dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value)
#     return JsonResponse({"data":data})
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
    data = functionTable.getDataFunctionsTable(dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value)
    return JsonResponse({"data":data})

# @api_view(['GET','POST'])
# def getDataGraphicNewCanvas(request):
#     try:
#         dataset_id = request.data.get("idMeta")
#         dataset = request.data.get('dataset')
#         adriaclim_timeperiod = dataset.get('adriaclim_timeperiod')
#         latitude = str(request.data.get("lat"))
#         longitude = str(request.data.get("lng"))
#         time_start = str(request.data.get("dateStart"))
#         time_finish = str(request.data.get("dateEnd"))
#         layer_name = request.data.get("variable")
#         num_parameters = request.data.get("dimensions")
#         range_value = str(request.data.get("range"))
#         lat_min = str(request.data.get("lat_min"))
#         lat_max =str(request.data.get("lat_max"))
#         lng_min = str(request.data.get("lng_min"))
#         lng_max =str(request.data.get("lng_max"))
#         operation = request.data.get("operation") #default or type of operation
#         context = request.data.get("context") #one or poylgon
#         allData = allFunctions.getDataGraphicGeneric(dataset_id,adriaclim_timeperiod,layer_name,time_start,time_finish,latitude,longitude,0,range_value,0,lat_min,lng_min,lat_max,lng_max,operation=operation,context=context)
#         if allData == "fuoriWms":
#             return JsonResponse({"allData":allData})
#         else:
#             return JsonResponse({'allData':allData})
#     except Exception as e:
#         print("ERRORE:",e)
#         return "fuoriWms"

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
        allData = functionPoint.getDataGraphicGeneric(dataset_id,adriaclim_timeperiod,layer_name,time_start,time_finish,latitude,longitude,0,range_value,0,lat_min,lng_min,lat_max,lng_max,operation=operation,context=context)
        # print("ALL DATA =============",allData)
        if allData == "fuoriWms":
            return JsonResponse({"allData":allData})
        else:
            return JsonResponse({'allData':allData})
    except Exception as e:
        print("ERRORE:",e)
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
        # print("SEL VAR ============",layer_name)
        lat_min = dataset.get('lat_min')
        lat_max = dataset.get('lat_max')
        lng_min = dataset.get('lng_min')
        lng_max = dataset.get('lng_max')
        is_indicator = request.data.get('isIndicator')
        # print("DATASET ID =", dataset_id)
        # print("SEL DATE =", sel_date)
        # print("LAYER NAME =", layer_name)
        # print("NUM PARAM =", num_param)
        # print("NUM PARAM TYPE =", type(num_param))
        # print("NUM DIMENSIONS =", num_dimensions)
        # print("NUM DIMENSIONS TYPE =", type(num_dimensions))
        # print("LAT MIN =", lat_min)
        # print("LAT MAX =", lat_max)
        # print("LNG MIN =", lng_min)
        # print("LNG MAX =", lng_max)
        # print("IS INDICATOR =", is_indicator)
        if is_indicator == "false":
            num_param = int(num_dimensions)
        
        # print("NUM PARAM =", num_param)
        # print("NUM PARAM TYPE =", type(num_param))
        # print("NUM DIMENSIONS =", num_dimensions)
        # print("NUM DIMENSIONS TYPE =", type(num_dimensions))
        
        # print("DATASET =", dataset)
        dataVect=allFunctions.getDataVectorial(dataset_id,layer_name,sel_date,lat_min,lat_max,lng_min,lng_max,num_param,0,is_indicator)
        # print("*************************************")
        # print("DATA VECT =============",dataVect)
        # print("*************************************")
        return JsonResponse({'dataVect': dataVect})
    except Exception as e:
        print("ERRORE GET VECTORIAL FINALE =", e)
        return str(e)

@api_view(['GET','POST'])
def getDataPolygonNew(request):
    try:
        request_data = request.data
        #call celery task
        task = task_get_data_polygon.apply_async(args=[request_data],queue="my_queue")
        return JsonResponse({'task_id':task.id})
    except Exception as e:
        print("eccezione",e)
        return str(e)

@api_view(['GET','POST'])
def check_task_status(request):
    try:
        task = AsyncResult(request.data.get('task_id'))
        response = {'status': task.status}
        # print("Task status",task.status)
        # print("TASK======",task)
        if task.status == 'SUCCESS':
            response['result'] = task.result
        if task.state == "PROGRESS":
            response["progressBar"] = task.info.get('current')
            # print("Siamo nello stato di progress")
            # return JsonResponse({"dataVect": task.info.get("current")})
            # 
            

        # if task.info is not None and 'progress' in task.info:
        #     print("TASK INFO PERCENTAGE============",task.info['progress'])
            # print("response============",response)
        return JsonResponse({"dataVect":response})
    except Exception as e:
        print("Eccezione check_task_status",e)
        response["error"] = str(e)
        return JsonResponse({"dataVect":response})

@api_view(['GET','POST'])
def discover_mb_indicator(request):
    mb_indicator = allFunctions.discover_how_mb_indicator_are(request.data.get('timeperiod'))
    return JsonResponse({"mb":mb_indicator})
    



@api_view(['GET','POST'])
def updateStatistics(request):
    new_dates = request.data.get("dates")
    new_values = request.data.get("values")
    dataset = request.data.get("dataset")
    polygon = request.data.get("polygon")
    adriaclim_timeperiod = dataset.get("adriaclim_timeperiod")
    new_values_calculated = allFunctions.updateStatistics(new_dates,new_values,adriaclim_timeperiod,polygon)
    return JsonResponse({"newValues":new_values_calculated})

# def check_additional_param(dataset):
#     if dataset["griddap_url"] != "" and dataset["dimensions"] > 3:
#         #è griddap e ha un parametro aggiuntivo
#         #passi il valore del minimo del parametro aggiuntivo
#         return str(dataset["param_min"])
#     else:
#         return "0"
    
@api_view(['GET','POST'])
def compareDatasets(request):
    try:
        # print("Request",request)
        compare_obj = request.data
        # print("COMPARE_OBJ===============",compare_obj)
        context = "one"
        operation = "default"
        latitude = str(compare_obj.get('latlng')["lat"])
        longitude = str(compare_obj.get('latlng')["lng"])
        # print("Latitude: ",latitude)
        # print("Longitude: ",longitude)
        first_dataset = compare_obj.get('firstDataset')["name"]
        # print("First_dataset: ",first_dataset)
        first_dataset_id = first_dataset["id"]
        # print("First_dataset_id: ",first_dataset_id)
        first_dataset_timeperiod = first_dataset["adriaclim_timeperiod"]
        first_dataset_layer_name = str(compare_obj.get('firstVarSel'))
        first_dataset_time_start = first_dataset["time_start"]
        first_dataset_time_end = first_dataset["time_end"]
        first_dataset_param = str(compare_obj.get('firstValue'))
        first_result = functionPoint.getDataGraphicGeneric(first_dataset_id,first_dataset_timeperiod,first_dataset_layer_name,first_dataset_time_start,first_dataset_time_end,latitude,longitude,0,first_dataset_param,0,"no","no","no","no",operation=operation,context=context)
        first_list = first_result[first_dataset_layer_name]
        all_values_first =  list(map(float, map(itemgetter('y'), first_list))) #prendo tutti i valori del primo dataset
        # print("all_values_first",all_values_first)
        second_dataset = compare_obj.get('secondDataset')["name"]
        # print("Second_dataset: ",second_dataset)
        second_dataset_id = second_dataset["id"]
        second_dataset_timeperiod = second_dataset["adriaclim_timeperiod"]
        second_dataset_layer_name = str(compare_obj.get('secondVarSel'))
        second_dataset_time_start = second_dataset["time_start"]
        second_dataset_time_end = second_dataset["time_end"]
        second_dataset_param = str(compare_obj.get('secondValue'))
        second_result = functionPoint.getDataGraphicGeneric(second_dataset_id,second_dataset_timeperiod,second_dataset_layer_name,second_dataset_time_start,second_dataset_time_end,latitude,longitude,0,second_dataset_param,0,"no","no","no","no",operation=operation,context=context)
        second_list = second_result[second_dataset_layer_name]
        # print("second list===",second_list)
        all_values_second =  list(map(float, map(itemgetter('y'), second_list))) #prendo tutti i valori del secondo dataset
        # print("all_values_second===",all_values_second)
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
        
        # allData = functionPoint.getDataGraphicGeneric(dataset_id,adriaclim_timeperiod,layer_name,time_start,time_finish,latitude,longitude,0,range_value,0,lat_min,lng_min,lat_max,lng_max,operation=operation,context=context)
        # if allData == "fuoriWms":
        #     return JsonResponse({"compareResult":allData})
        # else:
        #     return JsonResponse({'compareResult':allData})

        return JsonResponse({"compareResult": allData})
    except Exception as e:
        print("Eccezione",e)
        return HttpResponse("Errore",status=400)
    


    
    
    

