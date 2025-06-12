import urllib.request

from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

class DatasetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Dataset'

    def ready(self):
        try:
            from .dataset_manager import getAllDatasets
            from .models import Node

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

