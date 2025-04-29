from django.urls import path
from Dataset.views_datasets import (
    getDataGraphicNewCanvas,
    getDataVectorialNew,
    getDataPolygonNew,
    updateStatistics,
    compareDatasets,
    check_task_status,
    discover_mb_indicator,
)



urlpatterns = [
    path('getDataGraphic/', getDataGraphicNewCanvas, name='getDataGraphic'),
    path('getVectorial/', getDataVectorialNew, name='getDataVectorial'),
    path('getPolygon/', getDataPolygonNew, name='getDataPolygon'),
    path('updateStatistics/', updateStatistics, name='updateStatistics'),
    path('compareDatasets/', compareDatasets, name='compareDatasets'),
    path('taskStatus/', check_task_status, name='check_task_status'),
    path('discoverMb/', discover_mb_indicator, name='discover_mb_indicator'),
]