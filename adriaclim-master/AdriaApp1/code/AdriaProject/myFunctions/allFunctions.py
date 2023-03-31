import math
from pydoc import resolve
from math import isnan
from termios import VLNEXT
from django.db import models
from Dataset.models import Node,Indicator #,Cache
import pandas as pd
import csv
import urllib
from Utente.models import Utente
import numpy as np 
import os
import re
import io
import time
import json
import requests
from django.contrib import messages
from AdriaProject.settings import ERDDAP_URL
from django.core.cache import cache
from asgiref.sync import sync_to_async
import datetime as dt
from collections import defaultdict
from ipyleaflet import Polygon
from shapely.geometry import Point, Polygon as ShapelyPolygon 
 
htmlGetMetadata = """<style>
@import "https://fonts.googleapis.com/css?family=Montserrat:300,400,700";
@import "https://cdn.jsdelivr.net/npm/bootstrap@5.1.1/dist/css/bootstrap.min.css";
.rwd-table {
  margin: 1em 0;
  min-width: 300px;
}
.rwd-table tr {
  border-top: 1px solid #ddd;
  border-bottom: 1px solid #ddd;
}
.rwd-table th {
  display: none;
}
.rwd-table td {
  display: block;
}
.rwd-table td:first-child {
  padding-top: .5em;
}
.rwd-table td:last-child {
  padding-bottom: .5em;
}
.rwd-table td:before {
  content: attr(data-th) ": ";
  font-weight: bold;
  width: 6.5em;
  display: inline-block;
}

@media (min-width: 480px) {
  .rwd-table td:before {
    display: none;
  }
}
.rwd-table th, .rwd-table td {
  text-align: left;
}
@media (min-width: 480px) {
  .rwd-table th, .rwd-table td {
    display: table-cell;
    padding: .25em .5em;
  }
  .rwd-table th:first-child, .rwd-table td:first-child {
    padding-left: 0;
  }
  .rwd-table th:last-child, .rwd-table td:last-child {
    padding-right: 0;
  }
}
 
 
h1 {
  font-weight: normal;
  letter-spacing: -1px;
  color: #34495E;
}
 
.rwd-table {
  background: #34495E;
  color: #fff;
  border-radius: .4em;
  overflow: hidden;
}
.rwd-table tr {
  border-color: #46637f;
}
.rwd-table th, .rwd-table td {
  margin: .5em 1em;
}
@media (min-width: 480px) {
  .rwd-table th, .rwd-table td {
    padding: 1em !important;
  }
}
.rwd-table th, .rwd-table td:before {
  color: #dd5;
}
</style>
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="/">Homepage</a></li>
    <li class="breadcrumb-item active" aria-current="page">Get Metadata Of A Specific Dataset</li>
  </ol>
</nav>
<script>
  window.console = window.console || function(t) {};
</script>
<script>
  if (document.location.search.match(/type=embed/gi)) {
    window.parent.postMessage("resize", "*");
  }
</script>"""

htmlGetAllDatasets = """<style>
@import "https://fonts.googleapis.com/css?family=Montserrat:300,400,700";
@import "https://cdn.jsdelivr.net/npm/bootstrap@5.1.1/dist/css/bootstrap.min.css";
.rwd-table {
  margin: 1em 0;
  min-width: 300px;
}
.rwd-table tr {
  border-top: 1px solid #ddd;
  border-bottom: 1px solid #ddd;
}
.rwd-table th {
  display: none;
}
.rwd-table td {
  display: block;
}
.rwd-table td:first-child {
  padding-top: .5em;
}
.rwd-table td:last-child {
  padding-bottom: .5em;
}
.rwd-table td:before {
  content: attr(data-th) ": ";
  font-weight: bold;
  width: 6.5em;
  display: inline-block;
}
.rwd-table tr:first-child{
    color:#dd5;
    font-weight:bold;
}
@media (min-width: 480px) {
  .rwd-table td:before {
    display: none;
  }
}
.rwd-table th, .rwd-table td {
  text-align: left;
}
@media (min-width: 480px) {
  .rwd-table th, .rwd-table td {
    display: table-cell;
    padding: .25em .5em;
  }
  .rwd-table th:first-child, .rwd-table td:first-child {
    padding-left: 0;
  }
  .rwd-table th:last-child, .rwd-table td:last-child {
    padding-right: 0;
  }
}
 
 
h1 {
  font-weight: normal;
  letter-spacing: -1px;
  color: #34495E;
}
 
.rwd-table {
  background: #34495E;
  color: #fff;
  border-radius: .4em;
  overflow: hidden;
}
.rwd-table tr {
  border-color: #46637f;
}
.rwd-table th, .rwd-table td {
  margin: .5em 1em;
}
@media (min-width: 480px) {
  .rwd-table th, .rwd-table td {
    padding: 1em !important;
  }
}
.rwd-table th, .rwd-table td:before {
  color: #dd5;
}
</style>
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="/">Homepage</a></li>
    <li class="breadcrumb-item active" aria-current="page">Get The List Of All The Datasets</li>
  </ol>
</nav>
<script>
  window.console = window.console || function(t) {};
</script>
<script>
  if (document.location.search.match(/type=embed/gi)) {
    window.parent.postMessage("resize", "*");
  }
</script>"""

htmlGetData="""<style>
@import "https://fonts.googleapis.com/css?family=Montserrat:300,400,700";
@import "https://cdn.jsdelivr.net/npm/bootstrap@5.1.1/dist/css/bootstrap.min.css";
.rwd-table {
  margin: 1em 0;
  min-width: 300px;
}
.rwd-table tr {
  border-top: 1px solid #ddd;
  border-bottom: 1px solid #ddd;
}
.rwd-table th {
  display: none;
}
.rwd-table td {
  display: block;
}
.rwd-table td:first-child {
  padding-top: .5em;
}
.rwd-table td:last-child {
  padding-bottom: .5em;
}
.rwd-table td:before {
  content: attr(data-th) ": ";
  font-weight: bold;
  width: 6.5em;
  display: inline-block;
}
@media (min-width: 480px) {
  .rwd-table td:before {
    display: none;
  }
}
.rwd-table th, .rwd-table td {
  text-align: left;
}
@media (min-width: 480px) {
  .rwd-table th, .rwd-table td {
    display: table-cell;
    padding: .25em .5em;
  }
  .rwd-table th:first-child, .rwd-table td:first-child {
    padding-left: 0;
  }
  .rwd-table th:last-child, .rwd-table td:last-child {
    padding-right: 0;
  }
}


h1 {
  font-weight: normal;
  letter-spacing: -1px;
  color: #34495E;
}

.rwd-table {
  background: #34495E;
  color: #fff;
  border-radius: .4em;
  overflow: hidden;
}
.rwd-table tr {
  border-color: #46637f;
}
.rwd-table tr:first-child{
    color:#dd5;
    font-weight:bold;
}
.rwd-table th, .rwd-table td {
  margin: .5em 1em;
}
@media (min-width: 480px) {
  .rwd-table th, .rwd-table td {
    padding: 1em !important;
  }
}
.rwd-table th, .rwd-table td:before {
  color: #dd5;
}
</style>
<script>
  window.console = window.console || function(t) {};
</script>
<script>
  if (document.location.search.match(/type=embed/gi)) {
    window.parent.postMessage("resize", "*");
  }
</script>"""
x=500000

#I need to save in the cache the url and corresponding value!

def download_with_cache(u):
    cache_key = u # needs to be unique
    cache_time = 43200 # time in seconds for cache to be valid (now it is 12 hours)
    output_value = cache.get(cache_key) # returns None if no key-value pair
    if output_value == None:
        #if is none we save it in the cache and returns it
        output_value = urllib.request.urlopen(cache_key).read()
        if output_value:
          output_value = output_value.decode('utf-8')
          cache.set(cache_key,output_value,cache_time)
          return output_value
    else:
      return output_value

    # q = Cache.objects.filter(url=u)
    # if q.count()==0:
    #   output = urllib.request.urlopen(u).read()
    #   if output:
    #     output = output.decode('utf-8')
    #     new_cache = Cache(url=u,value=output)
    #     new_cache.save()
    #     return output 
    # else:
    #   return q[0].value

def download_with_cache_as_csv(u):
    q = download_with_cache(u)
    if q:
      return io.StringIO(q)
    else:
      return None

def getIndicator(id):
  q = Node.objects.filter(id=id)
  if q.count()==0:
    return None
  else:
    return q[0]

def getIndicatorBaseUrl(ind):
  if ind is None:
    return None
  if ind.griddap_url is not None and ind.griddap_url != "":
    return ind.griddap_url
  if ind.tabledap_url is not None and ind.tabledap_url != "":
    return ind.tabledap_url
  return None

def getIndicatorDataFormat(ind):
  if ind is None:
    return None
  if ind.griddap_url is not None and ind.griddap_url != "":
    return "griddap"
  if ind.tabledap_url is not None and ind.tabledap_url != "":
    return "tabledap"
  return None

def getIndicatorDimensions(ind):
  if ind is None:
    return None
  return ind.dimension_names.split()

def getIndicatorVariables(ind):
  if ind is None:
    return None
  return ind.variable_names.split()   

def getVariableAliases(variable):
  if variable=="depth":
    return ["plev","range"]
  if variable=="plev":
    return ["depth","range"]
  else:
    return [variable,"range"]

