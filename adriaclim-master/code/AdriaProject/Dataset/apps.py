from django.apps import AppConfig
import os
from pathlib import Path



class DatasetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Dataset'

    def ready(self):
        from Dataset import dataset_manager
        from .models import Node
        print("Ci entro in init.py")
        if Node.objects.count() == 0:
            dataset_manager.getAllDatasets()
