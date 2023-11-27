from django.test import TestCase, Client
from django.http import JsonResponse
from django.core import serializers
import json
from django.urls import reverse, resolve
from Dataset.models import Polygon, Node, Indicator

class TestViews(TestCase):

    def test_get_all_nodes(self):
        client = Client()

        response = client.get(reverse('get_all_nodes'))
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
        client = Client()
        all_nodes = Node.objects.all()
        for node in all_nodes:

            #if you need to pass argument in the request in the view you need to do a post 
            response = client.post(reverse('get_metadata_new'),{
                "idMeta": node.id
                })

            self.assertEquals(response.status_code, 200)
            self.assertIsInstance(response, JsonResponse)
            #the key is metadata
            json_metadata = response.json()
            self.assertIn('metadata', json_metadata)

            metadata_data = json_metadata["metadata"]
            self.assertIsInstance(metadata_data,list)

            #Check if the response is a list of 3 objects
            self.assertEqual(len(metadata_data),3)
            #check if each of the 3 objects is a list!
            self.assertTrue(all(isinstance(sub_metadata,list) for sub_metadata in metadata_data))