def getIndicatorQueryUrl(ind, onlyFirstVariable, skipDimensions, **kwargs):
  if type(ind) == str:
    ind = getIndicator(ind)

  # print("INDICATOR ========",ind)
  url = getIndicatorBaseUrl(ind)

  # print("URL ========",url)
  if "format" in kwargs:
    url = url + "." + kwargs["format"]



  di = getIndicatorDimensions(ind)

 
  va = getIndicatorVariables(ind)


  tipo = getIndicatorDataFormat(ind)
  


  
  griddap = (tipo == "griddap")
  
  if griddap and onlyFirstVariable and va.count()>1:
    va = [va[0]]

  if griddap and "variable" in kwargs:
    va = [kwargs["variable"]]  
  

 
  if skipDimensions:
    di = []

  query = "?"

  if griddap:
    for v in va:
      if query!="?":
        query = query+","
      query = query + v
      for d in di:

        query = query + "%5B("

        if d in kwargs and not (d+"Min") in kwargs:
          query = query + kwargs[d]
        elif (d+"Min") in kwargs:
          query = query + kwargs[d+"Min"]
        else:
          alias = getVariableAliases(d)
          
          for al in alias:
            if al in kwargs:
              query = query + kwargs[al]
            elif (al+"Min") in kwargs:
              query = query + kwargs[al+"Min"]

        query = query + "):1:("

        
        
        if d in kwargs and not (d+"Max") in kwargs:
          query = query + kwargs[d]
        elif (d+"Max") in kwargs:
          query = query + kwargs[d+"Max"]
        else:
          alias = getVariableAliases(d)
          
          for al in alias:
            if al in kwargs:
              query = query + kwargs[al]
            elif (al+"Max") in kwargs:
              query = query + kwargs[al+"Max"]

        query = query + ")%5D"
   
  else:
    for v in va:
      if query != "?":
        query = query + "%2C"
      query = query + v
    
    for d in va:
      if d != "Indicator":
        if d in kwargs and not (d+"Min") in kwargs:
          query = query + "&" + d + "%3E=" + kwargs[d]
        elif (d+"Min") in kwargs:
          query = query + "&" + d + "%3E=" + kwargs[d+"Min"]
        else:
          alias = getVariableAliases(d)
          for al in alias:
            if al in kwargs:
              query = query + "&" + d + "%3E=" + kwargs[al]
            elif (al+"Min") in kwargs:
              query = query + "&" + d + "%3E=" + kwargs[al+"Min"]

        if d in kwargs and not (d+"Max") in kwargs:
          query = query + "&" + d + "%3C=" + kwargs[d]
        elif (d+"Max") in kwargs:
          query = query + "&" + d + "%3C=" + kwargs[d+"Max"]
        else:
          alias = getVariableAliases(d)
          for al in alias:
            if al in kwargs:
              query = query + "&" + d + "%3C=" + kwargs[al]
            elif (al+"Max") in kwargs:
              query = query + "&" + d + "%3C=" + kwargs[al+"Max"]
    

  
  print("URL + QUERY =",url+query)
  #https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/EOBS_a583_d8f2_21c0.json?very_wet_days_wrt_95th_percentile_of_reference_period%5B(2020-12-31T00:00:00Z):1:(2020-12-31T00:00:00Z)%5D%5B(46.94985982579791):1:(46.94985982579791)%5D%5B(21.94986030317809):1:(21.94986030317809)%5D
  return url+query

def getIndicatorQueryUrlPoint(ind, onlyFirstVariable, skipDimensions, lat, lon, time, range, **kwargs):  
  return getIndicatorQueryUrl(ind, onlyFirstVariable, skipDimensions, latitude=lat, longitude=lon, time=time, range=range)


  
def url_is_indicator(is_indicator,is_graph,is_annual,**kwargs):
  if is_indicator == "true" and is_graph == False and is_annual == False:
  
    print("ENTRO IN URL_IS_INDICATOR LATO TABLEDAP!")
    url = ERDDAP_URL+"/tabledap/" + kwargs["dataset_id"] + ".csv?" + "time%2Clatitude%2Clongitude%2C" + kwargs["layer_name"] +"&time%3E=" + kwargs["date_start"] + "&time%3C=" + kwargs["date_start"]
  
  elif is_indicator == "true" and is_graph and is_annual:
      url = ERDDAP_URL+"/tabledap/" + kwargs["dataset_id"] + ".csv?" + "time%2Clatitude%2Clongitude%2C" + kwargs["layer_name"] +"&time%3E=" + kwargs["time_start"] + "&time%3C=" + kwargs["time_finish"] + "&latitude%3E=" + kwargs["latitude"] +"&latitude%3C=" + kwargs["latitude"] + "&longitude%3E=" + kwargs["longitude"] + "&longitude%3C=" + kwargs["longitude"]

  elif is_indicator == "true" and is_graph and not is_annual:
        #https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/indicators_wsdi_aba0_0062_8939.csv?time%2Clatitude%2Clongitude%2Cwsdi&time%3E=2021-07-01&time%3C=2050-07-01&latitude%3E=39.688777923584&latitude%3C=41.22824901518532&longitude%3E=14.740385055542&longitude%3C=15.183105468750002
        #https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/arpav_PRCPTOT_yearly.htmlTable?time%2Clatitude%2Clongitude%2CIndicator&time%3E=2021-12-25&time%3C=2022-01-01
      url = ERDDAP_URL+"/tabledap/" + kwargs["dataset_id"] + ".csv?" + "time%2Clatitude%2Clongitude%2C" + kwargs["layer_name"] +"&time%3E=" + kwargs["time_start"] + "&time%3C=" + kwargs["time_finish"] + "&latitude%3E=" + kwargs["latMin"] +"&latitude%3C=" + kwargs["latMax"] + "&longitude%3E=" + kwargs["longMin"] + "&longitude%3C=" + kwargs["longMax"]

  elif is_indicator == "false" and is_graph == False and is_annual == False:  
    if (kwargs["num_param"] > 3):
          #https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/adriaclim_WRF_9e77_be3a_4ac6.htmlTable?txx%5B(2036-07-01T09:00:00Z):1:(2036-07-01T09:00:00Z)%5D%5B(37.00147):1:(46.97328)%5D%5B(10.0168):1:(21.98158)%5D
          url = ERDDAP_URL+"/griddap/" + kwargs["dataset_id"] + ".csv?" +  kwargs["layer_name"] + "%5B(" +  kwargs["time_start"]  + "):1:(" +  kwargs["time_finish"]  + ")%5D%5B(" + str(kwargs["range_value"]) + "):1:(" + str(kwargs["range_value"]) + ")%5D%5B(" + kwargs["latitude_start"] + "):1:(" + kwargs["latitude_end"] + ")%5D%5B(" + kwargs["longitude_start"] + "):1:(" + kwargs["longitude_end"] + ")%5D"
    else:
          url = ERDDAP_URL+"/griddap/" + kwargs["dataset_id"]  + ".csv?" + kwargs["layer_name"] + "%5B(" +  kwargs["time_start"]  + "):1:(" +  kwargs["time_finish"] + ")%5D%5B(" + kwargs["latitude_start"] + "):1:(" + kwargs["latitude_end"] + ")%5D%5B(" + kwargs["longitude_start"] + "):1:(" + kwargs["longitude_end"]+ ")%5D"

  elif is_indicator == "false" and is_graph  and is_annual == False:
       if(kwargs["num_parameters"]>3):
          url=ERDDAP_URL+"/griddap/"+ kwargs["dataset_id"] +".csv?"+kwargs["layer_name"]+"%5B("+kwargs["time_start"]+"):1:("+kwargs["time_finish"]+")%5D%5B("+str(kwargs["range_value"])+"):1:("+str(kwargs["range_value"])+")%5D%5B("+kwargs["latitude"]+"):1:("+kwargs["latitude"]+")%5D%5B("+kwargs["longitude"]+"):1:("+kwargs["longitude"]+")%5D"
       else:
          url=ERDDAP_URL+"/griddap/"+ kwargs["dataset_id"] +".csv?"+ kwargs["layer_name"] +"%5B("+kwargs["time_start"]+"):1:("+kwargs["time_finish"]+")%5D%5B("+kwargs["latitude"]+"):1:("+ kwargs["latitude"] +")%5D%5B("+kwargs["longitude"]+"):1:("+kwargs["longitude"]+")%5D"
  
  elif is_indicator == "false" and is_graph and is_annual:
    if (kwargs["num_parameters"] > 3 ):
      
      url = ERDDAP_URL+"/griddap/" + kwargs["dataset_id"] +".csv?" + kwargs["layer_name"] + "%5B(" + kwargs["time_start"] + "):1:("+kwargs["time_finish"]+")%5D%5B("+str(kwargs["range_value"])+"):1:("+str(kwargs["range_value"])+")%5D%5B(" + kwargs["latMax"] + "):1:(" +kwargs["latMin"]  + ")%5D%5B(" +kwargs["longMax"]+ "):1:(" + kwargs["longMin"]  + ")%5D"
  
    else:
      url = ERDDAP_URL+"/griddap/" + kwargs["dataset_id"] +".csv?"+kwargs["layer_name"] + "%5B(" + kwargs["time_start"] + "):1:("+kwargs["time_finish"]+ ")%5D%5B(" + kwargs["latMax"]  + "):1:(" + kwargs["latMin"]  + ")%5D%5B(" +kwargs["longMax"]+ "):1:(" + kwargs["longMin"]  + ")%5D"
  
  elif is_indicator == "false" and is_graph == False:  
    if (kwargs["num_param"] > 3):
          url = ERDDAP_URL+"/griddap/" + kwargs["dataset_id"] + ".csv?" +  kwargs["layer_name"] + "%5B(" +  kwargs["date_start"]  + "):1:(" +  kwargs["date_start"]  + ")%5D%5B(" + str(kwargs["range_value"]) + "):1:(" + str(kwargs["range_value"]) + ")%5D%5B(" + kwargs["latitude_start"] + "):1:(" + kwargs["latitude_end"] + ")%5D%5B(" + kwargs["longitude_start"] + "):1:(" + kwargs["longitude_end"] + ")%5D"
    else:
          url = ERDDAP_URL+"/griddap/" + kwargs["dataset_id"]  + ".csv?" + kwargs["layer_name"] + "%5B(" +  kwargs["date_start"]  + "):1:(" +  kwargs["date_start"] + ")%5D%5B(" + kwargs["latitude_start"] + "):1:(" + kwargs["latitude_end"] + ")%5D%5B(" + kwargs["longitude_start"] + "):1:(" + kwargs["longitude_end"]+ ")%5D"
  
  return url

