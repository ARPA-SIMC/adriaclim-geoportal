from django.conf import settings

def erddap_url(request):
    return {"ERDDAP_URL":settings.ERDDAP_URL}