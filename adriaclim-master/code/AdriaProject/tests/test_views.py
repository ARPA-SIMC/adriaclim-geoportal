from django.test import TestCase, Client
from django.http import JsonResponse
from django.core import serializers
import json
from django.urls import reverse
from Dataset.models import Node
import Dataset.views as views

class TestViews(TestCase):

    def test_get_all_nodes(self):
        client = Client()

        response = client.get(reverse('getAllNodes'))
        self.assertEqual(response.status_code, 200)  # We are able to make a request to this view

        # Check if the response is a JsonResponse
        self.assertIsInstance(response, JsonResponse)

        # Check if the JsonResponse contains the key "nodes"
        json_data = response.json()
        self.assertIn("nodes", json_data)

        # Extract the "nodes" value 
        nodes_data = json_data["nodes"]
    
        # Check if the objects are instances of the Node model class
        self.assertTrue(all(isinstance(obj, Node) for obj in nodes_data))
    
def test_get_metadata_new(self):
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

    # Mock della funzione getMetadata
    def fake_get_metadata(idMeta):
        return {
            "metadata": [
                ["Dimensione", "Variabile"],
                ["lat", "temperature"],
                ["lon", "temperature"]
            ]
        }

    # Sostituiamo temporaneamente la funzione reale con il mock
    original_get_metadata = views.getMetadata
    views.getMetadata = fake_get_metadata

    try:
        client = Client()
        response = client.post(reverse('getMetadataNew'), {
            "idMeta": node.id
        })

        print("DEBUG RESPONSE:", response.content)

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("metadata", json_data)
        self.assertIsInstance(json_data["metadata"], list)
    finally:
        # Ripristina la funzione originale
        views.getMetadata = original_get_metadata
