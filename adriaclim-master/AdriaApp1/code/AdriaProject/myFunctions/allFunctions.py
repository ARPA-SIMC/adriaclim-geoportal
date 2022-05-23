from termios import VLNEXT
from django.db import models
from Dataset.models import Node
import pandas as pd
from Utente.models import Utente
import numpy as np 
import os
from django.contrib import messages
from django.conf import settings


ERDDAP_URL = settings.ERDDAP_URL


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
def getTitle():
  url_datasets = f"{ERDDAP_URL}/info/index.csv?page=1&itemsPerPage=100000"
  df=pd.read_csv(url_datasets,header=None,sep=",",names=["griddap","subset","tabledap","Make A Graph",
                                                           "wms","files","Title","Summary","FGDC","ISO 19115",
                                                           "Info","Background Info","RSS","Email","Institution",
                                                           "Dataset ID"],
                  na_values="Value not available")
  titleList=[]
  

  df1 = df.replace(np.nan, "", regex=True)
  allNodes=Node.objects.all()
  allNodes.delete()
  for index,row in df1.iterrows():
      if row["Title"]!="* The List of All Active Datasets in this ERDDAP *" and row["wms"]!="wms":
        n1=Node(id=row["Dataset ID"],title=row["Title"],metadata_url=row["Info"],griddap_url=row["griddap"],wms=row["wms"],institution=row["Institution"])
        n1.save()
        titleList.append(row["Title"])

  return titleList
 

