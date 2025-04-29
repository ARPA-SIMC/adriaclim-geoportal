import requests
from django.http import HttpResponse
from AdriaProject.settings import ERDDAP_URL

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
