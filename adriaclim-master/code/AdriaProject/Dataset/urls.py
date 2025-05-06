from django.urls import path
from .views import (
    getAllDatasets,
    dataset_id_wrong,
    getDataTable,
    getAllNodes,
    getMetadataNew,
    get_metadata_table,
    getDataTableNew,
)

urlpatterns = [
    path('getAllDatasets/', getAllDatasets, name='getAllDatasets'),
    path('dataset_id_wrong/', dataset_id_wrong, name='dataset_id_wrong'),
    path('getDataTable/', getDataTable, name='getDataTable'),
    path('getAllNodes/', getAllNodes, name='getAllNodes'),
    path('getMetadataNew/', getMetadataNew, name='getMetadataNew'),
    path('get_metadata_table/', get_metadata_table, name='get_metadata_table'),
    path('getDataTableNew/', getDataTableNew, name='getDataTableNew'),
]
