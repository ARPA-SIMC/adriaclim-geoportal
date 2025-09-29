import logging
import urllib.request
from django.conf import settings


from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

logger = logging.getLogger(__name__)
class DatasetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Dataset'

    def ready(self):
        try:
            from .dataset_manager import getAllDatasets
            from .models import Node

            erddap_url = f"{settings.ERDDAP_URL}/info/index.csv"

            try:
                urllib.request.urlopen(erddap_url, timeout=5)
            except Exception as net_error:
                logger.warning(f"ERDDAP non raggiungibile ({net_error}), skip importazione iniziale.")
                return

            if Node.objects.count() == 0:
                logger.info("Nessun dataset trovato, avvio importazione iniziale...")
                getAllDatasets()

        except (OperationalError, ProgrammingError):
            logger.warning("Database non pronto. Skip inizializzazione automatica.")

