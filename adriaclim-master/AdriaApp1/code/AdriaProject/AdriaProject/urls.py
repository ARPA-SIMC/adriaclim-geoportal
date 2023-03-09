"""AdriaProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.urls import path
from Dataset import views as data_views
from Metadata import views as metadata_views
from Utente import views as utente_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path("AdriaApp/WMS/request",data_views.layers2D),
    path("AdriaApp/WMS/3D/<str:parameter>/request",data_views.layers3D),
    path("AdriaApp/WMS/overlays/<str:dataset_id>/request",data_views.overlays),
    path("administration",utente_views.index),
    path("administration/modify",utente_views.modify),
    path('admin/adminPage', admin.site.urls),
    path('',data_views.index,name="homepage"),
    path('getDataExport/<str:dataset_id>/<str:selectedType>/<str:layer_name>/<str:time_start>/<str:time_finish>/<str:latitude>/'+
    '<str:longitude>',data_views.getDataExport),
    path('getDataVectorial/<str:dataset_id>/<str:layer_name>/<str:date_start>/<str:latitude_start>/<str:latitude_end>/<str:longitude_start>/<str:longitude_end>/<int:num_param>/<int:range_value>/<str:is_indicator>',data_views.getDataVectorial),
    path('getWindArrows/<str:datasetId1>/<str:datasetId2>/<str:layer_name1>/<str:date_start1>/<int:num_param1>/<int:range_value1>/<str:layer_name2>/<str:date_start2>/<str:latitude_start>/<str:latitude_end>/<str:longitude_start>/<str:longitude_end>/<int:num_param2>/<int:range_value2>',data_views.getWindArrows),
    path('allDatasets',data_views.allDatasets),
    path('getMetadata/<str:dataset_id>',data_views.getMetadataUrl),

    path('getDataTable/<str:dataset_id>/<str:layer_name>/<str:time_start>/<str:time_finish>/<str:latitude>/<str:longitude>/<int:num_parameters>/<int:range_value>',data_views.getDataTable),
    
    path('getDataTableIndicator/<str:dataset_id>/<str:layer_name>/<str:time_start>/<str:time_finish>/<str:lat_min>/<str:lat_max>/<str:long_min>/<str:long_max>/<int:num_parameters>/<int:range_value>',data_views.getDataTableIndicator),
    
    path('getDataGraphic/<str:dataset_id>/<str:layer_name>/<str:time_start>/<str:time_finish>/<str:latitude1>/'+
    '<str:longitude1>/<int:num_parameters>/<int:range_value>/<str:is_indicator>/<str:latMin>/'+
    '<str:longMin>/<str:latMax>/<str:longMax>/',data_views.getDataGraphic),
    
    path('getDataGraphicNew/<str:dataset_id>/<str:layer_name>/<str:operation>/<str:context>/<str:time_start>/<str:time_finish>/<str:latitude>/'+
    '<str:longitude>/<int:range_value>/<str:latMin>/'+
    '<str:longMin>/<str:latMax>/<str:longMax>/',data_views.getDataGraphicNew),

    path('getDataGraphicCsv/<str:dataset_id>/<str:layer_name>/<str:operation>/<str:context>/<str:time_start>/<str:time_finish>/<str:latitude>/'+
    '<str:longitude>/<int:range_value>/<str:latMin>/'+
    '<str:longMin>/<str:latMax>/<str:longMax>/',data_views.getDataGraphicCsv),
    
    path('getDataGraphicPolygon/<str:dataset_id>/<str:layer_name>/<str:operation>/<str:context>/<str:time_start>/<str:time_finish>/<str:latMin>/'+
    '<str:longMin>/<str:latMax>/<str:longMax>/<int:range_value>',data_views.getDataGraphicPolygon),
    path('getDataAnnualPolygon/<str:dataset_id>/<str:layer_name>/<str:time_start>/<str:time_finish>/<str:latMin>/'+
    '<str:longMin>/<str:latMax>/<str:longMax>/<int:num_parameters>/<int:range_value>/<str:is_indicator>',data_views.getDataAnnualPolygon),
    path('getDataGraphicAnnual/<str:dataset_id>/<str:layer_name>/<str:time_start>/<str:time_finish>/<str:latitude1>/'+
    '<str:longitude1>/<str:latitude2>/<str:longitude2>/<str:latitude3>/<str:longitude3>/<int:num_parameters>/<int:range_value>/<str:is_indicator>/<str:latMin>/'+
    '<str:longMin>/<str:latMax>/<str:longMax>/',data_views.getDataGraphicAnnual),
     path('getDataGraphicIndicatorAnnual/<str:dataset_id>/<str:layer_name>/<str:latitude>/'+
    '<str:longitude>/<int:num_parameters>/<int:range_value>',data_views.getDataGraphicIndicatorAnnual),
    path('getMaxMomentGraphic/<str:dataset_id>/<str:layer_name>/<str:time_start>/<str:time_finish>/<str:latitude1>/'+
    '<str:longitude1>/<str:latitude2>/<str:longitude2>/<str:latitude3>/<str:longitude3>/<int:num_parameters>/<int:range_value>/<str:is_indicator>/<str:latMin>/'+
    '<str:longMin>/<str:latMax>/<str:longMax>/',data_views.getMaxMomentGraphic),
    path('getMinMomentGraphic/<str:dataset_id>/<str:layer_name>/<str:time_start>/<str:time_finish>/<str:latitude1>/'+
    '<str:longitude1>/<str:latitude2>/<str:longitude2>/<str:latitude3>/<str:longitude3>/<int:num_parameters>/<int:range_value>/<str:is_indicator>/<str:latMin>/'+
    '<str:longMin>/<str:latMax>/<str:longMax>/',data_views.getMinMomentGraphic),
    path('getMeanMomentGraphic/<str:dataset_id>/<str:layer_name>/<str:time_start>/<str:time_finish>/<str:latitude1>/'+
    '<str:longitude1>/<str:latitude2>/<str:longitude2>/<str:latitude3>/<str:longitude3>/<int:num_parameters>/<int:range_value>/<str:is_indicator>/<str:latMin>/'+
    '<str:longMin>/<str:latMax>/<str:longMax>/',data_views.getMeanMomentGraphic),
    path('getTenthPercentileGraphic/<str:dataset_id>/<str:layer_name>/<str:time_start>/<str:time_finish>/<str:latitude1>/'+
    '<str:longitude1>/<str:latitude2>/<str:longitude2>/<str:latitude3>/<str:longitude3>/<int:num_parameters>/<int:range_value>/<str:is_indicator>/<str:latMin>/'+
    '<str:longMin>/<str:latMax>/<str:longMax>/',data_views.getTenthPercentileGraphic),
    path('getNinetiethPercentileGraphic/<str:dataset_id>/<str:layer_name>/<str:time_start>/<str:time_finish>/<str:latitude1>/'+
    '<str:longitude1>/<str:latitude2>/<str:longitude2>/<str:latitude3>/<str:longitude3>/<int:num_parameters>/<int:range_value>/<str:is_indicator>/<str:latMin>/'+
    '<str:longMin>/<str:latMax>/<str:longMax>/',data_views.getNinetiethPercentileGraphic),
    path('getMedianaGraphic/<str:dataset_id>/<str:layer_name>/<str:time_start>/<str:time_finish>/<str:latitude1>/'+
    '<str:longitude1>/<str:latitude2>/<str:longitude2>/<str:latitude3>/<str:longitude3>/<int:num_parameters>/<int:range_value>/<str:is_indicator>/<str:latMin>/'+
    '<str:longMin>/<str:latMax>/<str:longMax>/',data_views.getMedianaGraphic),
    path('myFunctions/getMetadata/<str:title>',data_views.getMetadata),
    path("myFunctions/getWMS",data_views.getWMS),
    path("myFunctions/getTitle",data_views.getTitle),
    path("myFunctions/getIndicators",data_views.getIndicators),
    path("myFunctions/getAllDatasets",data_views.getAllDatasets),
    path("<str:dataset_id>",metadata_views.getMetadataForm),
    path("test/prova",data_views.getTest),
    path("test/pippo",data_views.getPippo),
    path("test/pluto",data_views.getPluto),
    path("test/ind",data_views.getInd),
    path("test/allNodes",data_views.getAllNodes),
    path("test/metadata",data_views.getMetadataNew),
    path("test/layers2d",data_views.layers2DNew),
    path('test/layers3d/<str:parameter>',data_views.layers3DNew),
    path("test/addOverlays/<str:dataset_id>",data_views.overlaysNew),
    path("test/metadataTable",data_views.get_metadata_table),
    path("test/dataGraphTable",data_views.getDataTableNew),
    path("test/dataGraphCanvas",data_views.getDataGraphicNewCanvas),
  
  
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

#handler500="Dataset.views.dataset_id_wrong"
