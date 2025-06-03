from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError




class DatasetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Dataset'

    def ready(self):
        try:
            from .dataset_manager import getAllDatasets
            from .models import Node
            if Node.objects.count() == 0:
                print("📥 Nessun dataset trovato, avvio importazione iniziale...")
                getAllDatasets()
        except (OperationalError, ProgrammingError):
            # Le migrazioni non sono ancora state eseguite, quindi ignoro
            print("⚠️ Database non pronto. Skip inizializzazione automatica.")

    # def ready(self):
    #     from .dataset_manager import getAllDatasets
    #     from .models import Node
    #     print("Ci entro in init.py")
    #     if Node.objects.count() == 0:
    #         getAllDatasets()
            


# from django.apps import AppConfig
# import os
# from pathlib import Path



# class DatasetConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'Dataset'

#     def ready(self):
#         from Dataset import dataset_manager
#         from .models import Node
#         print("Ci entro in init.py")
#         if Node.objects.count() == 0:
#             dataset_manager.getAllDatasets()
