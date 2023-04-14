from unittest.util import _MAX_LENGTH
from django.db import models

# Create your models here.
class Node(models.Model):
    id = models.CharField(primary_key=True,max_length=500,default="")
    adriaclim_dataset = models.CharField(max_length=500,default="")
    adriaclim_model = models.CharField(max_length=500,default="")
    adriaclim_timeperiod = models.CharField(max_length=500,default="")
    adriaclim_scale = models.CharField(max_length=500,default="")
    adriaclim_type = models.CharField(max_length=500,default="")
    title = models.CharField(max_length=1500,null=False)
    metadata_url = models.CharField(max_length=1500,default="")
    institution = models.CharField(max_length=300,default="")
    lat_min = models.CharField(max_length=300,default="",null=True)
    lat_max = models.CharField(max_length=300,default="",null=True)
    lng_min = models.CharField(max_length=300,default="",null=True)
    lng_max = models.CharField(max_length=300,default="",null=True)
    time_start = models.CharField(max_length=120,default="")
    time_end = models.CharField(max_length=120,default="")
    param_min = models.FloatField(default=0,null=True)
    param_max = models.FloatField(default=0,null=True)
    tabledap_url = models.CharField(max_length=250,default="")
    dimensions = models.IntegerField(default=0,null=True)
    dimension_names = models.CharField(max_length=1500,default="",null=True)
    variables = models.IntegerField(default=0,null=True)
    variable_names = models.CharField(max_length=1500,default="",null=True)
    griddap_url = models.CharField(max_length=250,default="",null=True)
    wms_url = models.CharField(max_length=500,default="",null=True)
    
class Indicator(models.Model):
    dataset_id = models.CharField(primary_key=True,max_length=500,default="")
    adriaclim_dataset = models.CharField(max_length=500,default="")
    adriaclim_model = models.CharField(max_length=500,default="")
    adriaclim_timeperiod = models.CharField(max_length=500,default="")
    adriaclim_scale = models.CharField(max_length=500,default="")
    adriaclim_type = models.CharField(max_length=500,default="")
    title = models.CharField(max_length=1500,null=False)
    metadata_url = models.CharField(max_length=1500,default="")
    institution = models.CharField(max_length=300,default="")
    lat_min = models.CharField(max_length=300,default="",null=True)
    lat_max = models.CharField(max_length=300,default="",null=True)
    lng_min = models.CharField(max_length=300,default="",null=True)
    lng_max = models.CharField(max_length=300,default="",null=True)
    param_min = models.FloatField(default=0,null=True)
    param_max = models.FloatField(default=0,null=True)
    time_start = models.CharField(max_length=120,default="")
    time_end = models.CharField(max_length=120,default="")
    tabledap_url = models.CharField(max_length=250,default="")
    dimensions = models.IntegerField(default=0,null=True)
    dimension_names = models.CharField(max_length=1500,default="",null=True)
    variables = models.IntegerField(default=0,null=True)
    variable_names = models.CharField(max_length=1500,default="",null=True)
    griddap_url = models.CharField(max_length=250,default="",null=True)
    wms_url = models.CharField(max_length=500,default="",null=True)

class Polygon(models.Model):
    #cosi se c'è cache hit, ci prendiamo il poligono e l'id in questione
    
    pol_vertices_str = models.CharField(max_length=500,default="",null=True) 
    # id = models.CharField(primary_key=True,max_length=600,default="")
    id = models.AutoField(primary_key=True)
    value_0 = models.FloatField(default=0,null=True)
    dataset_id = models.ForeignKey(Node,on_delete=models.CASCADE)
    date_value = models.CharField(max_length=500,default="",null=True)
    latitude = models.FloatField(default=0,null=True)
    longitude = models.FloatField(default=0,null=True)
    parametro_agg = models.CharField(max_length=500,default="",null=True)
    
    # DA AGGIUNGERE CASO TABLEDAP DOVE BISOGNA PRENDERE SOLO L'ULTIMA VARIABILE
    def __init__(self, *args, **kwargs):
        super(Polygon, self).__init__(*args, **kwargs)
        # print("Dataset ID:", self.dataset_id)
        node = self.dataset_id
        if node.variables > 1 and node.griddap_url != "":
            for i in range(1, node.variables):
                setattr(self, 'value_'+str(i), models.FloatField(default=0, null=True))
    
    class Meta:
        unique_together = (("dataset_id", "date_value", "latitude", "longitude"),)
    
    
    # def __init__(self, value=0, date_value=''):
    #     self.value = value
    #     self.date_value = date_value
     
    
    # def as_dict(self):
    #     return {'time': self.date_value, 'value': self.value, 'lat_lng': "(" + str(self.latitude) + "," + str(self.longitude) + ")"}
# class Cache(models.Model):   
#     url = models.TextField(primary_key=True)
#     value = models.TextField() 
#     start = models.DateTimeField(auto_now=True)