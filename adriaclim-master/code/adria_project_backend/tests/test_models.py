from django.test import TestCase
from Dataset.models import Node

class TestNodeModel(TestCase):

    def test_node_creation(self):
        # Crea un'istanza del modello Node con tutti i campi principali compilati.
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

        # Verifica che il Node sia stato salvato correttamente nel database.
        self.assertEqual(Node.objects.count(), 1)
        # Controlla che i dati principali siano stati assegnati correttamente.
        self.assertEqual(node.title, "Test Climate Node")
        self.assertEqual(node.adriaclim_model, "model_abc")

