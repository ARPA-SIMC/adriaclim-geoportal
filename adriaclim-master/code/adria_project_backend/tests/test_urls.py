from django.test import SimpleTestCase
from django.urls import reverse, resolve
from Dataset.views import getAllNodes,get_metadata_table

class TestUrls(SimpleTestCase):
    
    def test_all_nodes(self):
        url = reverse('getAllNodes')
        # Verifica che la URL 'getAllNodes' punti correttamente alla funzione getAllNodes.
        self.assertEquals(resolve(url).func, getAllNodes)

    def test_get_metadata_table(self):
        url = reverse('get_metadata_table')
        # Verifica che la URL 'get_metadata_table' punti correttamente alla funzione get_metadata_table.
        self.assertEquals(resolve(url).func, get_metadata_table)


