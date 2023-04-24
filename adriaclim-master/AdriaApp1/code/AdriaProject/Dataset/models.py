import json
from unittest.util import _MAX_LENGTH
from django.contrib.gis.db import models
from postgres_copy import CopyManager


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

########################################################################################################################
# class Polygon(models.Model):
#     #cosi se c'è cache hit, ci prendiamo il poligono e l'id in questione
    
#     pol_vertices_str = models.CharField(max_length=500,default="",null=True) 
#     # id = models.CharField(primary_key=True,max_length=600,default="")
#     id = models.AutoField(primary_key=True)
#     value_0 = ArrayField(
#         models.FloatField(default=0,null=True),
#         default=list,
#         blank=True
#     )
#     # value_1 = ArrayField(models.FloatField(default=0, null=True, blank=True) blank=True, null=True, default=list)
#     # value_1 = models.FloatField(default=0,null=True)
#     dataset_id = models.ForeignKey(Node,on_delete=models.CASCADE)
#     date_value = models.CharField(max_length=500,default="",null=True)
#     latitude = models.FloatField(default=0,null=True)
#     longitude = models.FloatField(default=0,null=True)
#     parametro_agg = models.CharField(max_length=500,default="",null=True)
#     objects = models.Manager()
#     copy_manager = CopyManager()
#     # DA AGGIUNGERE CASO TABLEDAP DOVE BISOGNA PRENDERE SOLO L'ULTIMA VARIABILE
#     # def __init__(self, *args, **kwargs):
#     #     super(Polygon, self).__init__(*args, **kwargs)
#     #     # print("Dataset ID:", self.dataset_id)
#     #     node = self.dataset_id
#     #     print("Sono in polygon",node.variables)
#     #     if node.variables > 1 and node.griddap_url != "":
#     #         print("Sono nel caso di più di una variabile",node.variables)
#     #         for i in range(1, node.variables):
#     #             setattr(self, 'value_'+str(i), models.FloatField(default=0, null=True))
########################################################################################################################

# def dynamic_fieldname_model_factory(fields_prefix,variables,griddap_url):
#     class AbstractModel(models.Model):

        # class Meta:
        #     abstract = True

#     # if self.dataset_id.variables > 1 and self.dataset_id.griddap_url !=  "":
#     if variables > 1 and griddap_url !=  "":
        
#         AbstractModel.add_to_class(
#             fields_prefix + '_title',
#             models.CharField(max_length=255, blank=True, default=''),
#         )
#     return AbstractModel
#Everything worked fine but in models.py when I try to add a PointField after putting in settings.py in INSTALLED_APPS django.contrib.gis and importing in models.py 'from django.contrib.gis.db import models', it is returning me this error 'AttributeError: 'DatabaseOperations' object has no attribute 'geo_db_type''

class Polygon(models.Model):

    pol_vertices_str = models.CharField(max_length=500,default="",null=True) 
    # id = models.CharField(primary_key=True,max_length=600,default="")
    id = models.AutoField(primary_key=True)
    value_0 = models.FloatField(default=None,null=True)
    value_1 = models.FloatField(default=None,null=True)
    value_2 = models.FloatField(default=None,null=True)
    value_3 = models.FloatField(default=None,null=True)
    value_4 = models.FloatField(default=None,null=True)
    value_5 = models.FloatField(default=None,null=True)
    value_6 = models.FloatField(default=None,null=True)
    value_7 = models.FloatField(default=None,null=True)
    value_8 = models.FloatField(default=None,null=True)
    value_9 = models.FloatField(default=None,null=True)
    value_10 = models.FloatField(default=None,null=True)
    value_11 = models.FloatField(default=None,null=True)
    value_12 = models.FloatField(default=None,null=True)
    value_13 = models.FloatField(default=None,null=True)
    value_14 = models.FloatField(default=None,null=True)
    value_15 = models.FloatField(default=None,null=True)
    value_16 = models.FloatField(default=None,null=True)
    value_17 = models.FloatField(default=None,null=True)
    value_18 = models.FloatField(default=None,null=True)
    value_19 = models.FloatField(default=None,null=True)
    value_20 = models.FloatField(default=None,null=True)
    value_21 = models.FloatField(default=None,null=True)
    value_22 = models.FloatField(default=None,null=True)
    value_23 = models.FloatField(default=None,null=True)
    value_24 = models.FloatField(default=None,null=True)
    value_25 = models.FloatField(default=None,null=True)
    dataset_id = models.ForeignKey(Node,on_delete=models.CASCADE)
    date_value = models.CharField(max_length=500,default="",null=True)
    latitude = models.FloatField(default=0,null=True)
    longitude = models.FloatField(default=0,null=True)
    coordinate = models.PointField(null=True,srid=4326)
    parametro_agg = models.CharField(max_length=500,default="",null=True)
    objects = models.Manager()
    copy_manager = CopyManager()
    #     # DA AGGIUNGERE CASO TABLEDAP DOVE BISOGNA PRENDERE SOLO L'ULTIMA VARIABILE
    # def add_attribute(self, attribute):
    #     print("Ci entrooooooooooooo")
    #     print("attribute",attribute)
    #     print("value type",type(attribute))
    #     # self.__setattr__(str(attribute), models.FloatField(default=0, null=True))
    #     # self.__setattr__(str(attribute), value)
    #     field = models.FloatField(default=0, null=True)
    #     self.add_to_class(str(attribute), field)

    # def add_field_to_person_model():
    #     model_class = apps.get_model('myapp', 'Person')
    #     field = models.IntegerField()
    #     model_class.add_to_class('age', field)
        # setattr(self, str(value), models.FloatField(default=0, null=True))

    # def __init__(self, *args, **kwargs):
    #     super(Polygon, self).__init__(*args, **kwargs)
    #     # print("Dataset ID:", self.dataset_id)
    #     node = self.dataset_id
    #     print("Sono in polygon",node.variables)
    #     if node.variables > 1 and node.griddap_url != "":
    #         print("Sono nel caso di più di una variabile",node.variables)
    #         print("node type",type(node))
    #         print("self type",type(self))

    #         for i in range(1, node.variables):
    #             setattr(self, 'value_'+str(i), models.FloatField(default=0, null=True))

        # And finally here
    # class Meta:
    #     unique_together = ("dataset_id", "date_value", "latitude", "longitude")
    
    # mi da questo errore pre_insert() missing 2 required positional arguments: 'cursor' and 'rows'
    # def __init__(self, value=0, date_value=''):
    #     self.value = value
    #     self.date_value = date_value
     
    
    # def as_dict(self):
    #     return {'time': self.date_value, 'value': self.value, 'lat_lng': "(" + str(self.latitude) + "," + str(self.longitude) + ")"}
# class Cache(models.Model):   
#     url = models.TextField(primary_key=True)
#     value = models.TextField() 
#     start = models.DateTimeField(auto_now=True)