def getAllDatasets():
  start_time = time.time()
  print("Started getAllDatasets()")
  url_datasets=ERDDAP_URL+"/info/index.csv?page=1&itemsPerPage=100000"
  df=pd.read_csv(download_with_cache_as_csv(url_datasets),header=0,sep=",",names=["griddap","subset","tabledap","Make A Graph",
                                                          "wms","files","Title","Summary","FGDC","ISO 19115",
                                                          "Info","Background Info","RSS","Email","Institution",
                                                          "Dataset ID"],
                  na_values="Value not available")
  node_list = []
  dataset_list = []
  scale_list = []
  print("Time to finish first read_csv getAllDatasets() ========= {:.2f} seconds".format(time.time()-start_time))
  df1 = df.replace(np.nan, "", regex=True)
  all_datasets = Node.objects.all()
  # all_indicators = Indicator.objects.all()
  # all_indicators.delete()
  all_datasets.delete()
  for index,row in df1.iterrows():
    if row["Info"] != "Info" and row["Dataset ID"] != "allDatasets":
      #We take every datasets to fill the full list!
      
      adriaclim_scale = None
      adriaclim_dataset = None
      adriaclim_timeperiod = None
      adriaclim_model = None
      adriaclim_type = None
      institution = "UNKNOWN"
      time_start = None
      time_end = None
      lat_min = None
      lat_max = None
      lng_min = None
      lng_max = None

      variables = 0
      variable_names = ""
      dimensions = 0
      dimension_names = ""

      node_id = row["Dataset ID"]
      metadata_url = row["Info"]
      tabledap_url = row["tabledap"]
      griddap_url = row["griddap"]
      get_info = pd.read_csv(download_with_cache_as_csv(row["Info"]), header=None, sep=",",
                            names=["Row Type", "Variable Name", "Attribute Name", "Data Type", "Value"]).fillna("nan")
      for index1, row1 in get_info.iterrows():
        #now we create our datasets that we put in our db 
        if row1["Row Type"] == "dimension":
          if dimensions > 0:
            dimension_names = dimension_names + " "
          dimensions = dimensions+1
          dimension_names = dimension_names+row1["Variable Name"]

        if row1["Row Type"] == "variable":
          if variables > 0:
            variable_names = variable_names + " "
          variables = variables+1
          variable_names = variable_names+row1["Variable Name"]

        if row1["Attribute Name"] == "adriaclim_dataset":
          adriaclim_dataset = row1["Value"]
        if row1["Attribute Name"] == "adriaclim_model":
          adriaclim_model = row1["Value"]
        if row1["Attribute Name"] == "adriaclim_scale":
          adriaclim_scale = row1["Value"]
        if row1["Attribute Name"]  == "adriaclim_timeperiod":
          adriaclim_timeperiod = row1["Value"]
        if row1["Attribute Name"] == "adriaclim_type":
          adriaclim_type = row1["Value"]
        if row1["Attribute Name"] == "title":
          title = row1["Value"]
        if row1["Attribute Name"] == "institution":
          institution = row1["Value"]
        if row1["Attribute Name"] == "time_coverage_start":
          time_start = row1["Value"]
        if row1["Attribute Name"] == "time_coverage_end":
          time_end = row1["Value"]
        if row1["Attribute Name"] == "geospatial_lat_min":
          lat_min = row1["Value"]
        if row1["Attribute Name"] == "geospatial_lat_max":
          lat_max = row1["Value"]
        if row1["Attribute Name"] == "geospatial_lon_min":
          lng_min = row1["Value"]
        if row1["Attribute Name"] == "geospatial_lon_max":
          lng_max = row1["Value"]

      #is_indicator it is used to check if it the dataset is an indicator! in futuro la cambiamo checkando solo adriaclim_dataset!!!!!
      is_indicator =  re.search("^indicat*",row["Dataset ID"]) or re.search("indicator",row["Title"], re.IGNORECASE)
      
      if is_indicator and adriaclim_scale is None:
        adriaclim_scale = "large"

      if adriaclim_timeperiod == "day":
        adriaclim_timeperiod = "daily"


      if adriaclim_scale is None and not is_indicator:
        adriaclim_scale = "UNKNOWN"


      if adriaclim_model is None:
        adriaclim_model="UNKNOWN"

      if adriaclim_type is None:
        adriaclim_type="UNKNOWN"

      if adriaclim_dataset is None:
        if is_indicator:
          adriaclim_dataset = "indicator"
        else:
          adriaclim_dataset="no"

      if adriaclim_timeperiod is None:
        if "yearly" in row["Title"].lower():
          adriaclim_timeperiod = "yearly"
        if "monthly" in row["Title"].lower():
          adriaclim_timeperiod = "monthly"
        if "seasonal" in row["Title"].lower():
          adriaclim_timeperiod = "seasonal"

      if adriaclim_timeperiod is None:
        if is_indicator:
          adriaclim_timeperiod = "yearly"
        else:
          adriaclim_timeperiod = "UNKNOWN"
      
      if time_start is not None and time_end is not None:
          # if is_indicator:
          #   new_ind = Indicator(dataset_id = node_id, adriaclim_dataset = adriaclim_dataset, adriaclim_model = adriaclim_model,
          #         adriaclim_scale = adriaclim_scale, adriaclim_timeperiod = adriaclim_timeperiod, 
          #         adriaclim_type = adriaclim_type, title = row["Title"], metadata_url = metadata_url, institution = institution,
          #         lat_min = lat_min, lng_min = lng_min, lat_max = lat_max, lng_max = lng_max, time_start = time_start, time_end = time_end, tabledap_url = tabledap_url, dimensions = dimensions,
          #         dimension_names = dimension_names, variables = variables, variable_names = variable_names, griddap_url = griddap_url,
          #         wms_url=row["wms"])
          # else:
        new_node = Node(id = node_id, adriaclim_dataset = adriaclim_dataset, adriaclim_model = adriaclim_model,
                          adriaclim_scale = adriaclim_scale, adriaclim_timeperiod = adriaclim_timeperiod, 
                          adriaclim_type = adriaclim_type, title = row["Title"], metadata_url = metadata_url, institution = institution,
                          lat_min = lat_min, lng_min = lng_min, lat_max = lat_max, lng_max = lng_max, time_start = time_start, time_end = time_end, tabledap_url = tabledap_url, dimensions = dimensions,
                          dimension_names = dimension_names, variables = variables, variable_names = variable_names, griddap_url = griddap_url,
                          wms_url=row["wms"])
        # new_ind.save()
        new_node.save()
        node_list.append(new_node.title)
        dataset_list.append(adriaclim_dataset)
        scale_list.append(adriaclim_scale)
  print("Time to finish getAllDatasets() ========= {:.2f} seconds".format(time.time()-start_time))
  return [node_list,dataset_list,scale_list]

  
   
def getTitle():
  start_time = time.time()
  print("Started getTitle()")
  url_datasets=ERDDAP_URL+"/info/index.csv?page=1&itemsPerPage=100000"
  df=pd.read_csv(download_with_cache_as_csv(url_datasets),header=0,sep=",",names=["griddap","subset","tabledap","Make A Graph",
                                                           "wms","files","Title","Summary","FGDC","ISO 19115",
                                                           "Info","Background Info","RSS","Email","Institution",
                                                           "Dataset ID"],
                  na_values="Value not available")
  titleList=[]
  

  df1 = df.replace(np.nan, "", regex=True)

  for index,row in df1.iterrows():
      if row["Title"]!="* The List of All Active Datasets in this ERDDAP *" and row["wms"]!="wms" and not re.search("^indicat*",row["Dataset ID"]):
        titleList.append(row["Title"])
  
  print("Time to finish getTitle() ========= {:.2f} seconds".format(time.time()-start_time))
  return titleList

