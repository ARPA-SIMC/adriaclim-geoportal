from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError
import urllib.request


class DatasetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Dataset'

    def ready(self):
        try:
            from .dataset_manager import getAllDatasets
            from .models import Node

            # Tentiamo una connessione rapida all’ERDDAP
            erddap_url = "https://erddap-adriaclim.cmcc-opa.eu/erddap/info/index.csv"

            try:
                urllib.request.urlopen(erddap_url, timeout=5)
            except Exception as net_error:
                print(f"⚠️ ERDDAP non raggiungibile ({net_error}), skip importazione iniziale.")
                return

            if Node.objects.count() == 0:
                print("📥 Nessun dataset trovato, avvio importazione iniziale...")
                getAllDatasets()

        except (OperationalError, ProgrammingError):
            print("⚠️ Database non pronto. Skip inizializzazione automatica.")

# class DatasetConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'Dataset'

#     def ready(self):
#         try:
#             from .dataset_manager import getAllDatasets
#             from .models import Node
#             if Node.objects.count() == 0:
#                 print("📥 Nessun dataset trovato, avvio importazione iniziale...")
#                 getAllDatasets()
#         except (OperationalError, ProgrammingError):
#             # Le migrazioni non sono ancora state eseguite, quindi ignoro
#             print("⚠️ Database non pronto. Skip inizializzazione automatica.")

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
