import requests
from django.http import HttpResponse, JsonResponse
from AdriaProject.settings import ERDDAP_URL

def build_wms_url(base_url, dataset_id, params):
    """Helper function to construct the WMS URL."""
    query_string = "&".join(f"{key}={value}" for key, value in params.items())
    return f"{base_url}/wms/{dataset_id}/request?{query_string}"

def fetch_wms_response(url):
    """Helper function to fetch WMS response and handle errors."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return HttpResponse(
            content=response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'application/octet-stream')
        )
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)

def layers2DNew(request):
    """Handles 2D layer requests."""
    params = {
        'service': request.GET.get('service'),
        'request': request.GET.get('request'),
        'layers': request.GET.get('layers'),
        'styles': request.GET.get('styles'),
        'format': request.GET.get('format'),
        'transparent': request.GET.get('transparent'),
        'version': request.GET.get('version'),
        'width': request.GET.get('width'),
        'height': request.GET.get('height'),
        'crs': request.GET.get('crs'),
        'bbox': request.GET.get('bbox'),
        'time': request.GET.get('time'),
        'bgcolor': request.GET.get('bgcolor'),
    }
    dataset_id = params['layers'].partition(":")[0]
    url = build_wms_url(ERDDAP_URL, dataset_id, params)
    return fetch_wms_response(url)

def layers3DNew(request, parameter):
    """Handles 3D layer requests."""
    params = {
        'service': request.GET.get('service'),
        'request': request.GET.get('request'),
        'layers': request.GET.get('layers'),
        'styles': request.GET.get('styles'),
        'format': request.GET.get('format'),
        'transparent': request.GET.get('transparent'),
        'version': request.GET.get('version'),
        'width': request.GET.get('width'),
        'height': request.GET.get('height'),
        'crs': request.GET.get('crs'),
        'bbox': request.GET.get('bbox'),
        'time': request.GET.get('time'),
        'bgcolor': request.GET.get('bgcolor'),
        parameter: request.GET.get(parameter),
    }
    dataset_id = params['layers'].partition(":")[0]
    url = build_wms_url(ERDDAP_URL, dataset_id, params)
    return fetch_wms_response(url)

def overlaysNew(request, dataset_id):
    """Handles overlay requests."""
    params = {
        'service': request.GET.get('service'),
        'request': request.GET.get('request'),
        'layers': request.GET.get('layers'),
        'styles': request.GET.get('styles'),
        'format': request.GET.get('format'),
        'transparent': request.GET.get('transparent'),
        'version': request.GET.get('version'),
        'width': request.GET.get('width'),
        'height': request.GET.get('height'),
        'crs': request.GET.get('crs'),
        'bbox': request.GET.get('bbox'),
        'bgcolor': request.GET.get('bgcolor'),
    }
    url = build_wms_url(ERDDAP_URL, dataset_id, params)
    return fetch_wms_response(url)








