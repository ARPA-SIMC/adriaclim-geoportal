import time
from django.test import TestCase, Client
from Dataset.models import Node
from django.urls import reverse
import Dataset.views as views  # aggiungi se non presente

class TestPerformance(TestCase):
    def setUp(self):
        self.node = Node.objects.create(
            id="atm_regional_eaf9_c559_9752",
            adriaclim_dataset="atm",
            adriaclim_model="model_1",
            adriaclim_timeperiod="2020-2030",
            adriaclim_scale="regional",
            adriaclim_type="projection",
            title="Performance Test Node",
            metadata_url="https://example.com/info",  # placeholder, non usato dal mock
            institution="CMCC",
            time_start="2020-01-01",
            time_end="2020-12-31",
            tabledap_url="https://example.com/tabledap"
        )
        self.client = Client()

    def test_metadata_response_time(self):
        """Measure response time of getMetadataNew with mocked data"""
        
        # Mock temporaneo
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
            response = self.client.post(reverse('getMetadataNew'), {"idMeta": self.node.id})
            duration = time.time() - start_time

            print(f"⏱️ MetadataNew response time: {duration:.3f} seconds")
            print("🔴 Response content:", response.content)

            self.assertEqual(response.status_code, 200)
            self.assertLess(duration, 1.0, "⚠️ API too slow (> 1s)")

        finally:
            views.getMetadata = original_get_metadata  # ripristina