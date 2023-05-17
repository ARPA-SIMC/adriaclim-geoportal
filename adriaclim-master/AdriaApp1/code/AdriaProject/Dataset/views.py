from django.forms import model_to_dict
from django.http import response,request,Http404
from django.http.response import HttpResponse, JsonResponse,ResponseHeaders
from django.conf import settings
from django.shortcuts import render
from django.db.models import Q
from .tasks import task_get_data_polygon

# import allFunctions
from myFunctions import allFunctions
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



# Create your views here.
def index(request):
    form=DatasetForm()
    datasets=Node.objects.all()
    indicators=Indicator.objects.filter(~Q(adriaclim_dataset="no"))
    response=render(request,"homepage.html",{'form':form,'datasets':datasets,'indicators':indicators})
    return response

def overlays(request,dataset_id):
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
    print(url)
    requests_response = requests.get(url)
    django_response = HttpResponse(
            content=requests_response.content,
            status=requests_response.status_code,
            content_type=requests_response.headers['Content-Type']
        )
        
    return django_response

def layers2D(request):
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
        
    return django_response

def layers3D(request,parameter):
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
    print(url)
    requests_response = requests.get(url)
    django_response = HttpResponse(
            content=requests_response.content,
            status=requests_response.status_code,
            content_type=requests_response.headers['Content-Type']
        )
        
    return django_response



def allDatasets(request):
        allData=allFunctions.listAllDatasets()
        headers=[col for col in allData.fieldnames]
        out=[[row[h] for h in headers] for row in allData]
        return render(request,"allDatasets.html",{"data":out,"headers":headers})



@api_view(['GET','POST'])
def getAllDatasets(request):

    allNodes = allFunctions.getAllDatasets()
    return HttpResponse("Ok", status=200)

def getTitle(request):
    titles=allFunctions.getTitle()
    return JsonResponse({'title':titles})

def getIndicators(request):
    indicators = allFunctions.getIndicators()
    return JsonResponse({'indicators':indicators})

def rompiamo_tutto(request):
    try:
        allFunctions.rompo_tutto()
        return "Ho aggiustato tutto!!!!"
    except Exception as e:
        print("Ho rotto tutto!!!!!",e)
        return str(e)


def getMetadataUrl(request,dataset_id):
    metadata=allFunctions.getMetadataOfASpecificDataset(dataset_id)
    return HttpResponse(metadata)

def getWMS(request):
    wms=allFunctions.getWMS()
    return JsonResponse({'wms':wms})

def getMetadata(request,title):
    metadata=allFunctions.getMetadataTime1(title)
    return JsonResponse({'metadata':metadata})

def dataset_id_wrong(request):
    return render(request,"wrongIdPassed.html")

def getDataTable(request,dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value):
    data=allFunctions.getDataTable(dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value)
    headers=[col for col in data.fieldnames]
    out=[[row[h] for h in headers] for row in data]
    return HttpResponse(render(request,"getData.html",{"data":out,"headers":headers}))



def getDataTableIndicator(request,dataset_id,layer_name,time_start,time_finish,lat_min,lat_max,long_min,long_max,num_parameters,range_value):
    data=allFunctions.getDataTableIndicator(dataset_id,layer_name,time_start,time_finish,lat_min,lat_max,long_min,long_max,num_parameters,range_value)
    headers=[col for col in data.fieldnames]
    out=[[row[h] for h in headers] for row in data]
    return render(request,"getData.html",{"data":out,"headers":headers})


def getDataGraphic(request,dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,num_parameters,range_value,is_indicator,latMin,longMin,latMax,longMax):
    allData=allFunctions.getDataGraphic(dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,
                                        num_parameters,range_value,is_indicator,latMin,longMin,latMax,longMax)
    return JsonResponse({'allData':allData})

def getDataGraphicNew(request,dataset_id,layer_name,operation,context,time_start,time_finish,latitude,longitude,range_value,latMin,longMin,latMax,longMax):
    allData=allFunctions.getDataGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude,longitude,0,range_value,0,latMin,longMin,latMax,longMax,operation=operation,context=context)
    return JsonResponse({'allData':allData})

def getDataGraphicCsv(request,dataset_id,layer_name,operation,context,time_start,time_finish,latitude,longitude,range_value,latMin,longMin,latMax,longMax):
    allData=allFunctions.getDataGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude,longitude,0,range_value,0,
                                               latMin,longMin,latMax,longMax,operation=operation,context=context,output="csv")
    return HttpResponse(
            content=allData,
            status=200,
            content_type="text/csv"
        )


def getDataGraphicPolygon(request,dataset_id,layer_name,operation,context,time_start,time_finish,latMin,longMin,latMax,longMax,range_value):
    allData=allFunctions.getDataGraphicGeneric(dataset_id,layer_name,time_start,time_finish,None,None,0,range_value,0,latMin,longMin,latMax,longMax,operation=operation,context=context,cache="yes")
    return JsonResponse({'allData':allData})


