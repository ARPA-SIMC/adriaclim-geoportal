from django.contrib import admin
from .models import Node,Indicator,Polygon

# Register your models here.
admin.site.register(Node)
admin.site.register(Indicator)
admin.site.register(Polygon)