from django.urls import path
from Dataset.views import get_metadata_table, getMetadataNew

urlpatterns = [
    path('getMetadataNew/', getMetadataNew, name='getMetadataNew'),
    path('get_metadata_table/', get_metadata_table, name='get_metadata_table'),
]