def getWMS():
  url_datasets = f"{ERDDAP_URL}/info/index.csv?page=1&itemsPerPage=1000000000"
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
    url_datasets = f"{ERDDAP_URL}/info/index.csv?page=1&itemsPerPage=1000000000"
    df = pd.read_csv(url_datasets, header=None, sep=",", names=["griddap", "subset", "tabledap", "Make A Graph",
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
  
    for index, row in df1.iterrows():
        if row["Dataset ID"] == dataset_id:
            get_info = pd.read_csv(row["Info"], header=None, sep=",",
                                   names=["Row Type", "Variable Name", "Attribute Name", "Data Type", "Value"])
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
                   
                if row1["Row Type"] == "attribute" and row1["Attribute Name"] == "institution":
                    attribution_layer = row1["Value"]

                if row1["Row Type"] == "attribute" and row1["Variable Name"] != "time" and row1[
                    "Variable Name"] != "latitude" and row1[
                    "Variable Name"] != "longitude" and row1["Attribute Name"] == "actual_range":
                    values_others = row1["Value"]

                if row1["Row Type"] == "dimension" and row1["Variable Name"] != "time" and row1[
                    "Variable Name"] != "latitude" and row1[
                    "Variable Name"] != "longitude":
                    spacing = row1["Value"]
                    average_spacing_others = spacing.split(",")[2]
                if row1["Row Type"] =="attribute" and row1["Variable Name"] != "time" and row1[
                    "Variable Name"] != "latitude" and row1[
                    "Variable Name"] != "longitude" and row1["Attribute Name"]=="positive":
                    positive_negative=row1["Value"]
                if row1["Row Type"] == "attribute" and row1["Variable Name"]=="latitude" and row1["Attribute Name"]=="actual_range":
                    latitude_range = row1["Value"]
                if row1["Row Type"] == "attribute" and row1["Variable Name"]=="longitude" and row1["Attribute Name"]=="actual_range":
                    longitude_range = row1["Value"]

    our_metadata = [values_others, variable_meta, values_time, title_meta, layer_name, average_spacing_others,
                    attribution_layer,positive_negative,latitude_range,longitude_range]
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
   url_datasets = f"{ERDDAP_URL}/info/index.csv?page=1&itemsPerPage=1000000000"
   df=pd.read_csv(url_datasets,header=None,sep=",",names=["griddap","subset","tabledap","Make A Graph",
                                                           "wms","files","Title","Summary","FGDC","ISO 19115",
                                                           "Info","Background Info","RSS","Email","Institution",
                                                           "Dataset ID"],
                  na_values="Value not available")
   print(df["Title"])
   df1=df.replace(np.nan,"Value not available",regex=True)
   df1.to_html("AdriaProject/templates/allDatasets.html",index=False)
   with open("AdriaProject/templates/allDatasets.html") as file:
       file=file.read()
   file=file.replace("<table ", "<table class='rwd-table'")

   with open("AdriaProject/templates/allDatasets.html","w") as file_to_write:
       file_to_write.write(htmlGetAllDatasets+file)
   
   file_to_write.close()

def getMetadataOfASpecificDataset(dataset_id):
    x=Node.objects.get(id=dataset_id)
    df=pd.read_csv(x.metadata_url,header=None,sep=",",names=["Row Type","Variable Name","Attribute Name","Data Type","Value"],na_values="Value not available")
    df1=df.replace(np.nan,"Value not available",regex=True)
    df1.to_html("AdriaProject/templates/specificDataset.html",index=False)
    with open("AdriaProject/templates/specificDataset.html") as file:
        file=file.read()
    file=file.replace("<table ","<table class='rwd-table'")
    return file



def getDataTable(dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value):
    if(num_parameters>3):
        url = f"{ERDDAP_URL}/griddap/"+dataset_id+".csv?"+layer_name+"%5B("+time_start+"):1:("+time_finish+")%5D%5B("+str(range_value)+"):1:("+str(range_value)+")%5D%5B("+latitude+"):1:("+latitude+")%5D%5B("+longitude+"):1:("+longitude+")%5D"
    else:
        url = f"{ERDDAP_URL}/griddap/"+dataset_id+".csv?"+layer_name+"%5B("+time_start+"):1:("+time_finish+")%5D%5B("+latitude+"):1:("+latitude+")%5D%5B("+longitude+"):1:("+longitude+")%5D"
    #http://erddap-dev.cmcc-opa.eu/erddap/griddap/atm_regional_1f91_1673_845b.htmlTable?vegetfrac%5B(1969-12-30):1:(2005-11-20T00:00:00Z)%5D%5B(13):1:(13.0)%5D%5B(-90):1:(-90.0)%5D%5B(180.45724):1:(180.4572)%5D
    df=pd.read_csv(url,dtype='unicode')
    df.to_html("AdriaProject/templates/getData.html",index=False)
    with open("AdriaProject/templates/getData.html") as file_to_return:
      file_to_return=file_to_return.read()
    
    file_to_return=file_to_return.replace("<table","<table id='tableData' style='width:100%'")
    
    return file_to_return

def getDataGraphic(dataset_id,layer_name,time_start,time_finish,latitude,longitude,num_parameters,range_value):
    if (num_parameters > 3):
        url = f"{ERDDAP_URL}/griddap/" + dataset_id + ".csv?" + layer_name + "%5B(" + time_start + "):1:(" + time_finish + ")%5D%5B(" + str(range_value) + "):1:(" + str(range_value) + ")%5D%5B(" + latitude + "):1:(" + latitude + ")%5D%5B(" + longitude + "):1:(" + longitude + ")%5D"
    else:
        url = f"{ERDDAP_URL}/griddap/" + dataset_id + ".csv?" + layer_name + "%5B(" + time_start + "):1:(" + time_finish + ")%5D%5B(" + latitude + "):1:(" + latitude + ")%5D%5B(" + longitude + "):1:(" + longitude + ")%5D"
    df = pd.read_csv(url, dtype='unicode')
    allData=[]
    values=[]
    dates=[]
    i=0
    for index,row in df.iterrows():
        values.insert(i,row[layer_name])
        dates.insert(i,row["time"])
        i+=1
    unit = values[0]
    del values[0]
    del dates[0]

    allData=[values,dates,unit]
    return allData

def getDataVectorial(dataset_id,layer_name,date_start,latitude_start,latitude_end,longitude_start,longitude_end,num_param,range_value):
 if (num_param > 3):
        url = f"{ERDDAP_URL}/griddap/" + dataset_id + ".csv?" + layer_name + "%5B(" + date_start + "):1:(" + date_start + ")%5D%5B(" + str(range_value) + "):1:(" + str(range_value) + ")%5D%5B(" + latitude_start + "):1:(" + latitude_end + ")%5D%5B(" + longitude_start + "):1:(" + longitude_end + ")%5D"
 else:
        url = f"{ERDDAP_URL}/griddap/" + dataset_id + ".csv?" + layer_name + "%5B(" + date_start + "):1:(" + date_start+ ")%5D%5B(" + latitude_start + "):1:(" + latitude_end + ")%5D%5B(" + longitude_start + "):1:(" + longitude_end + ")%5D"
 df = pd.read_csv(url, dtype='unicode')
 allData=[]
 values=[]
 lat_coordinates=[]
 long_coordinates=[]
 value_min=0.0
 value_max=0.0
 i=0
 for index,row in df.iterrows():
          values.insert(i,row[layer_name])
          lat_coordinates.insert(i,row["latitude"])
          long_coordinates.insert(i,row["longitude"])          
          i+=1
 del values[0]
 del lat_coordinates[0]
 del long_coordinates[0]

 for value in values:
   if float(value)<value_min:
     value_min=float(value)
   elif float(value)>value_max:
     value_max=float(value)

 print(value_max)
 print(value_min)
 allData=[values,lat_coordinates,long_coordinates,value_min,value_max]
 return allData
         




def createArrow(datasetId1,datasetId2,layer_name1,date_start1,num_param1,range_value1,layer_name2,date_start2,latitude_start,latitude_end,longitude_start,longitude_end,num_param2,range_value2):
  lat_coordinates1=[]
  long_coordinates1=[]
  lat_coordinates2=[]
  long_coordinates2=[]
  values1=[]
  values2=[]
  allValuesArrow=[]


  if (num_param1>3):
    url1 = f"{ERDDAP_URL}/griddap/" + datasetId1 + ".csv?" + layer_name1 + "%5B(" + date_start1 + "):1:(" + date_start1 + ")%5D%5B(" + str(range_value1) + "):1:(" + str(range_value1) + ")%5D%5B(" + latitude_start + "):1:(" + latitude_end + ")%5D%5B(" + longitude_start + "):1:(" + longitude_end + ")%5D"
  else:
    url1 = f"{ERDDAP_URL}/griddap/" + datasetId1 + ".csv?" + layer_name1 + "%5B(" + date_start1 + "):1:(" + date_start1+ ")%5D%5B(" + latitude_start + "):1:(" + latitude_end + ")%5D%5B(" + longitude_start + "):1:(" + longitude_end + ")%5D"

  if (num_param2 > 3):
    url2 = f"{ERDDAP_URL}/griddap/" + datasetId2 + ".csv?" + layer_name2 + "%5B(" + date_start2 + "):1:(" + date_start2 + ")%5D%5B(" + str(range_value2) + "):1:(" + str(range_value2) + ")%5D%5B(" + latitude_start + "):1:(" + latitude_end + ")%5D%5B(" + longitude_start + "):1:(" + longitude_end + ")%5D"
  else:
    url2 = f"{ERDDAP_URL}/griddap/" + datasetId2 + ".csv?" + layer_name2 + "%5B(" + date_start2 + "):1:(" + date_start2 + ")%5D%5B(" + latitude_start + "):1:(" + latitude_end + ")%5D%5B(" + longitude_start + "):1:(" + longitude_end + ")%5D"

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




    