def getIndicators():
  start_time = time.time()
  print("Started getIndicators()")
  url_datasets=ERDDAP_URL+"/info/index.csv?page=1&itemsPerPage=100000"
  df=pd.read_csv(download_with_cache_as_csv(url_datasets),header=0,sep=",",names=["griddap","subset","tabledap","Make A Graph",
                                                           "wms","files","Title","Summary","FGDC","ISO 19115",
                                                           "Info","Background Info","RSS","Email","Institution",
                                                           "Dataset ID"],
                  na_values="Value not available")
  indicator_list = []
  dataset_list = []
  scale_list = []
  print("Time to finish first read_csv getIndicators() ========= {:.2f} seconds".format(time.time()-start_time))
  df1 = df.replace(np.nan, "", regex=True)
  all_indicators = Indicator.objects.all()
  all_indicators.delete()
  for index,row in df1.iterrows():
     if row["Info"] != "Info" and row["Dataset ID"] != "allDatasets" and (re.search("^indicat*",row["Dataset ID"]) or re.search("indicator",row["Title"], re.IGNORECASE)):
      #if the dataset_id starts with indicat...For now we assume that indicators have this thing in common......
      #we found an indicator so we need to explore its metadata!
      adriaclim_scale = None
      adriaclim_dataset = None
      adriaclim_timeperiod = None
      adriaclim_model = None
      adriaclim_type = None
      institution = "UNKNOWN"
      time_start = None
      time_end = None
      lat_min = None
      lat_max = None
      lng_min = None
      lng_max = None

      variables = 0
      variable_names = ""
      dimensions = 0
      dimension_names = ""

      dataset_id = row["Dataset ID"]
      metadata_url = row["Info"]
      tabledap_url = row["tabledap"]
      griddap_url = row["griddap"]
      get_info = pd.read_csv(download_with_cache_as_csv(row["Info"]), header=None, sep=",",
                            names=["Row Type", "Variable Name", "Attribute Name", "Data Type", "Value"]).fillna("nan")
      for index1, row1 in get_info.iterrows():
        #now we create our indicators that we put in our db 

        if row1["Row Type"] == "dimension":
           if dimensions > 0:
             dimension_names = dimension_names + " "
           dimensions = dimensions+1
           dimension_names = dimension_names+row1["Variable Name"]

        if row1["Row Type"] == "variable":
           if variables > 0:
             variable_names = variable_names + " "
           variables = variables+1
           variable_names = variable_names+row1["Variable Name"]

        if row1["Attribute Name"] == "adriaclim_dataset":
          adriaclim_dataset = row1["Value"]
        if row1["Attribute Name"] == "adriaclim_model":
          adriaclim_model = row1["Value"]
        if row1["Attribute Name"] == "adriaclim_scale":
          adriaclim_scale = row1["Value"]
        if row1["Attribute Name"]  == "adriaclim_timeperiod":
          adriaclim_timeperiod = row1["Value"]
        if row1["Attribute Name"] == "adriaclim_type":
          adriaclim_type = row1["Value"]
        if row1["Attribute Name"] == "title":
          title = row1["Value"]
        if row1["Attribute Name"] == "institution":
          institution = row1["Value"]
        if row1["Attribute Name"] == "time_coverage_start":
          time_start = row1["Value"]
        if row1["Attribute Name"] == "time_coverage_end":
          time_end = row1["Value"]
        if row1["Attribute Name"] == "geospatial_lat_min":
          lat_min = row1["Value"]
        if row1["Attribute Name"] == "geospatial_lat_max":
          lat_max = row1["Value"]
        if row1["Attribute Name"] == "geospatial_lon_min":
          lng_min = row1["Value"]
        if row1["Attribute Name"] == "geospatial_lon_max":
          lng_max = row1["Value"]

      # if adriaclim_scale is None or (adriaclim_scale != "pilot" and adriaclim_scale != "local") : 
      #   adriaclim_scale="large"
      if adriaclim_scale is None: 
        adriaclim_scale="large"

      if adriaclim_model is None:
        adriaclim_model="UNKNOWN"

      if adriaclim_type is None:
        adriaclim_type="UNKNOWN"

      if adriaclim_dataset is None:
        # if re.search("^indicat*",row["Dataset ID"]) or re.search("indicator",row["Title"], re.IGNORECASE):
        adriaclim_dataset="indicator"
        # else:
        #   adriaclim_dataset="no"

      if adriaclim_timeperiod is None:
        # if re.search("^yearly*",row["Title"]):
        #   adriaclim_timeperiod = "yearly"
        # if re.search("^monthly*",row["Title"]):
        #   adriaclim_timeperiod = "monthly"
        # if re.search("^seasonal*",row["Title"]):
        #   adriaclim_timeperiod = "seasonal"
        if "yearly" in row["Title"].lower():
          adriaclim_timeperiod = "yearly"
        if "monthly" in row["Title"].lower():
          adriaclim_timeperiod = "monthly"
        if "seasonal" in row["Title"].lower():
          adriaclim_timeperiod = "seasonal"
      if adriaclim_timeperiod is None:
        adriaclim_timeperiod = "yearly"
      
      if time_start is not None and time_end is not None:  
        new_indicator = Indicator(dataset_id = dataset_id, adriaclim_dataset = adriaclim_dataset, adriaclim_model = adriaclim_model,
                                  adriaclim_scale = adriaclim_scale, adriaclim_timeperiod = adriaclim_timeperiod, 
                                  adriaclim_type = adriaclim_type, title = row["Title"], metadata_url = metadata_url, institution = institution,
                                  lat_min = lat_min, lng_min = lng_min, lat_max = lat_max, lng_max = lng_max, time_start = time_start, time_end = time_end, tabledap_url = tabledap_url, dimensions = dimensions,
                                  dimension_names = dimension_names, variables = variables, variable_names = variable_names, griddap_url = griddap_url,
                                  wms_url=row["wms"])
        new_indicator.save()
        indicator_list.append(new_indicator.title)
        dataset_list.append(adriaclim_dataset)
        scale_list.append(adriaclim_scale)
  
  print("Time to finish getIndicators() ========= {:.2f} seconds".format(time.time()-start_time))
  return [indicator_list,dataset_list,scale_list]
    


 

def getWMS():
  url_datasets=ERDDAP_URL+"/info/index.csv?page=1&itemsPerPage=1000000000"
  df=pd.read_csv(url_datasets,header=None,sep=",",names=["griddap","subset","tabledap","Make A Graph",
                                                           "wms","files","Title","Summary","FGDC","ISO 19115",
                                                           "Info","Background Info","RSS","Email","Institution",
                                                           "Dataset ID"],
                  na_values="")
  df1=df.replace(np.nan,"",regex=True)
  wmsList=[]
  for index,row in df1.iterrows():
      wmsList.append(row["wms"])
    
  
  return wmsList

def getMetadataTime1(dataset_id):
    url_datasets = ERDDAP_URL+"/info/index.csv?page=1&itemsPerPage=1000000000"
    df = pd.read_csv(download_with_cache_as_csv(url_datasets), header=None, sep=",", names=["griddap", "subset", "tabledap", "Make A Graph",
                                                                "wms", "files", "Title", "Summary", "FGDC",
                                                                "ISO 19115",
                                                                "Info", "Background Info", "RSS", "Email",
                                                                "Institution",
                                                                "Dataset ID"],
                     na_values="")
  
    df1 = df.replace(np.nan, "", regex=True)
    our_metadata = []
    variable_meta = ""
    title_meta = ""
    layer_name = ""
    values_time = ""
    attribution_layer = ""
    values_others = ""
    average_spacing_others = ""
    positive_negative=""
    latitude_range = ""
    longitude_range = ""
    lat_min = ""
    lat_max = ""
    long_min = ""
    long_max = ""
    dimensions = "time, latitude, longitude"
    for index, row in df1.iterrows():
        if row["Dataset ID"] == dataset_id:
            get_info = pd.read_csv(download_with_cache_as_csv(row["Info"]), header=None, sep=",",
                                   names=["Row Type", "Variable Name", "Attribute Name", "Data Type", "Value"]).fillna("nan")
            for index1, row1 in get_info.iterrows():
                if row1["Row Type"] == "variable":
                    variable_meta = row1["Value"]
                if row1["Row Type"] == "attribute" and row1["Attribute Name"] == "title":
                    title_meta = row1["Value"]
                if row1["Row Type"] == "variable":
                    layer_name = row1["Variable Name"]
                if row1["Row Type"] == "attribute" and row1["Variable Name"] == "time" and row1[
                    "Attribute Name"] == "actual_range":
                    # 2005-11-20T00:00:00Z
                    values_time = row1["Value"]
                if row1["Row Type"] == "attribute" and row1["Variable Name"] == "Times" and row1[
                    "Attribute Name"] == "actual_range":
                    # 2005-11-20T00:00:00Z
                    values_time = row1["Value"]
                   
                if row1["Row Type"] == "attribute" and row1["Attribute Name"] == "institution":
                    attribution_layer = row1["Value"]

                if row1["Row Type"] == "attribute" and row1["Variable Name"] != "time" and row1["Variable Name"] != "Times" and row1[
                    "Variable Name"] != "latitude" and row1[
                    "Variable Name"] != "longitude" and row1["Attribute Name"] == "actual_range":
                    values_others = row1["Value"]

                if row1["Row Type"] == "dimension" and row1["Variable Name"] != "time" and row1["Variable Name"] != "Times" and row1[
                    "Variable Name"] != "latitude" and row1[
                    "Variable Name"] != "longitude":
                    dimensions += ", " + row1["Variable Name"]
                    spacing = row1["Value"]
                    average_spacing_others = spacing.split(",")[2]
                if row1["Row Type"] =="attribute" and row1["Variable Name"] != "time" and row1["Row Type"] == "attribute" and row1["Variable Name"] != "Times" and row1[
                    "Variable Name"] != "latitude" and row1[
                    "Variable Name"] != "longitude" and row1["Attribute Name"]=="positive":
                    positive_negative=row1["Value"]
                if row1["Row Type"] == "attribute" and row1["Variable Name"]=="latitude" and row1["Attribute Name"]=="actual_range":
                    latitude_range = row1["Value"]
                if row1["Row Type"] == "attribute" and row1["Variable Name"]=="longitude" and row1["Attribute Name"]=="actual_range":
                    longitude_range = row1["Value"]
    
    
    if variable_meta != "nan":
      our_metadata = [values_others, variable_meta, values_time, title_meta, layer_name, average_spacing_others,
                      attribution_layer,positive_negative,latitude_range,longitude_range]
    else:
      is_indicator = True
      our_metadata = [values_others, dimensions, values_time, title_meta, layer_name, average_spacing_others,
                      attribution_layer,positive_negative,latitude_range,longitude_range,is_indicator]

    return our_metadata

#def getValuesDatasets(id1,id2):
  


def getMetadata(dataset_id):
    all_metadata=getMetadataTime1(dataset_id)
    min_max_value=[]
    average_spacing_others=[]
    final_list=[]
    j=0
    for i in range(len(all_metadata[1])):
        splitted=all_metadata[1][i].split(",")
        if len(splitted)>3:
            min_max_value.append(all_metadata[0][j])
            average_spacing_others.append(all_metadata[6][j])
            j=j+1
        else:
            min_max_value.append(0)
            average_spacing_others.append(0)

    final_list=[all_metadata,min_max_value,average_spacing_others]
    return final_list
  


  

  
  


def listAllDatasets():
  url_datasets=ERDDAP_URL+"/info/index.csv?page=1&itemsPerPage=1000000000"
  url_open = urllib.request.urlopen(url_datasets)
  csvfile = csv.DictReader(io.TextIOWrapper(url_open, encoding = 'utf-8'), delimiter=',')  
  return csvfile
  """  df=pd.read_csv(url_datasets,header=None,sep=",",names=["griddap","subset","tabledap","Make A Graph",
                                                           "wms","files","Title","Summary","FGDC","ISO 19115",
                                                           "Info","Background Info","RSS","Email","Institution",
                                                           "Dataset ID"],
                  na_values="Value not available")
  
   df1=df.replace(np.nan,"Value not available",regex=True)
   df1.to_html("AdriaProject/templates/allDatasets.html",index=False)
   with open("AdriaProject/templates/allDatasets.html") as file:
       file=file.read()
   file=file.replace("<table ", "<table class='rwd-table'")

   with open("AdriaProject/templates/allDatasets.html","w") as file_to_write:
       file_to_write.write(htmlGetAllDatasets+file)
   
   file_to_write.close() """


