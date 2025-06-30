from django.test import TestCase
from Dataset.models import Node

class TestNodeModel(TestCase):
    def test_node_creation(self):
        node = Node.objects.create(
            id="node123",
            adriaclim_dataset="climate_ds",
            adriaclim_model="model_abc",
            adriaclim_timeperiod="2030-2040",
            adriaclim_scale="regional",
            adriaclim_type="projection",
            title="Test Climate Node",
            metadata_url="https://example.com/info",
            institution="CMCC",
            time_start="2030-01-01",
            time_end="2040-01-01",
            tabledap_url="https://example.com/tabledap"
        )

        self.assertEqual(Node.objects.count(), 1)
        self.assertEqual(node.title, "Test Climate Node")
        self.assertEqual(node.adriaclim_model, "model_abc")
