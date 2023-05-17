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


class Polygon(models.Model):

    pol_vertices_str = models.CharField(max_length=500,default="",null=True) 
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
