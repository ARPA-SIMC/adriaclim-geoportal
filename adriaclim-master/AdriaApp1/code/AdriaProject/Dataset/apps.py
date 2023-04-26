from django.apps import AppConfig


class DatasetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Dataset'

    def ready(self):
        from myFunctions import allFunctions
        from .models import Node
        print("Ci entro in init.py")
        if Node.objects.count() == 0:
            allFunctions.getAllDatasets()
