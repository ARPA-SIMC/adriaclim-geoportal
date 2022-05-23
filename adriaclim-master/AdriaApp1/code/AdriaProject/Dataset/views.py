from django.http import response,request,Http404
from django.http.response import HttpResponse, JsonResponse,ResponseHeaders
from django.conf import settings
from django.shortcuts import render
from myFunctions import allFunctions
from .forms import DatasetForm
import requests
import os
from .models import Node

# Create your views here.
def index(request):
    form=DatasetForm()
    datasets=Node.objects.all()
    response=render(request,"homepage.html",{'ERDDAP_URL': settings.ERDDAP_URL, 'form':form,'datasets':datasets})
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
    url="http://erddap.cmcc-opa.eu/erddap/wms/"+dataset_id+"/request?&service="+service+"&request="+request1+"&layers="+layers+"&styles="+styles+"&format="+format+"&transparent="+transparent+"&version="+version+"&bgcolor="+bgcolor+"&width="+width+"&height="+height+"&crs="+crs+"&bbox="+bbox
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
    url="http://erddap.cmcc-opa.eu/erddap/wms/"+dataset_id+"/request?&service="+service+"&request="+request1+"&layers="+layers+"&styles="+styles+"&format="+format+"&transparent="+transparent+"&version="+version+"&bgcolor="+bgcolor+"&time="+time+"&width="+width+"&height="+height+"&crs="+crs+"&bbox="+bbox
    print(url)
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
    url="http://erddap.cmcc-opa.eu/erddap/wms/"+dataset_id+"/request?&service="+service+"&request="+request1+"&layers="+layers+"&styles="+styles+"&format="+format+"&transparent="+transparent+"&version="+version+"&bgcolor="+bgcolor+"&time="+time+"&"+parameter+"="+value_param+"&width="+width+"&height="+height+"&crs="+crs+"&bbox="+bbox
    print(url)
    requests_response = requests.get(url)
    django_response = HttpResponse(
            content=requests_response.content,
            status=requests_response.status_code,
            content_type=requests_response.headers['Content-Type']
        )
        
    return django_response



def allDatasets(request):
        allFunctions.listAllDatasets()
        return render(request,"allDatasets.html")

def getHighTemp(request):
    result=allFunctions.getHighTemperature()
    return JsonResponse({'result':result})

def getTitle(request):
    titles=allFunctions.getTitle()
    return JsonResponse({'title':titles})

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
    return HttpResponse(data)

def getDataGraphic(request,dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value):
    allData=allFunctions.getDataGraphic(dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value)
    return JsonResponse({'allData':allData})

def getDataVectorial(request,dataset_id,layer_name,date_start,latitude_start,latitude_end,longitude_start,longitude_end,num_param,range_value):
    dataVect=allFunctions.getDataVectorial(dataset_id,layer_name,date_start,latitude_start,latitude_end,longitude_start,longitude_end,num_param,range_value)
    return JsonResponse({'dataVect':dataVect})

def getWindArrows(request,datasetId1,datasetId2,layer_name1,date_start1,num_param1,range_value1,layer_name2,date_start2,latitude_start,latitude_end,longitude_start,longitude_end,num_param2,range_value2):
    windArrows=allFunctions.createArrow(datasetId1,datasetId2,layer_name1,date_start1,num_param1,range_value1,layer_name2,date_start2,latitude_start,latitude_end,longitude_start,longitude_end,num_param2,range_value2)
    return JsonResponse({'windArrows':windArrows})

def getDataExport(request,dataset_id,selectedType,layer_name,time_start,time_finish,latitude,longitude):
    urlCall="http://erddap.cmcc-opa.eu/erddap/griddap/"+dataset_id+"."+selectedType+"?"+layer_name+"%5B("+time_start+"):1:("+time_finish+")%5D%5B("+latitude+"):1:("+latitude+")%5D%5B("+longitude+"):1:("+longitude+")%5D"
    print(urlCall)
    nameOfTheFile=dataset_id+"."+selectedType
    file_path = os.path.join(settings.MEDIA_ROOT, urlCall)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/"+selectedType)
            response['Content-Disposition'] = 'inline; filename=' + nameOfTheFile
            return response
    raise Http404
