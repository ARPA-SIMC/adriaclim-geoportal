from unittest.util import _MAX_LENGTH
from django.db import models

# Create your models here.
class Node(models.Model):
    id=models.CharField(max_length=600,primary_key=True)
    title=models.CharField(max_length=1500,null=False)
    metadata_url=models.CharField(max_length=1500,null=False)
    griddap_url=models.CharField(max_length=1500,null=True)
    wms=models.CharField(max_length=1500,null=True)
    institution=models.CharField(max_length=1500,null=True)
    
class Indicator(models.Model):
    dataset_id = models.CharField(primary_key=True,max_length=500)
    adriaclim_dataset = models.CharField(max_length=500)
    adriaclim_model = models.CharField(max_length=500)
    adriaclim_timeperiod = models.CharField(max_length=500)
    adriaclim_scale = models.CharField(max_length=500)
    adriaclim_type = models.CharField(max_length=500)
    title = models.CharField(max_length=1500,null=False)
    metadata_url = models.CharField(max_length=1500,default="")
    institution = models.CharField(max_length=300,default="")
    time_start = models.CharField(max_length=120,default="")
    time_end = models.CharField(max_length=120,default="")
    tabledap_url = models.CharField(max_length=250,default="")
    dimensions = models.IntegerField(default=0)
    dimension_names = models.CharField(max_length=500,default="")
    variables = models.IntegerField(default=0)
    variable_names = models.CharField(max_length=500,default="")
    griddap_url = models.CharField(max_length=250,default="")
    wms_url = models.CharField(max_length=500,default="")

class Cache(models.Model):   
    url = models.TextField(primary_key=True)
    value = models.TextField() 
    start = models.DateTimeField(auto_now=True)