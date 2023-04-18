import json
from unittest.util import _MAX_LENGTH
from django.db import models
from postgres_copy import CopyManager,CopyMapping

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

#         class Meta:
#             abstract = True

#     # if self.dataset_id.variables > 1 and self.dataset_id.griddap_url !=  "":
#     if variables > 1 and griddap_url !=  "":
        
#         AbstractModel.add_to_class(
#             fields_prefix + '_title',
#             models.CharField(max_length=255, blank=True, default=''),
#         )
#     return AbstractModel
class Polygon(models.Model):

    pol_vertices_str = models.CharField(max_length=500,default="",null=True) 
    # id = models.CharField(primary_key=True,max_length=600,default="")
    id = models.AutoField(primary_key=True)
    value_0 = models.FloatField(default=0,null=True)
    dataset_id = models.ForeignKey(Node,on_delete=models.CASCADE)
    date_value = models.CharField(max_length=500,default="",null=True)
    latitude = models.FloatField(default=0,null=True)
    longitude = models.FloatField(default=0,null=True)
    parametro_agg = models.CharField(max_length=500,default="",null=True)
    objects = models.Manager()
    copy_manager = CopyManager()
    #     # DA AGGIUNGERE CASO TABLEDAP DOVE BISOGNA PRENDERE SOLO L'ULTIMA VARIABILE
    def add_attribute(self,value):
        setattr(self, value, models.FloatField(default=0, null=True))

    def __init__(self, *args, **kwargs):
        super(Polygon, self).__init__(*args, **kwargs)
        # print("Dataset ID:", self.dataset_id)
        node = self.dataset_id
        print("Sono in polygon",node.variables)
        if node.variables > 1 and node.griddap_url != "":
            print("Sono nel caso di più di una variabile",node.variables)
            print("node type",type(node))
            print("self type",type(self))

            for i in range(1, node.variables):
                setattr(self, 'value_'+str(i), models.FloatField(default=0, null=True))


class HookedCopyMapping(CopyMapping):

    # def execute(self, using=None, keep_null=False, ignore_conflicts=False, rows=None):
    #     self.pre_copy(self.cursor)
    #     self.copy(using=using, keep_null=keep_null, ignore_conflicts=ignore_conflicts)
    #     self.post_copy(self.cursor)
    #     self.pre_insert(self.cursor, rows=rows)  # Pass the rows argument
    #     self.insert()
    #     self.post_insert(self.cursor)
    def __init__(self,*args,**kwargs):
        print("entro quiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
        print("args",args)
        # poly_to_check = args[0]
        print("args[0] type",type(args[0]))
        args[0] = Polygon(dataset_id=args[3])
        # for key in args[2]:
        #     if "value_" in key and key != "value_0":
        #         print("key",key)
        #         poly_to_check.__init__(poly_to_check)
                
        
        print("poly_to_check test",args[0])
        # print("args 0",dir(args[0].date_value.field))
        # print("args 2",args[2])
        # print("self", dir(self))
        # dict_pol = self.__dict__
        # print("dict_pol",dict_pol)
        super(HookedCopyMapping,self).__init__(*args, **kwargs)
        
    def pre_copy(self):
        print("pre_copy!")
        # Doing whatever you'd like here

    def post_copy(self):
        print("post_copy!")
        # And here

    def pre_insert(self):
        # print("cursor",cursor)
        print("self",self)
        dict_pol = self.__dict__
        model_pol = dict_pol["model"]
        # model_pol.__init__(pol_vertices_str=model_pol.pol_vertices_str,
        #                    id=model_pol.id,
        #                    dataset_id=model_pol.dataset_id,
        #                    date_value=model_pol.date_value,
        #                    latitude=model_pol.latitude,
        #                    longitude=model_pol.longitude,
        #                    parametro_agg=model_pol.parametro_agg,
        #                    value_0=model_pol.value_0
        #                    )
        
        # print("polygon_instance",polygon_instance)
        # Call the __init__ method of Polygon model with required arguments
        # print("self_parame",self.field_map)
        # polygon_instance.__init__(pol_vertices_str=self.field_map['pol_vertices_str'],
        #                           id=self.field_map['id'],
        #                           value_0=self.field_map['value_0'],
        #                           dataset_id=self.field_map['dataset_id'],
        #                           date_value=self.field_map['date_value'],
        #                           latitude=self.field_map['latitude'],
        #                           longitude=self.field_map['longitude'],
        #                           parametro_agg=self.field_map['parametro_agg'])
        print("self.polygon",self.__init__)
        print("pre_insert!")
        # And here

    def post_insert(self):
        print("post_insert!")
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