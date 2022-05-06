from django.db import models

# Create your models here.
class Node(models.Model):
    id=models.CharField(max_length=600,primary_key=True)
    title=models.CharField(max_length=1500,null=False)
    metadata_url=models.CharField(max_length=1500,null=False)
    griddap_url=models.CharField(max_length=1500,null=True)
    wms=models.CharField(max_length=1500,null=True)
    institution=models.CharField(max_length=1500,null=True)
    
