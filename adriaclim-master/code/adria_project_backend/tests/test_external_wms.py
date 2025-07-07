from unittest import TestCase
from unittest.mock import patch, Mock
from Dataset.external_wms import build_wms_url, fetch_wms_response
from django.http import HttpResponse, JsonResponse
from requests.exceptions import RequestException
import json

class TestBuildWMSUrl(TestCase):

    def test_build_wms_url_removes_none_values(self):
        base_url = "http://example.com/erddap"
        dataset_id = "test-dataset"
        params = {
            "service": "WMS",
            "request": "GetMap",
            "layers": "layer1",
            "styles": None,  # Questo parametro deve essere ignorato nella costruzione dell'URL.
            "format": "image/png"
        }

        url = build_wms_url(base_url, dataset_id, params)

        # Verifica che tutti i parametri validi siano presenti nell'URL.
        self.assertIn("service=WMS", url)
        self.assertIn("request=GetMap", url)
        self.assertIn("layers=layer1", url)
        self.assertIn("format=image%2Fpng", url)  # Verifica il corretto URL encoding.
        # Controlla che il parametro None sia stato rimosso.
        self.assertNotIn("styles=None", url)
        # Verifica che l'URL inizi correttamente con il prefisso previsto.
        self.assertTrue(url.startswith(f"{base_url}/wms/{dataset_id}?"))

        
class TestFetchWMSResponse(TestCase):

    @patch("Dataset.external_wms.requests.get")
    def test_fetch_wms_response_success(self, mock_get):
        # Simula una risposta valida dal servizio WMS.
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"fake image data"
        mock_response.headers = {"Content-Type": "image/png"}
        mock_get.return_value = mock_response

        response = fetch_wms_response("http://example.com/wms")

        # Verifica che la funzione restituisca correttamente una HttpResponse con i dati simulati.
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"fake image data")
        self.assertEqual(response["Content-Type"], "image/png")

    @patch("Dataset.external_wms.requests.get")
    def test_fetch_wms_response_error(self, mock_get):
        # Simula un errore di rete durante la richiesta al servizio WMS.
        mock_get.side_effect = RequestException("Server not reachable")

        response = fetch_wms_response("http://example.com/wms")

        # Verifica che la funzione gestisca l'errore e restituisca un JsonResponse con codice 500.
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertIn("error", data)