def getMetadataOfASpecificDataset(dataset_id):
  is_indicator = False
  try:
    x=Node.objects.get(id=dataset_id)
    url = x.metadata_url.replace(".csv",".json")
    r = requests.get(url=url)
    data = r.json()
    return data
    # df = pd.read_csv(x.metadata_url,header=None,sep=",",names=["Row Type","Variable Name","Attribute Name","Data Type","Value"],na_values="Value not available")
    # df1 = df.replace(np.nan,"Value not available",regex=True)
    # df1.to_html("./templates/specificDataset.html",index=False)
    # with open("./templates/specificDataset.html") as file:
    #     file = file.read()
    # file = file.replace("<table ","<table class='rwd-table'")
    # return file
  except Node.DoesNotExist:
    is_indicator = True
  
  if is_indicator:
    try:
      indicator = Indicator.objects.get(pk=dataset_id)
      url = indicator.metadata_url.replace(".csv",".json")
      r = requests.get(url=url)
      data = r.json()
      return data
      # df = pd.read_csv(indicator.metadata_url,header=None,sep=",",names=["Row Type","Variable Name","Attribute Name","Data Type","Value"],na_values="Value not available")
      # df1 = df.replace(np.nan,"Value not available",regex=True)
      # df1.to_html("./templates/specificDataset.html",index=False)
      # with open("./templates/specificDataset.html") as file:
      #     file = file.read()
      # file = file.replace("<table ","<table class='rwd-table'")
      # return file
    except Indicator.DoesNotExist:
      return 




def getDataTableIndicator(dataset_id,layer_name,time_start,time_finish,lat_start,lat_end,long_start,long_end,num_parameters,range_value):
    url = url_is_indicator("true",True,False,dataset_id=dataset_id,layer_name=layer_name,time_start=time_start,time_finish=time_finish,latMin=lat_start,
                            longMin=long_start,latMax=lat_end,longMax=long_end,num_parameters=num_parameters,range_value=range_value)
    print(url)
    url = getIndicatorQueryUrl(dataset_id,False,False,latitude=latitude,longitude=longitude,
                               timeMin=time_start,timeMax=time_finish,range=range_value,format="json")
    #https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/indicators_wsdi_aba0_0062_8939.csv?time%2Clatitude%2Clongitude%2Cwsdi&time%3E=2021-07-01&time%3C=2050-07-01&latitude%3E=39.688777923584&latitude%3C=41.22824901518532&longitude%3E=14.740385055542&longitude%3C=15.183105468750002
    r = requests.get(url=url)
    # csvfile = csv.DictReader(io.TextIOWrapper(url_open, encoding = 'utf-8'), delimiter=',') 
    data = r.json()
    return data

def getDataTable(dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value):
  try:
    #vedere se si tratta di un poligono e nel caso prendere tutti i punti che stanno nel poligono e per ogni punto chiamare questa funzione e costruire il json?

    url = getIndicatorQueryUrl(dataset_id,False,False,latitude=str(latitude),longitude=str(longitude),
    
                                timeMin=str(time_start),timeMax=str(time_finish),range=str(range_value),format="json")
    print("URL SUPER FUNZIONE =", url)
    # urlTabledap = https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/arpav_PRCPTOT_yearly.htmlTable?time%2Clatitude%2Clongitude%2CIndicator&time%3E=2021-12-25&time%3C=2022-01-01

    # if num_parameters > 3:
    #   url= ERDDAP_URL + "/griddap/"+dataset_id+".json?"+layer_name+"%5B("+str(time_start)+"):1:("+str(time_finish)+")%5D%5B("+str(range_value)+"):1:("+str(range_value)+")%5D%5B("+str(latitude)+"):1:("+str(latitude)+")%5D%5B("+str(longitude)+"):1:("+str(longitude)+")%5D"
    # else:
    #   url = ERDDAP_URL + "/griddap/"+dataset_id+".json?"+layer_name+"%5B("+str(time_start)+"):1:("+str(time_finish)+")%5D%5B("+str(latitude)+"):1:("+str(latitude)+")%5D%5B("+str(longitude)+"):1:("+str(longitude)+")%5D"
      
    #https://erddap-dev.cmcc-opa.eu/erddap/griddap/atm_regional_1f91_1673_845b.htmlTable?vegetfrac%5B(1969-12-30):1:(2005-11-20T00:00:00Z)%5D%5B(13):1:(13.0)%5D%5B(-90):1:(-90.0)%5D%5B(180.45724):1:(180.4572)%5D
    r = requests.get(url=url)
    
    # csvfile = csv.DictReader(io.TextIOWrapper(url_open, encoding = 'utf-8'), delimiter=',') 
    data = r.json() 
    return data

  except Exception as e:
    print("EXEPTION =", e)
    return e

def getDataGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end, **kwargs):
  
  onlyone = 0
  cache = 0
  if "context" in kwargs and kwargs["context"]=="one":
    onlyone = 1
  if "cache" in kwargs and kwargs["cache"]=="yes":
    cache = 1
  onlylat = None
  onlylong = None
  operation = None
  
  if "operation" in kwargs and kwargs["operation"]!="":
    operation = kwargs["operation"]

  if (lat_start == "no"):
    lat_start = latitude
  if (lat_end == "no"):
    lat_end = latitude
  if (long_start == "no"):
    long_start = longitude
  if (long_end == "no"):
    long_end = longitude

  




  url = getIndicatorQueryUrl(dataset_id,False,False,latitude=latitude,longitude=longitude, latitudeMin=lat_start, latitudeMax=lat_end, longitudeMin=long_start, longitudeMax=long_end, range=range_value,variable=layer_name,format="csv",timeMin=time_start,timeMax=time_finish)
  if cache==1:
    url = download_with_cache_as_csv(url)
  df = pd.read_csv(url, dtype='unicode')
  if df[layer_name] is not None:
    unit = df[layer_name][0]
  else:
     unit = layer_name
  unit = ""
  df = df.iloc[1: , :]
  n_values = len(df)
  allData=[]
  values=[]
  dates=[]
  layerName=[]
  lats = []
  longs = []
  i=0
  if n_values<=x:  #all the data
    for index,row in df.iterrows():
       if onlyone==1 and onlylat is None:
          onlylat = row["latitude"]
          onlylong = row["longitude"]
       if row[layer_name]==row[layer_name] and row[layer_name]!="NaN" and (onlyone==0 or (onlylat==row["latitude"] and onlylong==row["longitude"])):
          lats.insert(i,row["latitude"])
          longs.insert(i,row["longitude"])
          layerName.insert(i,layer_name)
          values.insert(i,row[layer_name])
          dates.insert(i,row["time"])
          i+=1
  else:  #one every nvalues/x data 
    every_nth_rows=int(n_values/x)
    df=df[::every_nth_rows]
    for index,row in df.iterrows():
       if row[layer_name]==row[layer_name] and row[layer_name]!="NaN" and (onlyone==0 or (onlylat==row["latitude"] and onlylong==row["longitude"])):
          lats.insert(i,row["latitude"])
          longs.insert(i,row["longitude"])
          layerName.insert(i,layer_name)
          values.insert(i,row[layer_name])
          dates.insert(i,row["time"])
          i+=1

  allData=[values,dates,unit,layerName,lats,longs]
  if operation is None:
    return allData
  else:
    output = None
    if "output" in kwargs:
      output = kwargs["output"]
 
    return packageGraphData(processOperation(operation,values,dates,unit,layerName,lats,longs),output=output)

def packageGraphData(allData,**kwargs):
  values = allData[0]
  dates = allData[1]
  unit = allData[2]
  layerName = allData[3]
  lats = allData[4]
  longs = allData[5]
  data = {}
  data["unit"]=unit
  data["entries"]=[]

  if "output" in kwargs:
    if kwargs["output"]=="csv":
        out = "Date,Dataset,Latitude,Longitude,Value\n"
        for n in range(len(values)):
          out = out + dates[n] + "," + layerName[n] + "," + str(lats[n]) + "," + str(longs[n]) + "," + str(values[n]) + "\n"
        return out
    
  for n in range(len(values)):
    dictKey = layerName[n]
    dictValue = None
    if dictKey in data:
      dictValue = data[dictKey]
    else:
      dictValue = []
      data[dictKey] = dictValue
      data["entries"].append(dictKey)
    entry = {}
    entry["x"]=dates[n]
    entry["y"]=values[n]
    dictValue.append(entry)
  return data

def processOperation(operation,values,dates,unit,layerName,lats,longs):
  if operation=="default":
    return [values,dates,unit,layerName,lats,longs]
  values2=[]

  dates2=[]
  layerName2=[]
  lats2 = []
  longs2 = []
  i=0
  vals = [] 
  lastDate = None

  pattern = None

  if operation == "annualMonth":
    pattern = re.compile('\d\d\d\d-(\d\d)-\S*')
    months = ["01","02","03","04","05","06","07","08","09","10","11","12"]
    for mon in months:
      dat = "0000-"+mon+"-01T00:00:00Z"
      vals = []
      for n in range(len(values)):
        if pattern.match(dates[n]).group(1)!=mon:
          continue
        vals.append(values[n])
        
      if (len(vals)>0):
        dates2.insert(i,dat)
        lats2.insert(i,0)
        longs2.insert(i,0)
        layerName2.insert(i,layerName[0])
        values2.insert(i,aggregateGraphicValues("avg",vals))
        
      vals = []

    return [values2,dates2,unit,layerName2,lats2,longs2]
  
  if operation == "annualDay":
    try:
      #operation is annual cycle but day by day 
      #I need to take that particular day for every year!!
      #print("Ci entrooooooooooooooooooooooooo")
      dates_list = [dt.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").date() for date in dates]
      #print("DATES_LIST======",dates_list)
      lats2 = [0 for value in values]
      longs2 = [0 for value in values]
      layerName2 = [layerName[0] for value in values]
      # in values ci sono tutti i valori, dates_list tutte le date!
      float_values = [float(value) for value in values]
      df = pd.DataFrame({'datetime':dates_list,'value':float_values})
      df["datetime"] = pd.to_datetime(df["datetime"])
      # Replace February 29th with February 28th
      df['datetime'] = df['datetime'].apply(lambda x: x.replace(day=28) if x.month == 2 and x.day == 29 else x)
      df["day_month"] = df["datetime"]
      df["day_month"] = df["day_month"].apply(lambda x: x.replace(year = 2000))
      df = df.sort_values(by=["day_month"])
      grouped = df.groupby('day_month')['value'].mean()
      df['day_month'] = df['day_month'].apply(lambda x: x.strftime("%d-%m"))
      removeDuplicates = df.drop_duplicates(subset=['day_month'])
      return [grouped.values,list(removeDuplicates["day_month"]),unit,layerName2,lats2,longs2]
    except Exception as e:
      print("EXCEPTION =", e)

  for n in range(len(values)):
    
    if lastDate is None:
      lastDate = dates[n]
      
    elif lastDate!=dates[n]:
      dates2.insert(i,lastDate)
      lats2.insert(i,0)
      longs2.insert(i,0)
      layerName2.insert(i,layerName[0])
      values2.insert(i,aggregateGraphicValues(operation,vals))
      i+=1
      lastDate = dates[n]
      vals = []

    vals.append(values[n])
  if lastDate is not None:
      dates2.insert(i,lastDate)
      lats2.insert(i,0)
      longs2.insert(i,0)
      layerName2.insert(i,layerName[0])
      values2.insert(i,aggregateGraphicValues(operation,vals))
      i+=1
    
 
  return [values2,dates2,unit,layerName2,lats2,longs2]

def aggregateGraphicValues(operation,vals):

  if vals is None:
    return None
  

  if operation=="median":
    vals.sort()
    return vals[int(len(vals)/2)]
  elif operation=="percentile_10":
    vals.sort()
    return vals[int(len(vals)*0.1)]
  elif operation=="percentile_90":
    vals.sort()
    return vals[int(len(vals)*0.9)]

  out = None
  for x in vals:
    x = float(x)
    if operation=="max":
      if out is None or x>out:
        out = x
    elif operation=="min":
      if out is None or x<out:
        out = x
    elif operation=="avg":
      if out is None:
        out = x
      else:
        out += x

  if operation=="avg":
    out = out / len(vals)
  return out

def getDataGraphic(dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end):
  graphic1=getDataGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end)
  return graphic1


def getMaxMinMeanMomentGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end):

    result = getDataGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end)

    if is_indicator == "false":
      url = url_is_indicator(is_indicator,True,False,dataset_id=dataset_id,layer_name=layer_name,time_start=time_start,time_finish=time_finish,latitude=latitude,
                            longitude=longitude,num_parameters=num_parameters,range_value=range_value)
    else:
      url = url_is_indicator("true",True,False,dataset_id=dataset_id,layer_name=layer_name,time_start=time_start,time_finish=time_finish,latMin=lat_start,
                            longMin=long_start,latMax=lat_end,longMax=long_end,num_parameters=num_parameters,range_value=range_value)
    df = pd.read_csv(url, dtype = 'unicode')
    unit = df[layer_name][0]
    df = df.iloc[1: , :]
    df_length = len(df)
    all_date = []
    all_values = []
    allData = []
    if df_length <= x:
        #take every value
        all_date = df["time"].to_numpy()
        all_values = df[layer_name].astype(float).to_numpy()
    else:
        every_nth_rows = int(df_length / x)
        df = df[::every_nth_rows]
        all_date = df["time"].to_numpy()
        all_values = df[layer_name].astype(float).to_numpy()
    
    allData = [all_date.tolist(),all_values.tolist(),layer_name,unit]
    return allData

def getMaxMinMomentIndicatorGraphic(max_min_mean,dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,latitude2,longitude2,latitude3,longitude3,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end):
    url = url_is_indicator("true",True,False,dataset_id=dataset_id,layer_name=layer_name,time_start=time_start,time_finish=time_finish,latMin=lat_start,
                            longMin=long_start,latMax=lat_end,longMax=long_end,num_parameters=num_parameters,range_value=range_value)
    
    df = pd.read_csv(url, dtype='unicode')
    df = df.iloc[1: , :]
    df[layer_name] = pd.to_numeric(df[layer_name],downcast="float")
    df['time'] = pd.to_datetime(df['time'].astype('str'))
    #find the max or min or the mean for every possible date! this needs to be changed!
    df[layer_name] = df.groupby('time')[layer_name].transform(max_min_mean)
    
    df.drop_duplicates(subset=['time'], inplace=True)
    df_length = len(df)
    all_date = []
    all_values = []
    allData = []
    if df_length <= x:
        #take every value
        all_date = df["time"].to_numpy()
        all_values = df[layer_name].astype(float).to_numpy()
    else:
        every_nth_rows = int(df_length / x)
        df = df[::every_nth_rows]
        all_date = df["time"].to_numpy()
        all_values = df[layer_name].astype(float).to_numpy()
    
    allData = [all_date.tolist(),all_values.tolist(),layer_name]
    return allData
    
    
      
def getMaxMomentGraphic(dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,latitude2,longitude2,latitude3,longitude3,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end):
    #now since the indicators' data are few, we take all the data of every possible points and find the maximum of every moment
    #this needs to be changed once the indicators have more data
    if is_indicator == "true":
      #take every possible data and find the maximum moment by moment!!!!!!!
      return getMaxMinMomentIndicatorGraphic("max",dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,latitude2,longitude2,latitude3,longitude3,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end)

    else:
      allData1 = getMaxMinMeanMomentGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end)
      allData2 = getMaxMinMeanMomentGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude2,longitude2,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end)
      allData3 = getMaxMinMeanMomentGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude3,longitude3,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end)
      maximum_value = np.maximum(allData1[1],allData2[1])
      maximum_value1 = np.maximum(maximum_value,allData3[1])
      allData = [allData1[0],maximum_value1.tolist(),allData1[len(allData1)-2],allData1[len(allData1)-1]]
      return allData

def getMinMomentGraphic(dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,latitude2,longitude2,latitude3,longitude3,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end):
    if is_indicator == "true":
      #take every possible data and find the minimum moment by moment!!!!!!!
      return getMaxMinMomentIndicatorGraphic("min",dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,latitude2,longitude2,latitude3,longitude3,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end)

    else:
      allData1 = getMaxMinMeanMomentGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end)
      allData2 = getMaxMinMeanMomentGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude2,longitude2,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end)
      allData3 = getMaxMinMeanMomentGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude3,longitude3,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end)
      minimum_value = np.minimum(allData1[1],allData2[1])
      minimum_value1 = np.minimum(minimum_value,allData3[1])
      allData = [allData1[0],minimum_value1.tolist(),allData1[len(allData1)-2],allData1[len(allData1)-1]]
      return allData

def getMeanMomentGraphic(dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,latitude2,longitude2,latitude3,longitude3,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end):
    if is_indicator == "true":
      #take every possible data and find the minimum moment by moment!!!!!!!
      return getMaxMinMomentIndicatorGraphic("mean",dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,latitude2,longitude2,latitude3,longitude3,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end)

    else:
      allData1 = getMaxMinMeanMomentGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end)
      allData2 = getMaxMinMeanMomentGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude2,longitude2,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end)
      allData3 = getMaxMinMeanMomentGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude3,longitude3,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end)
      all_arrays = [allData1[1],allData2[1],allData3[1]]
      average_array = np.array(all_arrays,dtype=float).mean(axis=0)
      allData=[allData1[0],average_array.tolist(),allData1[len(allData1)-2],allData1[len(allData1)-1]]
      return allData

def getDataGraphicPolygon(dataset_id,layer_name,time_start,time_finish,latMin,longMin,latMax,longMax,num_parameters,range_value,is_indicator):
    url = url_is_indicator(is_indicator,True,True,dataset_id=dataset_id,layer_name=layer_name,time_start=time_start,time_finish=time_finish,latMin=latMin,
                            longMin=longMin,latMax=latMax,longMax=longMax,num_parameters=num_parameters,range_value=range_value)
    df = pd.read_csv(url, dtype = 'unicode')
    unit = df[layer_name][0]
    df = df.iloc[1: , :]
    n_values = len(df)
    allData = []
    values = []
    dates = []
    coordinates = []
    layerName = []
    i=0
    if n_values <= x:  #all the data
      for index,row in df.iterrows():
            layerName.insert(i,layer_name)
            try:
                coordinates.insert(i,np.array([float(row["latitude"]),float(row["longitude"])]))
            except ValueError:
                print("Not a float!")
            values.insert(i,row[layer_name])
            dates.insert(i,row["time"])
            i+=1
    else:  #one every nvalues/x data
      every_nth_rows = int( n_values / x )
      df = df[::every_nth_rows]
      for index,row in df.iterrows():
            layerName.insert(i,layer_name)
            try:
                coordinates.insert(i,[float(row["latitude"]),float(row["longitude"])])
            except ValueError:
                print("Not a float!")
            values.insert(i,row[layer_name])
            dates.insert(i,row["time"])
            i+=1

    allData=[values,coordinates,dates,unit,layerName]
    return allData
 
def getDataGraphicIndicatorAnnualMean(all_points,all_dates,unit,layer_name,latitude_value,longitude_value):
  #first we create the dataframe from all the lists
  df = pd.DataFrame(list(zip(all_points,all_dates)),
                    columns=[layer_name,"time"])
  df = df.assign(latitude=latitude_value)
  df = df.assign(longitude=longitude_value)
  df[layer_name] = pd.to_numeric(df[layer_name],downcast="float")
  df['time'] = pd.to_datetime(df['time'].astype('str'))
  df = df.groupby([(df.time.dt.day),(df.time.dt.month),df.latitude,df.longitude])[layer_name].mean()
  return df.to_json()

def getDataGraphicAnnualGeneric(dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end):
    url = url_is_indicator(is_indicator,True,False,dataset_id=dataset_id,layer_name=layer_name,time_start=time_start,time_finish=time_finish,latitude=latitude1,
                            longitude=longitude1,num_parameters=num_parameters,range_value=range_value)
    print(url)
    df = pd.read_csv(url, dtype='unicode')
    unit = df[layer_name][0]
    df = df.iloc[1: , :]
    df[layer_name] = pd.to_numeric(df[layer_name],downcast="float")
    df['time'] = pd.to_datetime(df['time'].astype('str'))
    df['unit']=unit
    df = df.groupby([(df.time.dt.day),(df.time.dt.month),(df.unit)])[layer_name].mean()
    return df.to_json()


