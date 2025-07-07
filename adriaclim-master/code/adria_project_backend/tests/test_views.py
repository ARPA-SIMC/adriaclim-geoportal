from django.test import TestCase, Client
from django.http import JsonResponse
from django.core import serializers
import json
import time
from django.urls import reverse
from Dataset.models import Node
import Dataset.views as views
from unittest.mock import patch

class TestViews(TestCase):

    def test_get_all_nodes(self):
        client = Client()

        # Esegue una richiesta GET alla view 'getAllNodes'.
        response = client.get(reverse('getAllNodes'))
        self.assertEqual(response.status_code, 200)  # La view deve rispondere correttamente.

        # Verifica che la risposta sia di tipo JsonResponse.
        self.assertIsInstance(response, JsonResponse)

        # Controlla che la risposta contenga la chiave 'nodes'.
        json_data = response.json()
        self.assertIn("nodes", json_data)

        # Estrae i dati dei nodi.
        nodes_data = json_data["nodes"]
    
        # Verifica che tutti gli oggetti in 'nodes' siano istanze del modello Node.
        # Nota: questa verifica funziona solo se i dati restituiti sono oggetti Node, non dizionari serializzati.
        self.assertTrue(all(isinstance(obj, Node) for obj in nodes_data))
    
def test_get_metadata_new(self):
    # Crea un Node di test nel database.
    node = Node.objects.create(
        id="test_id",
        adriaclim_dataset="temp_ds",
        adriaclim_model="model_1",
        adriaclim_timeperiod="2020-2030",
        adriaclim_scale="regional",
        adriaclim_type="projection",
        title="Test Dataset",
        metadata_url="https://example.com/info",
        institution="CMCC",
        time_start="2020-01-01",
        time_end="2020-12-31",
        tabledap_url="https://example.com/tabledap"
    )

    # Mock della funzione getMetadata per evitare chiamate reali e velocizzare il test.
    def fake_get_metadata(idMeta):
        return {
            "metadata": [
                ["Dimensione", "Variabile"],
                ["lat", "temperature"],
                ["lon", "temperature"]
            ]
        }

    # Sostituisce temporaneamente la funzione reale con il mock.
    original_get_metadata = views.getMetadata
    views.getMetadata = fake_get_metadata

    try:
        client = Client()
        # Esegue una richiesta POST alla view 'getMetadataNew' passando l'ID del Node.
        response = client.post(reverse('getMetadataNew'), {
            "idMeta": node.id
        })

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("metadata", json_data)
        self.assertIsInstance(json_data["metadata"], list)
    finally:
        # Ripristina la funzione originale per non influenzare altri test.
        views.getMetadata = original_get_metadata

        
class TestOverlays(TestCase):
    def setUp(self):
        self.client = Client()
        self.dataset_id = "atm_regional_eaf9_c559_9752"  # ID del dataset di test (anche se privo di WMS).


@patch('Dataset.external_wms.fetch_wms_response')
def test_get_overlays(self, mock_fetch):
    # Simula una risposta del WMS con dati finti per evitare chiamate reali.
    mock_fetch.return_value = JsonResponse({"overlay": "mocked response"})

    # Esegue una richiesta GET alla view 'get_overlays_new' passando tutti i parametri necessari.
    response = self.client.get(
        reverse('get_overlays_new', args=[self.dataset_id]),
        {
            "service": "WMS",
            "request": "GetMap",
            "version": "1.3.0",
            "layers": "layer1",
            "styles": "",
            "format": "image/png",
            "transparent": "true",
            "width": "256",
            "height": "256",
            "srs": "EPSG:4326",
            "bbox": "0,0,10,10",
            "bgcolor": "0xFFFFFF"
        }
    )

    # Verifica che la risposta sia corretta e contenga la chiave 'overlay'.
    self.assertEqual(response.status_code, 200)
    self.assertIn("overlay", response.json())

