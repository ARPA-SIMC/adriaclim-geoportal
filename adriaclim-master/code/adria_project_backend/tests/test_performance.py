import time
from django.test import TestCase, Client
from Dataset.models import Node
from django.urls import reverse
import Dataset.views as views  # aggiungi se non presente

class TestPerformance(TestCase):

    def setUp(self):
        # Crea un Node finto nel database per eseguire il test.
        self.node = Node.objects.create(
            id="atm_regional_eaf9_c559_9752",
            adriaclim_dataset="atm",
            adriaclim_model="model_1",
            adriaclim_timeperiod="2020-2030",
            adriaclim_scale="regional",
            adriaclim_type="projection",
            title="Performance Test Node",
            metadata_url="https://example.com/info",  # Placeholder, non usato realmente nel test.
            institution="CMCC",
            time_start="2020-01-01",
            time_end="2020-12-31",
            tabledap_url="https://example.com/tabledap"
        )
        self.client = Client()

    def test_metadata_response_time(self):
        """Misura il tempo di risposta della view getMetadataNew con dati simulati."""

        # Mock della funzione getMetadata per evitare query lente o download reali.
        # Questo permette di testare solo la velocità della view, eliminando i fattori esterni.
        def fake_get_metadata(idMeta):
            return {
                "metadata": [
                    ["Dimensione", "Variabile"],
                    ["lat", "temperature"],
                    ["lon", "temperature"]
                ]
            }
        original_get_metadata = views.getMetadata
        views.getMetadata = fake_get_metadata

        try:
            start_time = time.time()
            # Esegue la richiesta POST alla view con il Node finto.
            response = self.client.post(reverse('getMetadataNew'), {"idMeta": self.node.id})
            duration = time.time() - start_time

            # Verifica che la risposta sia corretta.
            self.assertEqual(response.status_code, 200)
            # Controlla che il tempo di risposta sia inferiore a 1 secondo (limite imposto dal test).
            self.assertLess(duration, 1.0, "API too slow (> 1s)")

        finally:
            # Ripristina la funzione originale per non interferire con altri test.
            views.getMetadata = original_get_metadata