def getDataGraphicAnnualMean(dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,latitude2,longitude2,latitude3,longitude3,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end):
  graphic1=getDataGraphicAnnualGeneric(dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end)
  graphic2=getDataGraphicAnnualGeneric(dataset_id,layer_name,time_start,time_finish,latitude2,longitude2,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end)
  graphic3=getDataGraphicAnnualGeneric(dataset_id,layer_name,time_start,time_finish,latitude3,longitude3,num_parameters,range_value,is_indicator,lat_start,long_start,lat_end,long_end)
  allData=[graphic1,graphic2,graphic3]
  return allData

def getDataAnnualPolygon(dataset_id,layer_name,time_start,time_finish,latMin,longMin,latMax,longMax,num_parameters,range_value,is_indicator):
    url = url_is_indicator(is_indicator,True,True,dataset_id=dataset_id,layer_name=layer_name,time_start=time_start,time_finish=time_finish,latMin=latMin,
                            longMin=longMin,latMax=latMax,longMax=longMax,num_parameters=num_parameters,range_value=range_value)
    df = pd.read_csv(url, dtype = 'unicode')
    unit = df[layer_name][0]
    df = df.iloc[1: , :]
    n_values = len(df)
    if n_values > x:
      every_nth_rows = int( n_values / x)
      df = df[::every_nth_rows]
      df[layer_name] = pd.to_numeric(df[layer_name],downcast="float")
      df['time'] = pd.to_datetime(df['time'].astype('str'))
      df['unit']=unit
      df = df.groupby([(df.time.dt.day),(df.time.dt.month) ,(df["latitude"]),(df["longitude"]),(df.unit)])[layer_name].mean()
      return df.to_json()
    
    else:
      df[layer_name] = pd.to_numeric(df[layer_name],downcast="float")
      df['time'] = pd.to_datetime(df['time'].astype('str'))
      df['unit']=unit
      df = df.groupby([(df.time.dt.day),(df.time.dt.month) ,(df["latitude"]),(df["longitude"]),(df.unit)])[layer_name].mean()
      return df.to_json()

def percentile(percentile,dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,latitude2,longitude2,latitude3,longitude3,num_parameters,range_value,is_indicator,latMin,longMin,latMax,longMax):
  if is_indicator == "false":
      allData1 = getMaxMinMeanMomentGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,num_parameters,range_value,is_indicator,latMin,longMin,latMax,longMax)
      allData2 = getMaxMinMeanMomentGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude2,longitude2,num_parameters,range_value,is_indicator,latMin,longMin,latMax,longMax)
      allData3 = getMaxMinMeanMomentGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude3,longitude3,num_parameters,range_value,is_indicator,latMin,longMin,latMax,longMax)
      result_percentile=[]
      all_values1=allData1[1]
      all_values2=allData2[1]
      all_values3=allData3[1]
      all_date=allData1[0]
      unit=allData1[len(allData1)-1]
      allData=[]
      i=0
      for date,val1,val2,val3 in np.nditer([all_date,all_values1,all_values2,all_values3], flags=["refs_ok"]): 
          array_percentile = [float(val1),float(val2),float(val3)]
          result_percentile.insert(i,percentileFunction(array_percentile,percentile))
      
      result_percentile.reverse()
      allData=[all_date,result_percentile,layer_name,unit]
      return allData
  else:
      allData1 = getMaxMinMeanMomentGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,num_parameters,range_value,is_indicator,latMin,longMin,latMax,longMax)
      result_percentile=[]
      all_values1=allData1[1]
      all_date=allData1[0]
      unit = "Not available"
      allData=[]
      i=0
      for date,val1 in np.nditer([all_date,all_values1], flags=["refs_ok"]): 
          array_percentile = [float(val1)]
          result_percentile.insert(i,percentileFunction(array_percentile,percentile))
      
      result_percentile.reverse()
      allData=[all_date,result_percentile,layer_name,unit]
      return allData
      

    


def percentileFunction(arr,percentile):
    #sort the array
    arr.sort()
    k = len(arr)*percentile
    if (isinstance(k,int) & len(arr)>1):
        #is an integer, mean between the k-nth and the (k+1)-nth value
        mean = (arr[k-1] + arr[k]) / 2
        return mean
    else:
        index_array=round(k)
        return arr[index_array-1]

def getDataVectorial(dataset_id,layer_name,date_start,latitude_start,latitude_end,longitude_start,longitude_end,num_param,range_value,is_indicator):
  #print("ARRIVO PRIMA DI URL_IS_IND")
  url = url_is_indicator(is_indicator,False,False,dataset_id=dataset_id,layer_name=layer_name,date_start=date_start,latitude_start=latitude_start,latitude_end=latitude_end,
                        longitude_start=longitude_start,longitude_end=longitude_end,num_param=num_param,range_value=range_value)
  print("URL DATA VECTORIAL========",url)
  df = pd.read_csv(url, dtype='unicode')
  allData=[]
  values=[]
  lat_coordinates=[]
  long_coordinates=[]

  i=0
  for index,row in df.iterrows():
    values.insert(i,row[layer_name])
    lat_coordinates.insert(i,row["latitude"])
    long_coordinates.insert(i,row["longitude"])          
    i+=1
  del values[0]
  del lat_coordinates[0]
  del long_coordinates[0]

  [float(i) for i in values]

  value_min = min(values)
  value_max = max(values)


  allData=[values,lat_coordinates,long_coordinates,value_min,value_max]

  return allData

