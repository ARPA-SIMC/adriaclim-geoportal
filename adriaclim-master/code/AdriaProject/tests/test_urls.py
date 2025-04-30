from django.test import SimpleTestCase
from django.urls import reverse, resolve
from Dataset.views import getAllNodes,get_metadata_table,overlaysNew

class TestUrls(SimpleTestCase):
    
    def test_all_nodes(self):
        url = reverse('get_all_nodes')
        # print("url resolve====",resolve(url))
        #in func is present the Dataset.views.getAllNodes that is the one that is called with the name get_all_nodes
        # we can try to see if it is really this one, testing in this way:
        self.assertEquals(resolve(url).func,getAllNodes)  

    def test_get_metadata_table(self):
        url = reverse('get_metadata_table')
        self.assertEquals(resolve(url).func,get_metadata_table)
    
    def test_get_overlays(self):
        url = reverse('get_overlays_new',args=["atm_regional_eaf9_c559_9752"]) #if you need to pass arguments to the function, you need to pass args=[argument1,argument2,...]
        self.assertEquals(resolve(url).func,overlaysNew)