def getDataVectorial(request,dataset_id,layer_name,date_start,latitude_start,latitude_end,longitude_start,longitude_end,num_param,range_value,is_indicator):
    dataVect=allFunctions.getDataVectorial(dataset_id,layer_name,date_start,latitude_start,latitude_end,longitude_start,longitude_end,num_param,range_value,is_indicator)
    return JsonResponse({'dataVect':dataVect})

# def getWindArrows(request,datasetId1,datasetId2,layer_name1,date_start1,num_param1,range_value1,layer_name2,date_start2,latitude_start,latitude_end,longitude_start,longitude_end,num_param2,range_value2):
#     windArrows=allFunctions.createArrow(datasetId1,datasetId2,layer_name1,date_start1,num_param1,range_value1,layer_name2,date_start2,latitude_start,latitude_end,longitude_start,longitude_end,num_param2,range_value2)
#     return JsonResponse({'windArrows':windArrows})

def getDataExport(request,dataset_id,selectedType,layer_name,time_start,time_finish,latitude,longitude):
    urlCall=ERDDAP_URL+"griddap/"+dataset_id+"."+selectedType+"?"+layer_name+"%5B("+time_start+"):1:("+time_finish+")%5D%5B("+latitude+"):1:("+latitude+")%5D%5B("+longitude+"):1:("+longitude+")%5D"
    nameOfTheFile=dataset_id+"."+selectedType
    file_path = os.path.join(settings.MEDIA_ROOT, urlCall)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/"+selectedType)
            response['Content-Disposition'] = 'inline; filename=' + nameOfTheFile
            return response
    raise Http404

@csrf_exempt
def getTest(request):
    print("test")
    return JsonResponse({'test':'test'})

# @csrf_exempt
@api_view(['GET', 'POST'])
def getPippo(request):
    inputEs = request.data.get('inputEsterno')
    return JsonResponse({'pippo':'pippo'})

@api_view(['GET', 'POST'])
def getPluto(request):
    prova = Indicator.objects.get(dataset_id = "adriaclim_WRF_5e78_b419_ec8a")
    provaSer = serializers.serialize('json', [prova, ])
    provaJson = json.loads(provaSer)
    return JsonResponse({"pluto": provaJson})

@api_view(['GET', 'POST'])
def getInd(request):
    ind = Indicator.objects.all()
    data = [model_to_dict(i) for i in ind]
    return JsonResponse({"ind": data})

@api_view(['GET', 'POST'])
def getAllNodes(request):
    try:
        all_nodes = Node.objects.all()
        data = [model_to_dict(i) for i in all_nodes]
        return JsonResponse({"nodes": data})
    except Exception as e:
        print("ERRORE GET ALL NODES =", e)
        return str(e)

def rompiamo_tutto(request):
    try:
        allFunctions.rompo_tutto()
        return "Ho aggiustato tutto!!!!"
    except Exception as e:
        print("Ho rotto tutto!!!!! ",e)
        return str(e)
    
def download_big_data(request):
    try:
        allFunctions.download_big_data()
        return "Ho aggiustato tutto!!!!"
    except Exception as e:
        print("Ho rotto tutto!!!!! Final Version",e)
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
    data = allFunctions.getDataTable(dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value)
    return JsonResponse({"data":data})

@api_view(['GET','POST'])
def getDataGraphicNewCanvas(request):
    try:
        dataset_id = request.data.get("idMeta")
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
        allData = allFunctions.getDataGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude,longitude,0,range_value,0,lat_min,lng_min,lat_max,lng_max,operation=operation,context=context)
        if allData == "fuoriWms":
            return JsonResponse({"allData":allData})
        else:
            return JsonResponse({'allData':allData})
    except Exception as e:
        print("ERRORE:",e)
        return "fuoriWms"

@api_view(['GET','POST'])
def getDataVectorialNew(request):
    dataset = request.data.get("dataset")

    dataset_id = dataset.get('id')
    sel_date = str(request.data.get('selDate'))
    layer_name = request.data.get('selVar')
    num_param = dataset.get('variables')
    lat_min = dataset.get('lat_min')
    lat_max = dataset.get('lat_max')
    lng_min = dataset.get('lng_min')
    lng_max = dataset.get('lng_max')
    is_indicator = request.data.get('isIndicator')
    dataVect=allFunctions.getDataVectorial(dataset_id,layer_name,sel_date,lat_min,lat_max,lng_min,lng_max,num_param,0,is_indicator)
    return JsonResponse({'dataVect':dataVect})



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
        if task.status == 'SUCCESS':
            response['result'] = task.result
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
    new_values_calculated = allFunctions.updateStatistics(new_dates,new_values)
    return JsonResponse({"newValues":new_values_calculated})