def getDataPolygonNew(dataset_id,layer_name,date_start,date_end,lat_lng_obj,operation,time_op,num_param,range_value,is_indicator,lat_min,lat_max,lng_min,lng_max,parametro_agg):
  # print("ARRIVO PRIMA DI URL_IS_IND")
  # print("Lat_lng_obj=======",lat_lng_obj)
  # Define the polygon vertices
   #latitudes and longitudes from the frontend  
   #


  start_time = time.time()
  print("STARTED GETDATAPOLYGONNEW!")
  vertices = []
  
  for lat_lng in lat_lng_obj:
    vertices.append((float(lat_lng["lat"]),float(lat_lng["lng"])))
  
  shapely_polygon = ShapelyPolygon(vertices)
  pol_vertices_str = str(vertices[0][0]).replace(" ","")
  key_cached = dataset_id + "_" + pol_vertices_str
  xmin = None
  ymin = None
  xmax = None
  ymax = None
  area = None
  circ = None
  #print("KEY CACHED",key_cached)

  if cache.get(key_cached) is None:
    print("CACHE MISS!")
    # Definisci i limiti del poligono
    xmin, ymin, xmax, ymax = shapely_polygon.bounds
  # distanze = []
    circ = shapely_polygon.length
    print("circ", circ)
    area = shapely_polygon.area
    print("area =", area)

  # 2.23 = circonferenza poligono piccolo
  # 8.54 = circonferenza poligono grande
  # 4.67 = circonferenza poligono marche
  # 10.09 = circonferenza poligono puglia

  # 0.24 = area poligono piccolo
  # 3.11 = area poligono grande
  # 1.17 = area poligono marche
  # 2.33 = area poligono puglia
    if area > 2:
      step = 0.3
    elif area < 2 and area > 1:
      step = 0.2
    else:
      step = 0.1
    # distanza = sqrt((x2 - x1)^2 + (y2 - y1)^2)

    #anomaly 0.01 2378 points 625.62 seconds poligono più piccolo
    #anomaly 0.05 75 points 19.05 seconds poligono più piccolo
    #anomaly 0.05 1244 points 335.21 seconds croazia(poligono più grande)
    #r95p yearly 0.05 75 points 23.31 seconds poligono più piccolo

    #Salva tutte le coordinate dei punti interni al poligono
    points_inside_polygon = []
    for x in range(int(xmin/step), int(xmax/step)):
        for y in range(int(ymin/step), int(ymax/step)):
            point = Point(x*step, y*step)
            if point.within(shapely_polygon):
                points_inside_polygon.append((x*step, y*step))


    # Visualizza le coordinate dei punti all'interno del poligono
    # print("PUNTI INTERNI AL POLIGONO =", points_inside_polygon)
    print("PUNTI INTERNI AL POLIGONO LENGHT =", len(points_inside_polygon))
    df_polygon = pd.DataFrame(columns=['time','lat_lng', 'value'])
    
    i=0
    dataTable = []
    for point in points_inside_polygon:
      url = url_is_indicator(is_indicator,True,False,dataset_id=dataset_id,layer_name=layer_name,time_start=date_start,time_finish=date_end,latitude=str(point[0]),
                            longitude=str(point[1]),num_parameters=num_param,range_value=range_value)
      print("URL DATA VECTORIAL========",url)
      df = pd.read_csv(url, dtype='unicode')
      # DA SISTEMARE QUI!!!!!!!!!!!***********************************
      try:
        for index,row in df.iterrows():
          if parametro_agg:
            if len(dataTable) == 0:
              dataTable.append({row["time"], row["latitude"],row["longitude"],row[parametro_agg],row[layer_name]})
            if index != 0:
              df_polygon.loc[i] = [row["time"],"(" + row["latitude"]+","+row["longitude"] + ")",row[layer_name]]
              dataTable.append({row["time"], row["latitude"],row["longitude"],row[parametro_agg],row[layer_name]})
              i+=1
          else:
            if len(dataTable) == 0:
              dataTable.append({row["time"], row["latitude"],row["longitude"],row[layer_name]})
            if index != 0:
              df_polygon.loc[i] = [row["time"],"(" + row["latitude"]+","+row["longitude"] + ")",row[layer_name]]
              dataTable.append({row["time"], row["latitude"],row["longitude"],row[layer_name]})
              i+=1
      except Exception as e:
          print("EXCEPTION",e)
          return str(e)


    df_polygon = df_polygon.drop_duplicates(subset=["time","lat_lng","value"], keep='first')
        # print("df_polygon after drop duplicates",df_polygon.head())
    df_polygon["value"] = pd.to_numeric(df_polygon["value"])
    #a seconda del valore di operation e di time_op viene fatta l'operazione7
    df_polygon["time"] = pd.to_datetime(df_polygon["time"]) #converto la colonna time in datetime


    # ops = {
    # "avg": {"default": "mean", "month": lambda x: x.dt.month.mean(), "day": lambda x: x.dt.day.mean()},
    # "min": {"default": "min", "month": lambda x: x.dt.month.min(), "day": lambda x: x.dt.day.min()},
    # "max": {"default": "max", "month": lambda x: x.dt.month.max(), "day": lambda x: x.dt.day.max()},
    # "10th_perc": {"default": lambda x: x.quantile(0.1), "month": lambda x: x.dt.month.quantile(0.1), "day": lambda x: x.dt.day.quantile(0.1)},
    # "90th_perc": {"default": lambda x: x.quantile(0.9), "month": lambda x: x.dt.month.quantile(0.9), "day": lambda x: x.dt.day.quantile(0.9)},
    # "median": {"default": "median", "month": lambda x: x.dt.month.median(), "day": lambda x: x.dt.day.median()},
    # "sum" : {"default": "sum", "month": lambda x: x.dt.month.sum(), "day": lambda x: x.dt.day.sum()},
    # }

    # groupby_col = "time" if time_op == "default" else df_polygon["time"].dt
    # agg_func = ops[operation][time_op]

    # #AGG IS USED TO APPLY AN AGGREGATE FUNCTION AND YOU NEED TO PASS IT THE NAME OF THE FUNCTION (min,avg,max etc)!!!
    # res_values = df_polygon.groupby(groupby_col)["value"].agg(agg_func) #AGG IS USED TO APPLY AN AGGREGATE FUNCTION

        # print("df_polygon after convert to float",df_polygon.head())
    res_values = df_polygon.groupby("time")["value"].mean()
          # print("mean_values",mean_values)
    df_polygon = df_polygon.drop_duplicates(subset=["time"], keep='first')
    print("key_cached",key_cached)
    allData = []
    list_time = list(df_polygon["time"])
    list_value = list(res_values.values)
    for i in range(len(list_time)):
      data_pol = {}
      data_pol["x"] = list_time[i]
      data_pol["y"] = list_value[i]
      allData.append({"dataPol": data_pol})

    for i in range(len(dataTable)):
      data_table = {}
      data_table["time"] = dataTable[i]["time"]
      data_table["latitude"] = dataTable[i]["latitude"]
      data_table["longitude"] = dataTable[i]["longitude"]
      data_table[layer_name] = dataTable[i][layer_name]
      if parametro_agg:
        data_table[parametro_agg] = dataTable[i][parametro_agg]
      allData.append({"dataTable": data_table})
    
    
    # allData = [list(mean_values.values),list(df_polygon["time"])]
    cache.set(key_cached,json.dumps(allData),timeout=None) #it never expires NOT GOOD!
    print("cache setted! Cache key", cache.get(key_cached))
          # print("allData",allData)
    print("TIME GETDATAPOLYGONNEW {:.2f} seconds".format(time.time()-start_time))
          # print("list(df_polygon['time'])",list(df_polygon["time"]))
    return allData
  
  else:
    print("CACHE HIT!")
    print("CACHE TIME: ",time.time() - start_time)
    pol_from_cache = json.loads(cache.get(key_cached))
    return pol_from_cache
    
  # # Check if the point is inside the polygon
    # df_polygon = pd.DataFrame(columns=["time","lat_lng","value"])
    # i = 0
    #   # print("ARRIVO PRIMA DI URL_IS_IND")
    #   # print("num_param",num_param)
    #   # print("lat_min,lat_max,lng_min,lng_max",lat_min,lat_max,lng_min,lng_max)
    # url = url_is_indicator(is_indicator,False,False,dataset_id=dataset_id,layer_name=layer_name,time_start=date_start,time_finish=date_end,latitude_start=lat_min,latitude_end=lat_max,
    #                         longitude_start=lng_min,longitude_end=lng_max,num_param=num_param,range_value=range_value)
    # print("URL DATA VECTORIAL========",url)
    # df = pd.read_csv(url, dtype='unicode')
    # for index,row in df.iterrows():
    #   if index != 0:
    #     point = Point(float(row["latitude"]),float(row["longitude"]))
    #     is_inside = shapely_polygon.contains(point)
    #     if is_inside:
    #      # print("The point is inside the polygon.",row["time"],"(" + row["latitude"]+","+row["longitude"] + ")",row[layer_name])
    #       df_polygon.loc[i] = [row["time"],"(" + row["latitude"]+","+row["longitude"] + ")",row[layer_name]]
    #       i += 1
    #     else:
    #       continue
      
    #     # print("df_polygon",df_polygon.head())
    
    # df_polygon = df_polygon.drop_duplicates(subset=["lat_lng"], keep='first')
    # print("NUMBER OF POINTS INSIDE THE POLYGON=====",len(list(df_polygon["lat_lng"])))
    # df_polygon = df_polygon.drop_duplicates(subset=["time","lat_lng","value"], keep='first')
    #     # print("df_polygon after drop duplicates",df_polygon.head())
    # df_polygon["value"] = pd.to_numeric(df_polygon["value"])
    #     # print("df_polygon after convert to float",df_polygon.head())
    # mean_values = df_polygon.groupby("time")["value"].mean()
    #       # print("mean_values",mean_values)
    # df_polygon = df_polygon.drop_duplicates(subset=["time"], keep='first')
    #       # print("list(df_polygon['time'])",list(df_polygon["time"]))
    # allData = [list(mean_values.values),list(df_polygon["time"])]
    # #save it to the cache!
    # #time=31536000 is one year!
    # print("key_cached",key_cached)
    # cache.set(key_cached,json.dumps(allData),timeout=None) #it never expires NOT GOOD!
    # print("cache setted! Cache key", cache.get(key_cached))
    #       # print("allData",allData)
    # print("TIME GETDATAPOLYGONNEW {:.2f} seconds".format(time.time()-start_time))
    # return allData



 



    # allData=[mean_value.values,list(df_calculate["time"])]

  
    # return allData

      
      
# is_inside = shapely_polygon.contains(point)

# if is_inside:
#     print("The point is inside the polygon.")
# else:
#     print("The point is outside the polygon.")
  # url = url_is_indicator(is_indicator,False,False,dataset_id=dataset_id,layer_name=layer_name,time_start=date_start,time_finish=date_end,latitude_start=latitude_start,latitude_end=latitude_end,
  #                       longitude_start=longitude_start,longitude_end=longitude_end,num_param=num_param,range_value=range_value)
  # print("URL DATA VECTORIAL========",url)
  # df = pd.read_csv(url, dtype='unicode')
  # allData=[]
  # values=[]
  # lat_coordinates=[]
  # long_coordinates=[]

  # i=0
  # for index,row in df.iterrows():
  #   values.insert(i,row[layer_name])
  #   lat_coordinates.insert(i,row["latitude"])
  #   long_coordinates.insert(i,row["longitude"])          
  #   i+=1
  # del values[0]
  # del lat_coordinates[0]
  # del long_coordinates[0]

  # [float(i) for i in values]

  # value_min = min(values)
  # value_max = max(values)


  # allData=[values,lat_coordinates,long_coordinates,value_min,value_max]

  # return allData
 
         




def createArrow(datasetId1,datasetId2,layer_name1,date_start1,num_param1,range_value1,layer_name2,date_start2,latitude_start,latitude_end,longitude_start,longitude_end,num_param2,range_value2):
  lat_coordinates1=[]
  long_coordinates1=[]
  lat_coordinates2=[]
  long_coordinates2=[]
  values1=[]
  values2=[]
  allValuesArrow=[]


  if (num_param1>3):
    url1 = ERDDAP_URL+"/griddap/" + datasetId1 + ".csv?" + layer_name1 + "%5B(" + date_start1 + "):1:(" + date_start1 + ")%5D%5B(" + str(range_value1) + "):1:(" + str(range_value1) + ")%5D%5B(" + latitude_start + "):1:(" + latitude_end + ")%5D%5B(" + longitude_start + "):1:(" + longitude_end + ")%5D"
  else:
    url1 = ERDDAP_URL+"/griddap/" + datasetId1 + ".csv?" + layer_name1 + "%5B(" + date_start1 + "):1:(" + date_start1+ ")%5D%5B(" + latitude_start + "):1:(" + latitude_end + ")%5D%5B(" + longitude_start + "):1:(" + longitude_end + ")%5D"

  if (num_param2 > 3):
    url2 = ERDDAP_URL+"/griddap/" + datasetId2 + ".csv?" + layer_name2 + "%5B(" + date_start2 + "):1:(" + date_start2 + ")%5D%5B(" + str(range_value2) + "):1:(" + str(range_value2) + ")%5D%5B(" + latitude_start + "):1:(" + latitude_end + ")%5D%5B(" + longitude_start + "):1:(" + longitude_end + ")%5D"
  else:
    url2 = ERDDAP_URL+"/griddap/" + datasetId2 + ".csv?" + layer_name2 + "%5B(" + date_start2 + "):1:(" + date_start2 + ")%5D%5B(" + latitude_start + "):1:(" + latitude_end + ")%5D%5B(" + longitude_start + "):1:(" + longitude_end + ")%5D"
  
  print(url1)
  print(url2)
  df1=pd.read_csv(url1, dtype='unicode')
  df2=pd.read_csv(url2, dtype='unicode')

  i=0
  for index,row in df1.iterrows():
    values1.insert(i,row[layer_name1])
    lat_coordinates1.insert(i,row["latitude"])
    long_coordinates1.insert(i,row["longitude"])
    i+=1

  
  del values1[0]
  del lat_coordinates1[0]
  del long_coordinates1[0]
  
  j=0
  for index,row in df2.iterrows():
    values2.insert(j,row[layer_name2])
    lat_coordinates2.insert(j,row["latitude"])
    long_coordinates2.insert(j,row["longitude"])
    j+=1

  del values2[0]
  del lat_coordinates2[0]
  del long_coordinates2[0]
  
  allValuesArrow=[lat_coordinates1,long_coordinates1,values1,lat_coordinates2,long_coordinates2,values2]
  return allValuesArrow




    




