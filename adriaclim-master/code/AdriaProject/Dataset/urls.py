from django.urls import path
from .external_wms import overlaysNew, layers2DNew, layers3DNew
from .views import (
    allDatasets,
    dataset_id_wrong,
    getDataTable,
    getAllNodes,
    getMetadataNew,
    get_metadata_table,
    getDataTableNew,
    getDataPolygonNew,
    getDataGraphicNewCanvas,
    getDataVectorialNew,
    updateStatistics,
    compareDatasets,
    check_task_status,
    
)

urlpatterns = [
    path('allDatasets/', allDatasets, name='allDatasets'),
    # path('dataset_id_wrong/', dataset_id_wrong, name='dataset_id_wrong'),
    # path('getDataTable/', getDataTable, name='getDataTable'),
    path('getAllNodes/', getAllNodes, name='getAllNodes'),
    path('getMetadataNew/', getMetadataNew, name='getMetadataNew'),
    path('get_metadata_table/', get_metadata_table, name='get_metadata_table'),
    path('getDataTableNew/', getDataTableNew, name='getDataTableNew'),
    path('getOverlaysNew/<str:dataset_id>/', overlaysNew, name='get_overlays_new'),
    path("layers2DNew/", layers2DNew, name = "layers2d"),
    path('layers3DNew/<str:parameter>', layers3DNew, name = "layers3d"),
    path('getDataPolygonNew/', getDataPolygonNew, name='getDataPolygon'),
    path('getDataGraphicNewCanvas/', getDataGraphicNewCanvas, name='getDataGraphic'),
    path('getDataVectorialNew/', getDataVectorialNew, name='getDataVectorial'),
    path('updateStatistics/', updateStatistics, name='updateStatistics'),
    path('compareDatasets/', compareDatasets, name='compareDatasets'),
    path('check_task_status/', check_task_status, name='check_task_status'),
    # path("pluto", getPluto),
    # path("ind", getInd),
]


