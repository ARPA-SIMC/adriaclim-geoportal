import math
from pydoc import resolve
from math import isnan
from scipy import stats
from termios import VLNEXT
from statistics import mean, median, stdev
from django.db import models, transaction
from django.db.models import Q
from Dataset.models import Node, Indicator, Polygon  # ,Cache
import pandas as pd
import csv
import geopandas as gpd
from django.contrib.gis.geos import Point 
from django.contrib.gis.geos import Polygon as GeosPolygon
from django.contrib.gis.geos import GEOSGeometry
import urllib
from Utente.models import Utente
import numpy as np
import os
import asyncio
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
from shapely.geometry import Polygon as ShapelyPolygon
from shapely.geometry import Point as ShapelyPoint
import shapely.speedups
from django.forms import model_to_dict
from postgres_copy import CopyManager
from sklearn.linear_model import LinearRegression



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

htmlGetData = """<style>
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
x = 500000
months = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}
# I need to save in the cache the url and corresponding value!


def download_with_cache(u):
    cache_key = u  # needs to be unique
    cache_time = 43200  # time in seconds for cache to be valid (now it is 12 hours)
    output_value = cache.get(key=cache_key)  # returns None if no key-value pair
    # print("output_value: ",output_value)
    if output_value == None:
        # if is none we save it in the cache and returns it
        try:
            output_value = urllib.request.urlopen(cache_key).read()
        except Exception as e:
            return "fuoriWms"
        if output_value:
            output_value = output_value.decode("utf-8")
            cache.set(key=cache_key, value=output_value,timeout=cache_time)
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
    try:
        q = download_with_cache(u)
        if q:
            return io.StringIO(q)
        else:
            return None
    except Exception as e:
        return "fuoriWms"


def getIndicator(id):
    q = Node.objects.filter(id=id)
    if q.count() == 0:
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
    if variable == "depth":
        return ["plev", "range"]
    if variable == "plev":
        return ["depth", "range"]
    else:
        return [variable, "range"]


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

    selVar = [kwargs["variable"]]

    tipo = getIndicatorDataFormat(ind)

    griddap = tipo == "griddap"

    if griddap and onlyFirstVariable and va.count() > 1:
        va = [va[0]]

    if griddap and "variable" in kwargs:
        va = [kwargs["variable"]]

    if skipDimensions:
        di = []
    
    va = selVar

    query = "?"

    if griddap:
        for v in va:
            if query != "?":
                query = query + ","
            query = query + v
            for d in di:
                query = query + "%5B("

                if d in kwargs and not (d + "Min") in kwargs:
                    query = query + kwargs[d]
                elif (d + "Min") in kwargs:
                    query = query + kwargs[d + "Min"]
                else:
                    alias = getVariableAliases(d)

                    for al in alias:
                        if al in kwargs:
                            query = query + kwargs[al]
                        elif (al + "Min") in kwargs:
                            query = query + kwargs[al + "Min"]

                query = query + "):1:("

                if d in kwargs and not (d + "Max") in kwargs:
                    query = query + kwargs[d]
                elif (d + "Max") in kwargs:
                    query = query + kwargs[d + "Max"]
                else:
                    alias = getVariableAliases(d)

                    for al in alias:
                        if al in kwargs:
                            query = query + kwargs[al]
                        elif (al + "Max") in kwargs:
                            query = query + kwargs[al + "Max"]

                query = query + ")%5D"

    else:
        for v in va:
            if query != "?":
                query = query + "%2C"
            query = query + v

        for d in va:
            if d != "Indicator":
                if d in kwargs and not (d + "Min") in kwargs:
                    query = query + "&" + d + "%3E=" + kwargs[d]
                elif (d + "Min") in kwargs:
                    query = query + "&" + d + "%3E=" + kwargs[d + "Min"]
                else:
                    alias = getVariableAliases(d)
                    for al in alias:
                        if al in kwargs:
                            query = query + "&" + d + "%3E=" + kwargs[al]
                        elif (al + "Min") in kwargs:
                            query = query + "&" + d + "%3E=" + kwargs[al + "Min"]

                if d in kwargs and not (d + "Max") in kwargs:
                    query = query + "&" + d + "%3C=" + kwargs[d]
                elif (d + "Max") in kwargs:
                    query = query + "&" + d + "%3C=" + kwargs[d + "Max"]
                else:
                    alias = getVariableAliases(d)
                    for al in alias:
                        if al in kwargs:
                            query = query + "&" + d + "%3C=" + kwargs[al]
                        elif (al + "Max") in kwargs:
                            query = query + "&" + d + "%3C=" + kwargs[al + "Max"]

    print("URL + QUERY =", url + query)
    # https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/EOBS_a583_d8f2_21c0.json?very_wet_days_wrt_95th_percentile_of_reference_period%5B(2020-12-31T00:00:00Z):1:(2020-12-31T00:00:00Z)%5D%5B(46.94985982579791):1:(46.94985982579791)%5D%5B(21.94986030317809):1:(21.94986030317809)%5D
    return url + query


def getIndicatorQueryUrlPoint(
    ind, onlyFirstVariable, skipDimensions, lat, lon, time, range, **kwargs
):
    return getIndicatorQueryUrl(
        ind,
        onlyFirstVariable,
        skipDimensions,
        latitude=lat,
        longitude=lon,
        time=time,
        range=range,
    )


def url_is_indicator(is_indicator, is_graph, is_annual, **kwargs):
    # true, true, false
    try:
        if is_indicator == "true" and is_graph == False:
            #print("ENTRO IN URL_IS_INDICATOR LATO TABLEDAP!")
            url = (
                ERDDAP_URL
                + "/tabledap/"
                + kwargs["dataset_id"]
                + ".csv?"
                + "time%2Clatitude%2Clongitude%2C"
                + kwargs["layer_name"]
                + "&time%3E="
                + kwargs["date_start"]
                + "&time%3C="
                + kwargs["date_start"]
            )

        elif is_indicator == "true" and is_graph and is_annual:
            try:
                #print("Entro qui parte 2!!!!!!")
                url = (
                    ERDDAP_URL
                    + "/tabledap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + "time%2Clatitude%2Clongitude%2C"
                    + kwargs["layer_name"]
                    + "&time%3E="
                    + kwargs["time_start"]
                    + "&time%3C="
                    + kwargs["time_finish"]
                    + "&latitude%3E="
                    + kwargs["latitude"]
                    + "&latitude%3C="
                    + kwargs["latitude"]
                    + "&longitude%3E="
                    + kwargs["longitude"]
                    + "&longitude%3C="
                    + kwargs["longitude"]
                )
            except Exception as e1:
                print("Eccezione 2", e1)
                return str(e1)
        elif is_indicator == "true" and is_graph and not is_annual:
            #  url = url_is_indicator(is_indicator,True,False,dataset_id=dataset_id,layer_name=layer_name,time_start=date_start,time_finish=date_end,latitude=str(point[0]),
            #                     longitude=str(point[1]),num_parameters=num_param,range_value=range_value)
            # https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/indicators_wsdi_aba0_0062_8939.csv?time%2Clatitude%2Clongitude%2Cwsdi&time%3E=2021-07-01&time%3C=2050-07-01&latitude%3E=39.688777923584&latitude%3C=41.22824901518532&longitude%3E=14.740385055542&longitude%3C=15.183105468750002
            # https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/arpav_PRCPTOT_yearly.htmlTable?time%2Clatitude%2Clongitude%2CIndicator&time%3E=2021-12-25&time%3C=2022-01-01
            url = (
                ERDDAP_URL
                + "/tabledap/"
                + kwargs["dataset_id"]
                + ".csv?"
                + "time%2Clatitude%2Clongitude%2C"
                + kwargs["layer_name"]
                + "&time%3E="
                + kwargs["time_start"]
                + "&time%3C="
                + kwargs["time_finish"]
                + "&latitude%3E="
                + kwargs["latMin"]
                + "&latitude%3C="
                + kwargs["latMax"]
                + "&longitude%3E="
                + kwargs["longMin"]
                + "&longitude%3C="
                + kwargs["longMax"]
            )

        elif is_indicator == "false" and is_graph == False and is_annual == False:
            if kwargs["num_param"] > 3:
                # https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/adriaclim_WRF_9e77_be3a_4ac6.htmlTable?txx%5B(2036-07-01T09:00:00Z):1:(2036-07-01T09:00:00Z)%5D%5B(37.00147):1:(46.97328)%5D%5B(10.0168):1:(21.98158)%5D
                url = (
                    ERDDAP_URL
                    + "/griddap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + kwargs["layer_name"]
                    + "%5B("
                    + kwargs["time_start"]
                    + "):1:("
                    + kwargs["time_finish"]
                    + ")%5D%5B("
                    + str(kwargs["range_value"])
                    + "):1:("
                    + str(kwargs["range_value"])
                    + ")%5D%5B("
                    + kwargs["latitude_start"]
                    + "):1:("
                    + kwargs["latitude_end"]
                    + ")%5D%5B("
                    + kwargs["longitude_start"]
                    + "):1:("
                    + kwargs["longitude_end"]
                    + ")%5D"
                )
            else:
                url = (
                    ERDDAP_URL
                    + "/griddap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + kwargs["layer_name"]
                    + "%5B("
                    + kwargs["time_start"]
                    + "):1:("
                    + kwargs["time_finish"]
                    + ")%5D%5B("
                    + kwargs["latitude_start"]
                    + "):1:("
                    + kwargs["latitude_end"]
                    + ")%5D%5B("
                    + kwargs["longitude_start"]
                    + "):1:("
                    + kwargs["longitude_end"]
                    + ")%5D"
                )

        elif is_indicator == "false" and is_graph and is_annual == False:
            if kwargs["num_parameters"] > 3:
                url = (
                    ERDDAP_URL
                    + "/griddap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + kwargs["layer_name"]
                    + "%5B("
                    + kwargs["time_start"]
                    + "):1:("
                    + kwargs["time_finish"]
                    + ")%5D%5B("
                    + str(kwargs["range_value"])
                    + "):1:("
                    + str(kwargs["range_value"])
                    + ")%5D%5B("
                    + kwargs["latitude"]
                    + "):1:("
                    + kwargs["latitude"]
                    + ")%5D%5B("
                    + kwargs["longitude"]
                    + "):1:("
                    + kwargs["longitude"]
                    + ")%5D"
                )
            else:
                url = (
                    ERDDAP_URL
                    + "/griddap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + kwargs["layer_name"]
                    + "%5B("
                    + kwargs["time_start"]
                    + "):1:("
                    + kwargs["time_finish"]
                    + ")%5D%5B("
                    + kwargs["latitude"]
                    + "):1:("
                    + kwargs["latitude"]
                    + ")%5D%5B("
                    + kwargs["longitude"]
                    + "):1:("
                    + kwargs["longitude"]
                    + ")%5D"
                )

        elif is_indicator == "false" and is_graph and is_annual:
            if kwargs["num_parameters"] > 3:
                url = (
                    ERDDAP_URL
                    + "/griddap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + kwargs["layer_name"]
                    + "%5B("
                    + kwargs["time_start"]
                    + "):1:("
                    + kwargs["time_finish"]
                    + ")%5D%5B("
                    + str(kwargs["range_value"])
                    + "):1:("
                    + str(kwargs["range_value"])
                    + ")%5D%5B("
                    + kwargs["latMax"]
                    + "):1:("
                    + kwargs["latMin"]
                    + ")%5D%5B("
                    + kwargs["longMax"]
                    + "):1:("
                    + kwargs["longMin"]
                    + ")%5D"
                )

            else:
                url = (
                    ERDDAP_URL
                    + "/griddap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + kwargs["layer_name"]
                    + "%5B("
                    + kwargs["time_start"]
                    + "):1:("
                    + kwargs["time_finish"]
                    + ")%5D%5B("
                    + kwargs["latMax"]
                    + "):1:("
                    + kwargs["latMin"]
                    + ")%5D%5B("
                    + kwargs["longMax"]
                    + "):1:("
                    + kwargs["longMin"]
                    + ")%5D"
                )

        elif is_indicator == "false" and is_graph == False and is_annual:
            if kwargs["num_param"] > 3:
                url = (
                    ERDDAP_URL
                    + "/griddap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + kwargs["layer_name"]
                    + "%5B("
                    + kwargs["date_start"]
                    + "):1:("
                    + kwargs["date_start"]
                    + ")%5D%5B("
                    + str(kwargs["range_value"])
                    + "):1:("
                    + str(kwargs["range_value"])
                    + ")%5D%5B("
                    + kwargs["latitude_start"]
                    + "):1:("
                    + kwargs["latitude_end"]
                    + ")%5D%5B("
                    + kwargs["longitude_start"]
                    + "):1:("
                    + kwargs["longitude_end"]
                    + ")%5D"
                )
            else:
                url = (
                    ERDDAP_URL
                    + "/griddap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + kwargs["layer_name"]
                    + "%5B("
                    + kwargs["date_start"]
                    + "):1:("
                    + kwargs["date_start"]
                    + ")%5D%5B("
                    + kwargs["latitude_start"]
                    + "):1:("
                    + kwargs["latitude_end"]
                    + ")%5D%5B("
                    + kwargs["longitude_start"]
                    + "):1:("
                    + kwargs["longitude_end"]
                    + ")%5D"
                )

        return url
    except Exception as e:
        print("Error", e)
        return str(e)


async def delete_all(param, **kwargs):
    if param == "Node":
        objects = await asyncio.gather(*[asyncio.to_thread(Node.objects.all)])
        await asyncio.gather(*[asyncio.to_thread(obj.delete) for obj in objects])
    elif param == "Polygon":
        # polygon_object = await asyncio.gather(*[asyncio.to_thread(Polygon.objects.all)])
        # print("arrivo qui test")
        # mioOggetto = await asyncio.to_thread(Polygon.objects.all)
        # print("mioOggetto", mioOggetto)
        # print("test",kwargs["id"].title)
        # test_print = await asyncio.gather(*[asyncio.to_thread(type(Polygon.objects))])
        # print("test_print",test_print)
        all_polygons = await asyncio.gather(*[asyncio.to_thread(Polygon.objects.all)])
        # await asyncio.gather(*[asyncio.to_thread(pol.delete) for pol in all_polygons if pol.dataset_id == kwargs["id"]])
        # print("Test_print polygons",test_print)
        # polygons = await asyncio.to_thread(Polygon.objects.filter(dataset_id__title=kwargs["id"].title).all())
        # print("test3",polygons)
        # await asyncio.gather(*[asyncio.to_thread(obj.delete) for obj in polygons])

def deletePoly(param, **kwargs):
    # print("PARAM =", par)
    if param == "Node":
        Node.objects.all().delete()
    elif param == "Polygon":
        obj = Polygon.objects.filter(dataset_id=kwargs["id"])
        obj.delete()

def getAllDatasets():
    start_time = time.time()
    print("Started getAllDatasets()")
    url_datasets = ERDDAP_URL + "/info/index.csv?page=1&itemsPerPage=100000"
    # node_list = []
    asyncio.run(delete_all("Node"))  # delete all existing nodes
    try:
        df = pd.read_table(
            download_with_cache_as_csv(url_datasets),
            header=0,
            sep=",",
            engine="c",
            names=[
                "griddap",
                "subset",
                "tabledap",
                "MakeAGraph",
                "wms",
                "files",
                "Title",
                "Summary",
                "FGDC",
                "ISO 19115",
                "Info",
                "BackgroundInfo",
                "RSS",
                "Email",
                "Institution",
                "DatasetID",
            ],
            na_values="Value not available",
        )

        # print("Time to finish first read_table getAllDatasets() ========= {:.2f} seconds".format(time.time()-start_time))
        df = df.fillna("")
        df.drop(index=df.index[0], axis=0, inplace=True)
    except Exception as e:
        print("Error", e)
        return str(e)
    # all_indicators = Indicator.objects.all()
    # all_indicators.delete()
    # print("All datasets",Node.objects.all())
    for row in df.to_dict(orient="records"):
        info = row["Info"]
        # print("Info",info)
        # for index,row in df.iterrows(): #cambiare iterrows
        # if row["Info"] != "Info" and row["Dataset ID"] != "allDatasets":
        # We take every datasets to fill the full list!
        adriaclim_scale = None
        adriaclim_dataset = None
        adriaclim_timeperiod = None
        adriaclim_model = None
        adriaclim_type = None
        institution = "UNKNOWN"
        time_start = ""
        time_end = ""
        lat_min = None
        lat_max = None
        lng_min = None
        lng_max = None

        variables = 0
        variable_names = ""
        dimensions = 0
        dimension_names = ""
        param_min = 0
        param_max = 0
        node_id = row["DatasetID"]
        metadata_url = row["Info"]
        tabledap_url = row["tabledap"]
        griddap_url = row["griddap"]
        wms_url = row["wms"]
        get_info = pd.read_table(
            download_with_cache_as_csv(info),
            header=None,
            sep=",",
            engine="c",
            names=["RowType", "VariableName", "AttributeName", "DataType", "Value"],
        ).fillna("nan")
        # for index1, row1 in get_info.iterrows():
        get_info.drop(index=get_info.index[0], axis=0, inplace=True)
        get_info = get_info.to_dict(orient="records")
        for row1 in get_info:
            if row1 == get_info[-1] and time_start != "" and time_end != "":
                #print("Last row====", row1)
                defaults = {
                    "adriaclim_dataset": adriaclim_dataset,
                    "adriaclim_model": adriaclim_model,
                    "adriaclim_timeperiod": adriaclim_timeperiod,
                    "adriaclim_scale": adriaclim_scale,
                    "adriaclim_type": adriaclim_type,
                    "title": row["Title"],
                    "metadata_url": metadata_url,
                    "institution": institution,
                    "lat_min": lat_min,
                    "lat_max": lat_max,
                    "lng_min": lng_min,
                    "lng_max": lng_max,
                    "time_start": time_start,
                    "time_end": time_end,
                    "param_min": param_min,
                    "param_max": param_max,
                    "tabledap_url": tabledap_url,
                    "dimensions": dimensions,
                    "dimension_names": dimension_names,
                    "variables": variables,
                    "variable_names": variable_names,
                    "griddap_url": griddap_url,
                    "wms_url": wms_url,
                }
                Node.objects.update_or_create(id=node_id, defaults=defaults)
            else:
                # print("row1")
                # now we create our datasets that we put in our db
                if row1["RowType"] == "dimension":
                    if dimensions > 0:
                        dimension_names = dimension_names + " "

                    dimensions = dimensions + 1
                    dimension_names = dimension_names + row1["VariableName"]

                if row1["RowType"] == "variable":
                    if variables > 0:
                        variable_names = variable_names + " "

                    variables = variables + 1
                    variable_names = variable_names + row1["VariableName"]

                if row1["AttributeName"] == "adriaclim_dataset":
                    adriaclim_dataset = row1["Value"]
                if row1["AttributeName"] == "adriaclim_model":
                    adriaclim_model = row1["Value"]
                if row1["AttributeName"] == "adriaclim_scale":
                    adriaclim_scale = row1["Value"]
                if row1["AttributeName"] == "adriaclim_timeperiod":
                    adriaclim_timeperiod = row1["Value"]
                if row1["AttributeName"] == "adriaclim_type":
                    adriaclim_type = row1["Value"]
                if row1["AttributeName"] == "title":
                    title = row1["Value"]
                if row1["AttributeName"] == "institution":
                    institution = row1["Value"]
                if row1["AttributeName"] == "time_coverage_start":
                    time_start = row1["Value"]
                if row1["AttributeName"] == "time_coverage_end":
                    time_end = row1["Value"]
                if row1["AttributeName"] == "geospatial_lat_min":
                    lat_min = row1["Value"]
                if row1["AttributeName"] == "geospatial_lat_max":
                    lat_max = row1["Value"]
                if row1["AttributeName"] == "geospatial_lon_min":
                    lng_min = row1["Value"]
                if row1["AttributeName"] == "geospatial_lon_max":
                    lng_max = row1["Value"]
                if griddap_url != "":
                    if (
                        row1["AttributeName"] == "actual_range"
                        and row1["VariableName"] != "time"
                        and row1["VariableName"] != "latitude"
                        and row1["VariableName"] != "longitude"
                    ):
                        param_agg = row1["Value"].split(",")
                        param_min = float(param_agg[0])
                        param_max = float(param_agg[1].replace(" ", ""))

                # is_indicator it is used to check if it the dataset is an indicator! in futuro la cambiamo checkando solo adriaclim_dataset!!!!!
                is_indicator = re.search("indicator", row["Title"], re.IGNORECASE)

                if is_indicator and adriaclim_scale is None:
                    adriaclim_scale = "large"

                if adriaclim_timeperiod == "day":
                    adriaclim_timeperiod = "daily"

                if adriaclim_scale is None and not is_indicator:
                    adriaclim_scale = "UNKNOWN"

                if adriaclim_model is None:
                    adriaclim_model = "UNKNOWN"

                if adriaclim_type is None:
                    adriaclim_type = "UNKNOWN"

                if adriaclim_dataset is None:
                    adriaclim_dataset = "no"

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

    print(
        "Time to finish getAllDatasets() ========= {:.2f} seconds".format(
            time.time() - start_time
        )
    )


def getTitle():
    start_time = time.time()
    print("Started getTitle()")
    url_datasets = ERDDAP_URL + "/info/index.csv?page=1&itemsPerPage=100000"
    df = pd.read_csv(
        download_with_cache_as_csv(url_datasets),
        header=0,
        sep=",",
        names=[
            "griddap",
            "subset",
            "tabledap",
            "Make A Graph",
            "wms",
            "files",
            "Title",
            "Summary",
            "FGDC",
            "ISO 19115",
            "Info",
            "Background Info",
            "RSS",
            "Email",
            "Institution",
            "Dataset ID",
        ],
        na_values="Value not available",
    )
    titleList = []

    df1 = df.replace(np.nan, "", regex=True)

    for index, row in df1.iterrows():
        if (
            row["Title"] != "* The List of All Active Datasets in this ERDDAP *"
            and row["wms"] != "wms"
            and not re.search("^indicat*", row["Dataset ID"])
        ):
            titleList.append(row["Title"])

    print(
        "Time to finish getTitle() ========= {:.2f} seconds".format(
            time.time() - start_time
        )
    )
    return titleList


def getIndicators():
    start_time = time.time()
    print("Started getIndicators()")
    url_datasets = ERDDAP_URL + "/info/index.csv?page=1&itemsPerPage=100000"
    df = pd.read_table(
        download_with_cache_as_csv(url_datasets),
        header=0,
        sep=",",
        engine="c",
        names=[
            "griddap",
            "subset",
            "tabledap",
            "Make A Graph",
            "wms",
            "files",
            "Title",
            "Summary",
            "FGDC",
            "ISO 19115",
            "Info",
            "Background Info",
            "RSS",
            "Email",
            "Institution",
            "Dataset ID",
        ],
        na_values="Value not available",
    )
    indicator_list = []
    dataset_list = []
    scale_list = []
    print(
        "Time to finish first read_csv getIndicators() ========= {:.2f} seconds".format(
            time.time() - start_time
        )
    )
    df = df.fillna("")
    Indicator.objects.all().delete()
    for index, row in df.iterrows():
        if (
            row["Info"] != "Info"
            and row["Dataset ID"] != "allDatasets"
            and re.search("indicator", row["Title"], re.IGNORECASE)
        ):
            # if the dataset_id starts with indicat...For now we assume that indicators have this thing in common......
            # we found an indicator so we need to explore its metadata!
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
            get_info = pd.read_table(
                download_with_cache_as_csv(row["Info"]),
                header=None,
                sep=",",
                engine="c",
                names=[
                    "Row Type",
                    "Variable Name",
                    "Attribute Name",
                    "Data Type",
                    "Value",
                ],
            ).fillna("nan")
            for index1, row1 in get_info.iterrows():
                # now we create our indicators that we put in our db

                if row1["Row Type"] == "dimension":
                    if dimensions > 0:
                        dimension_names = dimension_names + " "
                    dimensions = dimensions + 1
                    dimension_names = dimension_names + row1["Variable Name"]

                if row1["Row Type"] == "variable":
                    if variables > 0:
                        variable_names = variable_names + " "
                    variables = variables + 1
                    variable_names = variable_names + row1["Variable Name"]

                if row1["Attribute Name"] == "adriaclim_dataset":
                    adriaclim_dataset = row1["Value"]
                if row1["Attribute Name"] == "adriaclim_model":
                    adriaclim_model = row1["Value"]
                if row1["Attribute Name"] == "adriaclim_scale":
                    adriaclim_scale = row1["Value"]
                if row1["Attribute Name"] == "adriaclim_timeperiod":
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
                adriaclim_scale = "large"

            if adriaclim_model is None:
                adriaclim_model = "UNKNOWN"

            if adriaclim_type is None:
                adriaclim_type = "UNKNOWN"

            if adriaclim_dataset is None:
                # if re.search("^indicat*",row["Dataset ID"]) or re.search("indicator",row["Title"], re.IGNORECASE):
                adriaclim_dataset = "indicator"
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
                new_indicator = Indicator(
                    dataset_id=dataset_id,
                    adriaclim_dataset=adriaclim_dataset,
                    adriaclim_model=adriaclim_model,
                    adriaclim_scale=adriaclim_scale,
                    adriaclim_timeperiod=adriaclim_timeperiod,
                    adriaclim_type=adriaclim_type,
                    title=row["Title"],
                    metadata_url=metadata_url,
                    institution=institution,
                    lat_min=lat_min,
                    lng_min=lng_min,
                    lat_max=lat_max,
                    lng_max=lng_max,
                    time_start=time_start,
                    time_end=time_end,
                    tabledap_url=tabledap_url,
                    dimensions=dimensions,
                    dimension_names=dimension_names,
                    variables=variables,
                    variable_names=variable_names,
                    griddap_url=griddap_url,
                    wms_url=row["wms"],
                )
                new_indicator.save()
                indicator_list.append(new_indicator.title)
                dataset_list.append(adriaclim_dataset)
                scale_list.append(adriaclim_scale)

    print(
        "Time to finish getIndicators() ========= {:.2f} seconds".format(
            time.time() - start_time
        )
    )
    return [indicator_list, dataset_list, scale_list]


def getTitle():
    start_time = time.time()
    print("Started getTitle()")
    url_datasets = ERDDAP_URL + "/info/index.csv?page=1&itemsPerPage=100000"
    df = pd.read_csv(
        download_with_cache_as_csv(url_datasets),
        header=0,
        sep=",",
        names=[
            "griddap",
            "subset",
            "tabledap",
            "Make A Graph",
            "wms",
            "files",
            "Title",
            "Summary",
            "FGDC",
            "ISO 19115",
            "Info",
            "Background Info",
            "RSS",
            "Email",
            "Institution",
            "Dataset ID",
        ],
        na_values="Value not available",
    )
    titleList = []

    df1 = df.replace(np.nan, "", regex=True)

    for index, row in df1.iterrows():
        if (
            row["Title"] != "* The List of All Active Datasets in this ERDDAP *"
            and row["wms"] != "wms"
            and not re.search("^indicat*", row["Dataset ID"])
        ):
            titleList.append(row["Title"])

    print(
        "Time to finish getTitle() ========= {:.2f} seconds".format(
            time.time() - start_time
        )
    )
    return titleList


def getIndicators():
    start_time = time.time()
    print("Started getIndicators()")
    url_datasets = ERDDAP_URL + "/info/index.csv?page=1&itemsPerPage=100000"
    df = pd.read_table(
        download_with_cache_as_csv(url_datasets),
        header=0,
        sep=",",
        engine="c",
        names=[
            "griddap",
            "subset",
            "tabledap",
            "Make A Graph",
            "wms",
            "files",
            "Title",
            "Summary",
            "FGDC",
            "ISO 19115",
            "Info",
            "Background Info",
            "RSS",
            "Email",
            "Institution",
            "Dataset ID",
        ],
        na_values="Value not available",
    )
    indicator_list = []
    dataset_list = []
    scale_list = []
    print(
        "Time to finish first read_csv getIndicators() ========= {:.2f} seconds".format(
            time.time() - start_time
        )
    )
    df = df.fillna("")
    Indicator.objects.all().delete()
    for index, row in df.iterrows():
        if (
            row["Info"] != "Info"
            and row["Dataset ID"] != "allDatasets"
            and re.search("indicator", row["Title"], re.IGNORECASE)
        ):
            # if the dataset_id starts with indicat...For now we assume that indicators have this thing in common......
            # we found an indicator so we need to explore its metadata!
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
            get_info = pd.read_table(
                download_with_cache_as_csv(row["Info"]),
                header=None,
                sep=",",
                engine="c",
                names=[
                    "Row Type",
                    "Variable Name",
                    "Attribute Name",
                    "Data Type",
                    "Value",
                ],
            ).fillna("nan")
            for index1, row1 in get_info.iterrows():
                # now we create our indicators that we put in our db

                if row1["Row Type"] == "dimension":
                    if dimensions > 0:
                        dimension_names = dimension_names + " "
                    dimensions = dimensions + 1
                    dimension_names = dimension_names + row1["Variable Name"]

                if row1["Row Type"] == "variable":
                    if variables > 0:
                        variable_names = variable_names + " "
                    variables = variables + 1
                    variable_names = variable_names + row1["Variable Name"]

                if row1["Attribute Name"] == "adriaclim_dataset":
                    adriaclim_dataset = row1["Value"]
                if row1["Attribute Name"] == "adriaclim_model":
                    adriaclim_model = row1["Value"]
                if row1["Attribute Name"] == "adriaclim_scale":
                    adriaclim_scale = row1["Value"]
                if row1["Attribute Name"] == "adriaclim_timeperiod":
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
                adriaclim_scale = "large"

            if adriaclim_model is None:
                adriaclim_model = "UNKNOWN"

            if adriaclim_type is None:
                adriaclim_type = "UNKNOWN"

            if adriaclim_dataset is None:
                # if re.search("^indicat*",row["Dataset ID"]) or re.search("indicator",row["Title"], re.IGNORECASE):
                adriaclim_dataset = "indicator"
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
                new_indicator = Indicator(
                    dataset_id=dataset_id,
                    adriaclim_dataset=adriaclim_dataset,
                    adriaclim_model=adriaclim_model,
                    adriaclim_scale=adriaclim_scale,
                    adriaclim_timeperiod=adriaclim_timeperiod,
                    adriaclim_type=adriaclim_type,
                    title=row["Title"],
                    metadata_url=metadata_url,
                    institution=institution,
                    lat_min=lat_min,
                    lng_min=lng_min,
                    lat_max=lat_max,
                    lng_max=lng_max,
                    time_start=time_start,
                    time_end=time_end,
                    tabledap_url=tabledap_url,
                    dimensions=dimensions,
                    dimension_names=dimension_names,
                    variables=variables,
                    variable_names=variable_names,
                    griddap_url=griddap_url,
                    wms_url=row["wms"],
                )
                new_indicator.save()
                indicator_list.append(new_indicator.title)
                dataset_list.append(adriaclim_dataset)
                scale_list.append(adriaclim_scale)

    print(
        "Time to finish getIndicators() ========= {:.2f} seconds".format(
            time.time() - start_time
        )
    )
    return [indicator_list, dataset_list, scale_list]


def getWMS():
    url_datasets = ERDDAP_URL + "/info/index.csv?page=1&itemsPerPage=1000000000"
    df = pd.read_csv(
        url_datasets,
        header=None,
        sep=",",
        names=[
            "griddap",
            "subset",
            "tabledap",
            "Make A Graph",
            "wms",
            "files",
            "Title",
            "Summary",
            "FGDC",
            "ISO 19115",
            "Info",
            "Background Info",
            "RSS",
            "Email",
            "Institution",
            "Dataset ID",
        ],
        na_values="",
    )
    df1 = df.replace(np.nan, "", regex=True)
    wmsList = []
    for index, row in df1.iterrows():
        wmsList.append(row["wms"])

    return wmsList


def getMetadataTime1(dataset_id):
    url_datasets = ERDDAP_URL + "/info/index.csv?page=1&itemsPerPage=1000000000"
    df = pd.read_csv(
        download_with_cache_as_csv(url_datasets),
        header=None,
        sep=",",
        names=[
            "griddap",
            "subset",
            "tabledap",
            "Make A Graph",
            "wms",
            "files",
            "Title",
            "Summary",
            "FGDC",
            "ISO 19115",
            "Info",
            "Background Info",
            "RSS",
            "Email",
            "Institution",
            "Dataset ID",
        ],
        na_values="",
    )

    df1 = df.replace(np.nan, "", regex=True)
    our_metadata = []
    variable_meta = ""
    title_meta = ""
    layer_name = ""
    values_time = ""
    attribution_layer = ""
    values_others = ""
    average_spacing_others = ""
    positive_negative = ""
    latitude_range = ""
    longitude_range = ""
    lat_min = ""
    lat_max = ""
    long_min = ""
    long_max = ""
    dimensions = "time, latitude, longitude"
    for index, row in df1.iterrows():
        if row["Dataset ID"] == dataset_id:
            get_info = pd.read_csv(
                download_with_cache_as_csv(row["Info"]),
                header=None,
                sep=",",
                names=[
                    "Row Type",
                    "Variable Name",
                    "Attribute Name",
                    "Data Type",
                    "Value",
                ],
            ).fillna("nan")
            for index1, row1 in get_info.iterrows():
                if row1["Row Type"] == "variable":
                    variable_meta = row1["Value"]
                if (
                    row1["Row Type"] == "attribute"
                    and row1["Attribute Name"] == "title"
                ):
                    title_meta = row1["Value"]
                if row1["Row Type"] == "variable":
                    layer_name = row1["Variable Name"]
                if (
                    row1["Row Type"] == "attribute"
                    and row1["Variable Name"] == "time"
                    and row1["Attribute Name"] == "actual_range"
                ):
                    # 2005-11-20T00:00:00Z
                    values_time = row1["Value"]
                if (
                    row1["Row Type"] == "attribute"
                    and row1["Variable Name"] == "Times"
                    and row1["Attribute Name"] == "actual_range"
                ):
                    # 2005-11-20T00:00:00Z
                    values_time = row1["Value"]

                if (
                    row1["Row Type"] == "attribute"
                    and row1["Attribute Name"] == "institution"
                ):
                    attribution_layer = row1["Value"]

                if (
                    row1["Row Type"] == "attribute"
                    and row1["Variable Name"] != "time"
                    and row1["Variable Name"] != "Times"
                    and row1["Variable Name"] != "latitude"
                    and row1["Variable Name"] != "longitude"
                    and row1["Attribute Name"] == "actual_range"
                ):
                    values_others = row1["Value"]

                if (
                    row1["Row Type"] == "dimension"
                    and row1["Variable Name"] != "time"
                    and row1["Variable Name"] != "Times"
                    and row1["Variable Name"] != "latitude"
                    and row1["Variable Name"] != "longitude"
                ):
                    dimensions += ", " + row1["Variable Name"]
                    spacing = row1["Value"]
                    average_spacing_others = spacing.split(",")[2]
                if (
                    row1["Row Type"] == "attribute"
                    and row1["Variable Name"] != "time"
                    and row1["Row Type"] == "attribute"
                    and row1["Variable Name"] != "Times"
                    and row1["Variable Name"] != "latitude"
                    and row1["Variable Name"] != "longitude"
                    and row1["Attribute Name"] == "positive"
                ):
                    positive_negative = row1["Value"]
                if (
                    row1["Row Type"] == "attribute"
                    and row1["Variable Name"] == "latitude"
                    and row1["Attribute Name"] == "actual_range"
                ):
                    latitude_range = row1["Value"]
                if (
                    row1["Row Type"] == "attribute"
                    and row1["Variable Name"] == "longitude"
                    and row1["Attribute Name"] == "actual_range"
                ):
                    longitude_range = row1["Value"]

    if variable_meta != "nan":
        our_metadata = [
            values_others,
            variable_meta,
            values_time,
            title_meta,
            layer_name,
            average_spacing_others,
            attribution_layer,
            positive_negative,
            latitude_range,
            longitude_range,
        ]
    else:
        is_indicator = True
        our_metadata = [
            values_others,
            dimensions,
            values_time,
            title_meta,
            layer_name,
            average_spacing_others,
            attribution_layer,
            positive_negative,
            latitude_range,
            longitude_range,
            is_indicator,
        ]

    return our_metadata


# def getValuesDatasets(id1,id2):


def getMetadata(dataset_id):
    all_metadata = getMetadataTime1(dataset_id)
    min_max_value = []
    average_spacing_others = []
    final_list = []
    j = 0
    for i in range(len(all_metadata[1])):
        splitted = all_metadata[1][i].split(",")
        if len(splitted) > 3:
            min_max_value.append(all_metadata[0][j])
            average_spacing_others.append(all_metadata[6][j])
            j = j + 1
        else:
            min_max_value.append(0)
            average_spacing_others.append(0)

    final_list = [all_metadata, min_max_value, average_spacing_others]
    return final_list


def listAllDatasets():
    url_datasets = ERDDAP_URL + "/info/index.csv?page=1&itemsPerPage=1000000000"
    url_open = urllib.request.urlopen(url_datasets)
    csvfile = csv.DictReader(
        io.TextIOWrapper(url_open, encoding="utf-8"), delimiter=","
    )
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
        x = Node.objects.get(id=dataset_id)
        url = x.metadata_url.replace(".csv", ".json")
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
            url = indicator.metadata_url.replace(".csv", ".json")
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


def getDataTableIndicator(
    dataset_id,
    layer_name,
    time_start,
    time_finish,
    lat_start,
    lat_end,
    long_start,
    long_end,
    num_parameters,
    range_value,
):
    url = url_is_indicator(
        "true",
        True,
        False,
        dataset_id=dataset_id,
        layer_name=layer_name,
        time_start=time_start,
        time_finish=time_finish,
        latMin=lat_start,
        longMin=long_start,
        latMax=lat_end,
        longMax=long_end,
        num_parameters=num_parameters,
        range_value=range_value,
    )
    print(url)
    url = getIndicatorQueryUrl(
        dataset_id,
        False,
        False,
        latitude=latitude,
        longitude=longitude,
        timeMin=time_start,
        timeMax=time_finish,
        range=range_value,
        format="json",
    )
    # https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/indicators_wsdi_aba0_0062_8939.csv?time%2Clatitude%2Clongitude%2Cwsdi&time%3E=2021-07-01&time%3C=2050-07-01&latitude%3E=39.688777923584&latitude%3C=41.22824901518532&longitude%3E=14.740385055542&longitude%3C=15.183105468750002
    r = requests.get(url=url)
    # csvfile = csv.DictReader(io.TextIOWrapper(url_open, encoding = 'utf-8'), delimiter=',')
    data = r.json()
    return data


def getDataTable(
    dataset_id,
    layer_name,
    time_start,
    time_finish,
    latitude,
    longitude,
    num_parameters,
    range_value,
):
    try:
        # vedere se si tratta di un poligono e nel caso prendere tutti i punti che stanno nel poligono e per ogni punto chiamare questa funzione e costruire il json?

        url = getIndicatorQueryUrl(
            dataset_id,
            False,
            False,
            latitude=str(latitude),
            longitude=str(longitude),
            timeMin=str(time_start),
            timeMax=str(time_finish),
            range=str(range_value),
            format="json",
            variable=str(layer_name),
        )
        print("URL SUPER FUNZIONE =", url)
        # urlTabledap = https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/arpav_PRCPTOT_yearly.htmlTable?time%2Clatitude%2Clongitude%2CIndicator&time%3E=2021-12-25&time%3C=2022-01-01

        # if num_parameters > 3:
        #   url= ERDDAP_URL + "/griddap/"+dataset_id+".json?"+layer_name+"%5B("+str(time_start)+"):1:("+str(time_finish)+")%5D%5B("+str(range_value)+"):1:("+str(range_value)+")%5D%5B("+str(latitude)+"):1:("+str(latitude)+")%5D%5B("+str(longitude)+"):1:("+str(longitude)+")%5D"
        # else:
        #   url = ERDDAP_URL + "/griddap/"+dataset_id+".json?"+layer_name+"%5B("+str(time_start)+"):1:("+str(time_finish)+")%5D%5B("+str(latitude)+"):1:("+str(latitude)+")%5D%5B("+str(longitude)+"):1:("+str(longitude)+")%5D"

        # https://erddap-dev.cmcc-opa.eu/erddap/griddap/atm_regional_1f91_1673_845b.htmlTable?vegetfrac%5B(1969-12-30):1:(2005-11-20T00:00:00Z)%5D%5B(13):1:(13.0)%5D%5B(-90):1:(-90.0)%5D%5B(180.45724):1:(180.4572)%5D
        r = requests.get(url=url)

        # csvfile = csv.DictReader(io.TextIOWrapper(url_open, encoding = 'utf-8'), delimiter=',')
        data = r.json()
        return data

    except Exception as e:
        print("EXEPTION =", e)
        return "fuoriWms"


def getDataGraphicGeneric(
    dataset_id,
    layer_name,
    time_start,
    time_finish,
    latitude,
    longitude,
    num_parameters,
    range_value,
    is_indicator,
    lat_start,
    long_start,
    lat_end,
    long_end,
    **kwargs
):
    try:
        onlyone = 0
        cache = 0
        if "context" in kwargs and kwargs["context"] == "one":
            onlyone = 1
        if "cache" in kwargs and kwargs["cache"] == "yes":
            cache = 1
        onlylat = None
        onlylong = None
        operation = None

        if "operation" in kwargs and kwargs["operation"] != "":
            operation = kwargs["operation"]

        if lat_start == "no":
            lat_start = latitude
        if lat_end == "no":
            lat_end = latitude
        if long_start == "no":
            long_start = longitude
        if long_end == "no":
            long_end = longitude

        url = getIndicatorQueryUrl(
            dataset_id,
            False,
            False,
            latitude=latitude,
            longitude=longitude,
            latitudeMin=lat_start,
            latitudeMax=lat_end,
            longitudeMin=long_start,
            longitudeMax=long_end,
            range=range_value,
            variable=layer_name,
            format="csv",
            timeMin=time_start,
            timeMax=time_finish,
        )
        if cache == 1:
            url = download_with_cache_as_csv(url)
        if url == "fuoriWms":
            return url
        try:
            df = pd.read_csv(url, dtype="unicode")
        except Exception as e:
            return "fuoriWms"
        if df[layer_name] is not None:
            unit = df[layer_name][0]
        else:
            unit = layer_name
        unit = ""
        df = df.iloc[1:, :]
        n_values = len(df)
        allData = []
        values = []
        dates = []
        layerName = []
        lats = []
        longs = []
        i = 0
        if n_values <= x:  # all the data
            for index, row in df.iterrows():
                if onlyone == 1 and onlylat is None:
                    onlylat = row["latitude"]
                    onlylong = row["longitude"]
                if (
                    row[layer_name] == row[layer_name]
                    and row[layer_name] != "NaN"
                    and (
                        onlyone == 0
                        or (onlylat == row["latitude"] and onlylong == row["longitude"])
                    )
                ):
                    lats.insert(i, row["latitude"])
                    longs.insert(i, row["longitude"])
                    layerName.insert(i, layer_name)
                    values.insert(i, float(row[layer_name]))
                    dates.insert(i, row["time"])
                    i += 1
        else:  # one every nvalues/x data
            every_nth_rows = int(n_values / x)
            df = df[::every_nth_rows]
            for index, row in df.iterrows():
                if (
                    row[layer_name] == row[layer_name]
                    and row[layer_name] != "NaN"
                    and (
                        onlyone == 0
                        or (onlylat == row["latitude"] and onlylong == row["longitude"])
                    )
                ):
                    lats.insert(i, row["latitude"])
                    longs.insert(i, row["longitude"])
                    layerName.insert(i, layer_name)
                    values.insert(i, float(row[layer_name]))
                    dates.insert(i, row["time"])
                    i += 1

        allData = [values, dates, unit, layerName, lats, longs]
        if operation is None:
            return allData
        else:
            output = None
            if "output" in kwargs:
                output = kwargs["output"]

            return packageGraphData(
                processOperation(operation, values, dates, unit, layerName, lats, longs),
                output=output,
            )
    except Exception as e:
        return "fuoriWms"

def calculate_trend(dates, values):
    try:
        y = np.array(values)
        # print("dates inside calculate_trend==============",dates)
        print(type(dates[0]))
        # converti le date in oggetti datetime
        if type(dates[0]) is str:
            if dates[0].startswith("0000"):
                #annual month by month
                dates = [dt.datetime.strptime(d.replace('0000',"2000"), "%Y-%m-%dT%H:%M:%SZ") for d in dates]
            elif len(dates[0].split("-")) == 2: #01-01 1 gennaio 2000-01-01
                 #annual day by day
                 dates = [dt.datetime.strptime("2000-" + d, "%Y-%d-%m") for d in dates]
            else:
            #è una stringa!
                dates = [dt.datetime.strptime(d, "%Y-%m-%dT%H:%M:%SZ") for d in dates]
       
        days = np.array([d.timestamp() for d in dates])
        # print("Days",days)
        # esegue la regressione lineare
        slope, intercept, r_value, p_value, std_err = stats.linregress(days,y)
        # model = LinearRegression().fit(seconds_norm.reshape(-1, 1), y)
        # # coefficiente angolare
        # coef_angular = model.coef_[0]
        return slope * 86400 * 365.25
    except Exception as e:
        print("Errore in calculate_trend",e)
        return str(e)

def updateStatistics(new_dates,new_values):
    try:
        allData = {}
        #print("new_values=============",new_values)
        if type(new_values[0]) is not dict:
            allData["mean"] = mean(new_values)
            allData["stdev"] = stdev(new_values)
            allData["median"] = median(new_values)
            allData["trend"] = calculate_trend(new_dates,new_values)
        else:
            #is a polygon so we need to calculate mean, stdev, median and trend
            #print("new_values=====",new_values)
            df_stats = pd.DataFrame(new_values,columns = ["date","value"])
            #print("df_stats=====",df_stats)
            allData["mean"] = mean(df_stats["value"].tolist())
            allData["stdev"] = stdev(df_stats["value"].tolist())
            allData["median"] = median(df_stats["value"].tolist())
            mean_trend = df_stats.groupby("date")["value"].mean().tolist()
            df_stats = df_stats.drop_duplicates(subset=["date"], keep="first") 
            #print("Df_stat after drop_duplicates",df_stats)
            df_stats["date"] = pd.to_datetime(df_stats["date"])
            allData["trend"] = calculate_trend(df_stats["date"].tolist(),mean_trend)

        return allData
    except Exception as e:
        print("Errore in update",e)
        return str(e)


def packageGraphData(allData, **kwargs):
    values = allData[0]
    mean_result = mean(values)
    median_result = median(values)
    stdev_result = stdev(values)
    trend_result = calculate_trend(allData[1],values)
    print("package graph data=======trend result",trend_result)
    dates = allData[1]
    unit = allData[2]
    layerName = allData[3]
    lats = allData[4]
    longs = allData[5]
    data = {}
    data["unit"] = unit
    data["mean"] = mean_result
    data["median"] = median_result
    data["stdev"] = stdev_result
    data["trend_yr"] = trend_result
    data["entries"] = []

    if "output" in kwargs:
        if kwargs["output"] == "csv":
            out = "Date,Dataset,Latitude,Longitude,Value\n"
            for n in range(len(values)):
                out = (
                    out
                    + dates[n]
                    + ","
                    + layerName[n]
                    + ","
                    + str(lats[n])
                    + ","
                    + str(longs[n])
                    + ","
                    + str(values[n])
                    + "\n"
                )
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
        entry["x"] = dates[n]
        entry["y"] = values[n]
        dictValue.append(entry)
    return data


def processOperation(operation, values, dates, unit, layerName, lats, longs):
    if operation == "default":
        return [values, dates, unit, layerName, lats, longs]
    values2 = []
    
    dates_trend = dates.copy()
    mean_result = mean(values)
    median_result = median(values)
    stdev_result = stdev(values)
    trend_result = calculate_trend(dates_trend,values)
    dates2 = []
    layerName2 = []
    lats2 = []
    longs2 = []
    i = 0
    vals = []
    lastDate = None

    pattern = None

    if operation == "annualMonth":
        pattern = re.compile("\d\d\d\d-(\d\d)-\S*")
        months = [
            "01",
            "02",
            "03",
            "04",
            "05",
            "06",
            "07",
            "08",
            "09",
            "10",
            "11",
            "12",
        ]
        for mon in months:
            dat = "0000-" + mon + "-01T00:00:00Z"
            vals = []
            for n in range(len(values)):
                if pattern.match(dates[n]).group(1) != mon:
                    continue
                vals.append(values[n])

            if len(vals) > 0:
                dates2.insert(i, dat)
                lats2.insert(i, 0)
                longs2.insert(i, 0)
                layerName2.insert(i, layerName[0])
                values2.insert(i, aggregateGraphicValues("avg", vals))

            vals = []

        return [
            values2,
            dates2,
            unit,
            layerName2,
            lats2,
            longs2,
            mean_result,
            median_result,
            stdev_result,
            trend_result,
        ]

    if operation == "annualDay":
        try:
            # operation is annual cycle but day by day
            # I need to take that particular day for every year!!
            # print("Ci entrooooooooooooooooooooooooo")
            dates_list = [
                dt.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").date()
                for date in dates
            ]
            # print("DATES_LIST======",dates_list)
            lats2 = [0 for value in values]
            longs2 = [0 for value in values]
            layerName2 = [layerName[0] for value in values]
            # in values ci sono tutti i valori, dates_list tutte le date!
            float_values = [float(value) for value in values]
            df = pd.DataFrame({"datetime": dates_list, "value": float_values})
            df["datetime"] = pd.to_datetime(df["datetime"])
            # Replace February 29th with February 28th
            df["datetime"] = df["datetime"].apply(
                lambda x: x.replace(day=28) if x.month == 2 and x.day == 29 else x
            )
            df["day_month"] = df["datetime"]
            df["day_month"] = df["day_month"].apply(lambda x: x.replace(year=2000))
            df = df.sort_values(by=["day_month"])
            grouped = df.groupby("day_month")["value"].mean()
            df["day_month"] = df["day_month"].apply(lambda x: x.strftime("%d-%m"))
            removeDuplicates = df.drop_duplicates(subset=["day_month"])
            return [
                grouped.values,
                list(removeDuplicates["day_month"]),
                unit,
                layerName2,
                lats2,
                longs2,
                mean_result,
                median_result,
                stdev_result,
                trend_result,
            ]
        except Exception as e:
            print("EXCEPTION =", e)

    for n in range(len(values)):
        if lastDate is None:
            lastDate = dates[n]

        elif lastDate != dates[n]:
            dates2.insert(i, lastDate)
            lats2.insert(i, 0)
            longs2.insert(i, 0)
            layerName2.insert(i, layerName[0])
            values2.insert(i, aggregateGraphicValues(operation, vals))
            i += 1
            lastDate = dates[n]
            vals = []

        vals.append(values[n])
    if lastDate is not None:
        dates2.insert(i, lastDate)
        lats2.insert(i, 0)
        longs2.insert(i, 0)
        layerName2.insert(i, layerName[0])
        values2.insert(i, aggregateGraphicValues(operation, vals))
        i += 1

    return [values2, dates2, unit, layerName2, lats2, longs2]


def aggregateGraphicValues(operation, vals):
    if vals is None:
        return None

    if operation == "median":
        vals.sort()
        return vals[int(len(vals) / 2)]
    elif operation == "percentile_10":
        vals.sort()
        return vals[int(len(vals) * 0.1)]
    elif operation == "percentile_90":
        vals.sort()
        return vals[int(len(vals) * 0.9)]

    out = None
    for x in vals:
        x = float(x)
        if operation == "max":
            if out is None or x > out:
                out = x
        elif operation == "min":
            if out is None or x < out:
                out = x
        elif operation == "avg":
            if out is None:
                out = x
            else:
                out += x

    if operation == "avg":
        out = out / len(vals)
    return out


def getDataGraphic(
    dataset_id,
    layer_name,
    time_start,
    time_finish,
    latitude1,
    longitude1,
    num_parameters,
    range_value,
    is_indicator,
    lat_start,
    long_start,
    lat_end,
    long_end,
):
    graphic1 = getDataGraphicGeneric(
        dataset_id,
        layer_name,
        time_start,
        time_finish,
        latitude1,
        longitude1,
        num_parameters,
        range_value,
        is_indicator,
        lat_start,
        long_start,
        lat_end,
        long_end,
    )
    return graphic1


def getMaxMinMeanMomentGraphicGeneric(
    dataset_id,
    layer_name,
    time_start,
    time_finish,
    latitude,
    longitude,
    num_parameters,
    range_value,
    is_indicator,
    lat_start,
    long_start,
    lat_end,
    long_end,
):
    result = getDataGraphicGeneric(
        dataset_id,
        layer_name,
        time_start,
        time_finish,
        latitude,
        longitude,
        num_parameters,
        range_value,
        is_indicator,
        lat_start,
        long_start,
        lat_end,
        long_end,
    )

    if is_indicator == "false":
        url = url_is_indicator(
            is_indicator,
            True,
            False,
            dataset_id=dataset_id,
            layer_name=layer_name,
            time_start=time_start,
            time_finish=time_finish,
            latitude=latitude,
            longitude=longitude,
            num_parameters=num_parameters,
            range_value=range_value,
        )
    else:
        url = url_is_indicator(
            "true",
            True,
            False,
            dataset_id=dataset_id,
            layer_name=layer_name,
            time_start=time_start,
            time_finish=time_finish,
            latMin=lat_start,
            longMin=long_start,
            latMax=lat_end,
            longMax=long_end,
            num_parameters=num_parameters,
            range_value=range_value,
        )
    df = pd.read_csv(url, dtype="unicode")
    unit = df[layer_name][0]
    df = df.iloc[1:, :]
    df_length = len(df)
    all_date = []
    all_values = []
    allData = []
    if df_length <= x:
        # take every value
        all_date = df["time"].to_numpy()
        all_values = df[layer_name].astype(float).to_numpy()
    else:
        every_nth_rows = int(df_length / x)
        df = df[::every_nth_rows]
        all_date = df["time"].to_numpy()
        all_values = df[layer_name].astype(float).to_numpy()

    allData = [all_date.tolist(), all_values.tolist(), layer_name, unit]
    return allData


def getMaxMinMomentIndicatorGraphic(
    max_min_mean,
    dataset_id,
    layer_name,
    time_start,
    time_finish,
    latitude1,
    longitude1,
    latitude2,
    longitude2,
    latitude3,
    longitude3,
    num_parameters,
    range_value,
    is_indicator,
    lat_start,
    long_start,
    lat_end,
    long_end,
):
    url = url_is_indicator(
        "true",
        True,
        False,
        dataset_id=dataset_id,
        layer_name=layer_name,
        time_start=time_start,
        time_finish=time_finish,
        latMin=lat_start,
        longMin=long_start,
        latMax=lat_end,
        longMax=long_end,
        num_parameters=num_parameters,
        range_value=range_value,
    )

    df = pd.read_csv(url, dtype="unicode")
    df = df.iloc[1:, :]
    df[layer_name] = pd.to_numeric(df[layer_name], downcast="float")
    df["time"] = pd.to_datetime(df["time"].astype("str"))
    # find the max or min or the mean for every possible date! this needs to be changed!
    df[layer_name] = df.groupby("time")[layer_name].transform(max_min_mean)

    df.drop_duplicates(subset=["time"], inplace=True)
    df_length = len(df)
    all_date = []
    all_values = []
    allData = []
    if df_length <= x:
        # take every value
        all_date = df["time"].to_numpy()
        all_values = df[layer_name].astype(float).to_numpy()
    else:
        every_nth_rows = int(df_length / x)
        df = df[::every_nth_rows]
        all_date = df["time"].to_numpy()
        all_values = df[layer_name].astype(float).to_numpy()

    allData = [all_date.tolist(), all_values.tolist(), layer_name]
    return allData


def getMaxMomentGraphic(
    dataset_id,
    layer_name,
    time_start,
    time_finish,
    latitude1,
    longitude1,
    latitude2,
    longitude2,
    latitude3,
    longitude3,
    num_parameters,
    range_value,
    is_indicator,
    lat_start,
    long_start,
    lat_end,
    long_end,
):
    # now since the indicators' data are few, we take all the data of every possible points and find the maximum of every moment
    # this needs to be changed once the indicators have more data
    if is_indicator == "true":
        # take every possible data and find the maximum moment by moment!!!!!!!
        return getMaxMinMomentIndicatorGraphic(
            "max",
            dataset_id,
            layer_name,
            time_start,
            time_finish,
            latitude1,
            longitude1,
            latitude2,
            longitude2,
            latitude3,
            longitude3,
            num_parameters,
            range_value,
            is_indicator,
            lat_start,
            long_start,
            lat_end,
            long_end,
        )

    else:
        allData1 = getMaxMinMeanMomentGraphicGeneric(
            dataset_id,
            layer_name,
            time_start,
            time_finish,
            latitude1,
            longitude1,
            num_parameters,
            range_value,
            is_indicator,
            lat_start,
            long_start,
            lat_end,
            long_end,
        )
        allData2 = getMaxMinMeanMomentGraphicGeneric(
            dataset_id,
            layer_name,
            time_start,
            time_finish,
            latitude2,
            longitude2,
            num_parameters,
            range_value,
            is_indicator,
            lat_start,
            long_start,
            lat_end,
            long_end,
        )
        allData3 = getMaxMinMeanMomentGraphicGeneric(
            dataset_id,
            layer_name,
            time_start,
            time_finish,
            latitude3,
            longitude3,
            num_parameters,
            range_value,
            is_indicator,
            lat_start,
            long_start,
            lat_end,
            long_end,
        )
        maximum_value = np.maximum(allData1[1], allData2[1])
        maximum_value1 = np.maximum(maximum_value, allData3[1])
        allData = [
            allData1[0],
            maximum_value1.tolist(),
            allData1[len(allData1) - 2],
            allData1[len(allData1) - 1],
        ]
        return allData


def getMinMomentGraphic(
    dataset_id,
    layer_name,
    time_start,
    time_finish,
    latitude1,
    longitude1,
    latitude2,
    longitude2,
    latitude3,
    longitude3,
    num_parameters,
    range_value,
    is_indicator,
    lat_start,
    long_start,
    lat_end,
    long_end,
):
    if is_indicator == "true":
        # take every possible data and find the minimum moment by moment!!!!!!!
        return getMaxMinMomentIndicatorGraphic(
            "min",
            dataset_id,
            layer_name,
            time_start,
            time_finish,
            latitude1,
            longitude1,
            latitude2,
            longitude2,
            latitude3,
            longitude3,
            num_parameters,
            range_value,
            is_indicator,
            lat_start,
            long_start,
            lat_end,
            long_end,
        )

    else:
        allData1 = getMaxMinMeanMomentGraphicGeneric(
            dataset_id,
            layer_name,
            time_start,
            time_finish,
            latitude1,
            longitude1,
            num_parameters,
            range_value,
            is_indicator,
            lat_start,
            long_start,
            lat_end,
            long_end,
        )
        allData2 = getMaxMinMeanMomentGraphicGeneric(
            dataset_id,
            layer_name,
            time_start,
            time_finish,
            latitude2,
            longitude2,
            num_parameters,
            range_value,
            is_indicator,
            lat_start,
            long_start,
            lat_end,
            long_end,
        )
        allData3 = getMaxMinMeanMomentGraphicGeneric(
            dataset_id,
            layer_name,
            time_start,
            time_finish,
            latitude3,
            longitude3,
            num_parameters,
            range_value,
            is_indicator,
            lat_start,
            long_start,
            lat_end,
            long_end,
        )
        minimum_value = np.minimum(allData1[1], allData2[1])
        minimum_value1 = np.minimum(minimum_value, allData3[1])
        allData = [
            allData1[0],
            minimum_value1.tolist(),
            allData1[len(allData1) - 2],
            allData1[len(allData1) - 1],
        ]
        return allData


def getMeanMomentGraphic(
    dataset_id,
    layer_name,
    time_start,
    time_finish,
    latitude1,
    longitude1,
    latitude2,
    longitude2,
    latitude3,
    longitude3,
    num_parameters,
    range_value,
    is_indicator,
    lat_start,
    long_start,
    lat_end,
    long_end,
):
    if is_indicator == "true":
        # take every possible data and find the minimum moment by moment!!!!!!!
        return getMaxMinMomentIndicatorGraphic(
            "mean",
            dataset_id,
            layer_name,
            time_start,
            time_finish,
            latitude1,
            longitude1,
            latitude2,
            longitude2,
            latitude3,
            longitude3,
            num_parameters,
            range_value,
            is_indicator,
            lat_start,
            long_start,
            lat_end,
            long_end,
        )

    else:
        allData1 = getMaxMinMeanMomentGraphicGeneric(
            dataset_id,
            layer_name,
            time_start,
            time_finish,
            latitude1,
            longitude1,
            num_parameters,
            range_value,
            is_indicator,
            lat_start,
            long_start,
            lat_end,
            long_end,
        )
        allData2 = getMaxMinMeanMomentGraphicGeneric(
            dataset_id,
            layer_name,
            time_start,
            time_finish,
            latitude2,
            longitude2,
            num_parameters,
            range_value,
            is_indicator,
            lat_start,
            long_start,
            lat_end,
            long_end,
        )
        allData3 = getMaxMinMeanMomentGraphicGeneric(
            dataset_id,
            layer_name,
            time_start,
            time_finish,
            latitude3,
            longitude3,
            num_parameters,
            range_value,
            is_indicator,
            lat_start,
            long_start,
            lat_end,
            long_end,
        )
        all_arrays = [allData1[1], allData2[1], allData3[1]]
        average_array = np.array(all_arrays, dtype=float).mean(axis=0)
        allData = [
            allData1[0],
            average_array.tolist(),
            allData1[len(allData1) - 2],
            allData1[len(allData1) - 1],
        ]
        return allData


def getDataGraphicPolygon(
    dataset_id,
    layer_name,
    time_start,
    time_finish,
    latMin,
    longMin,
    latMax,
    longMax,
    num_parameters,
    range_value,
    is_indicator,
):
    url = url_is_indicator(
        is_indicator,
        True,
        True,
        dataset_id=dataset_id,
        layer_name=layer_name,
        time_start=time_start,
        time_finish=time_finish,
        latMin=latMin,
        longMin=longMin,
        latMax=latMax,
        longMax=longMax,
        num_parameters=num_parameters,
        range_value=range_value,
    )
    df = pd.read_csv(url, dtype="unicode")
    unit = df[layer_name][0]
    df = df.iloc[1:, :]
    n_values = len(df)
    allData = []
    values = []
    dates = []
    coordinates = []
    layerName = []
    i = 0
    if n_values <= x:  # all the data
        for index, row in df.iterrows():
            layerName.insert(i, layer_name)
            try:
                coordinates.insert(
                    i, np.array([float(row["latitude"]), float(row["longitude"])])
                )
            except ValueError:
                print("Not a float!")
            values.insert(i, row[layer_name])
            dates.insert(i, row["time"])
            i += 1
    else:  # one every nvalues/x data
        every_nth_rows = int(n_values / x)
        df = df[::every_nth_rows]
        for index, row in df.iterrows():
            layerName.insert(i, layer_name)
            try:
                coordinates.insert(i, [float(row["latitude"]), float(row["longitude"])])
            except ValueError:
                print("Not a float!")
            values.insert(i, row[layer_name])
            dates.insert(i, row["time"])
            i += 1

    allData = [values, coordinates, dates, unit, layerName]
    return allData


def getDataGraphicIndicatorAnnualMean(
    all_points, all_dates, unit, layer_name, latitude_value, longitude_value
):
    # first we create the dataframe from all the lists
    df = pd.DataFrame(list(zip(all_points, all_dates)), columns=[layer_name, "time"])
    df = df.assign(latitude=latitude_value)
    df = df.assign(longitude=longitude_value)
    df[layer_name] = pd.to_numeric(df[layer_name], downcast="float")
    df["time"] = pd.to_datetime(df["time"].astype("str"))
    df = df.groupby([(df.time.dt.day), (df.time.dt.month), df.latitude, df.longitude])[
        layer_name
    ].mean()
    return df.to_json()


def getDataGraphicAnnualGeneric(
    dataset_id,
    layer_name,
    time_start,
    time_finish,
    latitude1,
    longitude1,
    num_parameters,
    range_value,
    is_indicator,
    lat_start,
    long_start,
    lat_end,
    long_end,
):
    url = url_is_indicator(
        is_indicator,
        True,
        False,
        dataset_id=dataset_id,
        layer_name=layer_name,
        time_start=time_start,
        time_finish=time_finish,
        latitude=latitude1,
        longitude=longitude1,
        num_parameters=num_parameters,
        range_value=range_value,
    )
    print(url)
    df = pd.read_csv(url, dtype="unicode")
    unit = df[layer_name][0]
    df = df.iloc[1:, :]
    df[layer_name] = pd.to_numeric(df[layer_name], downcast="float")
    df["time"] = pd.to_datetime(df["time"].astype("str"))
    df["unit"] = unit
    df = df.groupby([(df.time.dt.day), (df.time.dt.month), (df.unit)])[
        layer_name
    ].mean()
    return df.to_json()


def getDataGraphicAnnualMean(
    dataset_id,
    layer_name,
    time_start,
    time_finish,
    latitude1,
    longitude1,
    latitude2,
    longitude2,
    latitude3,
    longitude3,
    num_parameters,
    range_value,
    is_indicator,
    lat_start,
    long_start,
    lat_end,
    long_end,
):
    graphic1 = getDataGraphicAnnualGeneric(
        dataset_id,
        layer_name,
        time_start,
        time_finish,
        latitude1,
        longitude1,
        num_parameters,
        range_value,
        is_indicator,
        lat_start,
        long_start,
        lat_end,
        long_end,
    )
    graphic2 = getDataGraphicAnnualGeneric(
        dataset_id,
        layer_name,
        time_start,
        time_finish,
        latitude2,
        longitude2,
        num_parameters,
        range_value,
        is_indicator,
        lat_start,
        long_start,
        lat_end,
        long_end,
    )
    graphic3 = getDataGraphicAnnualGeneric(
        dataset_id,
        layer_name,
        time_start,
        time_finish,
        latitude3,
        longitude3,
        num_parameters,
        range_value,
        is_indicator,
        lat_start,
        long_start,
        lat_end,
        long_end,
    )
    allData = [graphic1, graphic2, graphic3]
    return allData


def getDataAnnualPolygon(
    dataset_id,
    layer_name,
    time_start,
    time_finish,
    latMin,
    longMin,
    latMax,
    longMax,
    num_parameters,
    range_value,
    is_indicator,
):
    url = url_is_indicator(
        is_indicator,
        True,
        True,
        dataset_id=dataset_id,
        layer_name=layer_name,
        time_start=time_start,
        time_finish=time_finish,
        latMin=latMin,
        longMin=longMin,
        latMax=latMax,
        longMax=longMax,
        num_parameters=num_parameters,
        range_value=range_value,
    )
    df = pd.read_csv(url, dtype="unicode")
    unit = df[layer_name][0]
    df = df.iloc[1:, :]
    n_values = len(df)
    if n_values > x:
        every_nth_rows = int(n_values / x)
        df = df[::every_nth_rows]
        df[layer_name] = pd.to_numeric(df[layer_name], downcast="float")
        df["time"] = pd.to_datetime(df["time"].astype("str"))
        df["unit"] = unit
        df = df.groupby(
            [
                (df.time.dt.day),
                (df.time.dt.month),
                (df["latitude"]),
                (df["longitude"]),
                (df.unit),
            ]
        )[layer_name].mean()
        return df.to_json()

    else:
        df[layer_name] = pd.to_numeric(df[layer_name], downcast="float")
        df["time"] = pd.to_datetime(df["time"].astype("str"))
        df["unit"] = unit
        df = df.groupby(
            [
                (df.time.dt.day),
                (df.time.dt.month),
                (df["latitude"]),
                (df["longitude"]),
                (df.unit),
            ]
        )[layer_name].mean()
        return df.to_json()


# AdriaClim Indicators | adriaclim_WRF | yearly | hist | r95p
# tempo 4709 secondi circa


def download_big_data(timeperiod):
    start_effettivo = time.time()
    all_datasets = Node.objects.filter(Q(adriaclim_dataset="indicator") & Q(adriaclim_timeperiod=timeperiod))
    for dataset in all_datasets:
        start_time = time.time()
        print("Sono iniziata ora final version!!!")
        url_csv = ""
        if dataset.griddap_url != "":
            # https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/MedCordex_IPSL_bda7_23d0_0f98.csv?consecutive_summer_days_index_per_time_period%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,number_of_csu_periods_with_more_than_5days_per_time_period%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,fg%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,heat_wave_duration_index_wrt_mean_of_reference_period%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,heat_waves_per_time_period%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,summer_days_index_per_time_period%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,tg%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,tropical_nights_index_per_time_period%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,txn%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,txx%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D
            # https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/WAVES_VTM10_5da8_8ef6_cf64
            url_csv += dataset.griddap_url + ".csv?"
            variable_names = dataset.variable_names.split(" ")
            for index, var in enumerate(variable_names):
                if dataset.dimensions > 3:
                    if index < len(variable_names) - 1:
                        # https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/atm_regional_1f91_1673_845b.htmlTable?vegetfrac%5B(2005-11-20T00:00:00Z):1:(2005-11-20T00:00:00Z)%5D%5B(1.0):1:(13.0)%5D%5B(90.0):1:(-90.0)%5D%5B(-171.2326):1:(180.4572)%5D
                        url_csv += (
                            var
                            + "%5B("
                            + dataset.time_start
                            + "):1:("
                            + dataset.time_end
                            + ")%5D%5B("
                            + str(dataset.param_min)
                            + "):1:("
                            + str(dataset.param_max)
                            + ")%5D%5B("
                            + dataset.lat_max
                            + "):1:("
                            + dataset.lat_min
                            + ")%5D%5B("
                            + dataset.lng_min
                            + "):1:("
                            + dataset.lng_max
                            + ")%5D,"
                        )
                    else:
                        url_csv += (
                            var
                            + "%5B("
                            + dataset.time_start
                            + "):1:("
                            + dataset.time_end
                            + ")%5D%5B("
                            + str(dataset.param_min)
                            + "):1:("
                            + str(dataset.param_max)
                            + ")%5D%5B("
                            + dataset.lat_max
                            + "):1:("
                            + dataset.lat_min
                            + ")%5D%5B("
                            + dataset.lng_min
                            + "):1:("
                            + dataset.lng_max
                            + ")%5D"
                        )

                else:
                    #niente param aggiuntivo
                    if index < len(variable_names) - 1:
                        url_csv += (
                            var
                            + "%5B("
                            + dataset.time_start
                            + "):1:("
                            + dataset.time_end
                            + ")%5D%5B("
                            + dataset.lat_max
                            + "):1:("
                            + dataset.lat_min
                            + ")%5D%5B("
                            + dataset.lng_min
                            + "):1:("
                            + dataset.lng_max
                            + ")%5D,"
                        )
                    else:
                        url_csv += (
                            var
                            + "%5B("
                            + dataset.time_start
                            + "):1:("
                            + dataset.time_end
                            + ")%5D%5B("
                            + dataset.lat_max
                            + "):1:("
                            + dataset.lat_min
                            + ")%5D%5B("
                            + dataset.lng_min
                            + "):1:("
                            + dataset.lng_max
                            + ")%5D"
                        )


            print("url_csv=======", url_csv)
            generic_big_data_download(url_csv,dataset,dataset.variables,False)

        else:
            #siamo nel caso di tabledap!
            url_csv += dataset.tabledap_url + ".csv?"
            variable_names = dataset.variable_names.split(" ")
            for index, var in enumerate(variable_names):
                if index < len(variable_names) - 1:
                    url_csv += var + "%2C"
                else:
                    url_csv += var + "&"

            url_csv += (
                "time%3E="
                + dataset.time_start
                + "&time%3C="
                + dataset.time_end
                + "&latitude%3E="
                + dataset.lat_min
                + "&latitude%3C="
                + dataset.lat_max
                + "&longitude%3E="
                + dataset.lng_min
                + "&longitude%3C="
                + dataset.lng_max
            )
            print("url_csv=======", url_csv)
            generic_big_data_download(url_csv,dataset,dataset.variables,True)
            
        print("TIME FOR A DATASET {:.2f} seconds".format(time.time() - start_time))

    print("TIME FOR DOWNLOAD BIG DATA {:.2f} seconds".format(time.time() - start_effettivo))

def generic_big_data_download(url_dataset,dataset,num_variables,is_tabledap):
    deletePoly("Polygon",id=dataset)
    if is_tabledap:
        dtypes = {'date_value': 'string', 'latitude': 'float32', 'longitude': 'float32'}
        names = ['date_value', 'latitude', 'longitude']
        chunksize = 10**6
        variable_names = dataset.variable_names.split(" ")
        if dataset.variables > 3:
            for index,name in enumerate(variable_names):
                if name != "time" and name != "latitude" and name != "longitude":
                    dtypes["value_"+str(index)] = 'float32'
                    names.append("value_" + str(index))
        
        list_keys = names.copy()
        list_keys.append("dataset_id")
        list_keys.append("coordinate")

        for chunk in pd.read_table(
            url_dataset,
            engine="c",
            sep=",",
            header=0,
            chunksize=chunksize,
            low_memory=False,
            names=names
        ):
        

            chunk.drop(index=chunk.index[0], axis=0, inplace=True)
            chunk = chunk.astype(dtypes)
            chunk["dataset_id"] = dataset.id
            chunk_geo = gpd.GeoDataFrame(chunk, geometry=gpd.points_from_xy(chunk.latitude, chunk.longitude), crs="EPSG:4326")
            chunk_geo['coordinate'] = chunk_geo['geometry'].apply(lambda p: Point(p.y,p.x,srid=4326))
            # chunk_geo = chunk_geo.rename(columns={'geometry':'coordinate'})
            chunk_geo = chunk_geo.drop(columns=['geometry'])
            chunk_geo["coordinate"] = chunk_geo["coordinate"].apply(lambda p: p.wkt)

            csv_data = chunk_geo.to_csv(index=False)
            csv_file = io.StringIO(csv_data)

                        
            mapping = {
                name: name.lower()
                for name in list_keys
            }

            try:

                Polygon.copy_manager.from_csv(
                    csv_file,
                    mapping,
                
                )
                

            except Exception as e:
                print("Eccezione", e)
                return str(e)
    else:
        #siamo nel caso di griddap
        dtypes = {'date_value': 'string', 'latitude': 'float32', 'longitude': 'float32'}
        names = ['date_value', 'latitude', 'longitude']
        
        dimensions = dataset.dimension_names.split(" ")
        if dataset.dimensions > 3:
            for name in dimensions:
                if name != "time" and name != "latitude" and name != "longitude":
                    dtypes[name] = 'float32'
                    names.append(name)
        
        for i in range(0,num_variables):
            dtypes["value_" + str(i)] = 'float32'
            names.append("value_" + str(i))
        
        list_keys = names.copy()
        list_keys.append("dataset_id") 
        list_keys.append("coordinate")

        chunksize = 10**6
        for chunk in pd.read_table(
            url_dataset,
            engine="c",
            sep=",",
            header=0,
            chunksize=chunksize,
            low_memory=False,
            names=names
        ):

            chunk.drop(index=chunk.index[0], axis=0, inplace=True)
            chunk = chunk.astype(dtypes)
            chunk["dataset_id"] = dataset.id 
            chunk_geo = gpd.GeoDataFrame(chunk, geometry=gpd.points_from_xy(chunk.latitude, chunk.longitude), crs="EPSG:4326")
            chunk_geo['coordinate'] = chunk_geo['geometry'].apply(lambda p: Point(p.y,p.x,srid=4326))
            # chunk_geo = chunk_geo.rename(columns={'geometry':'coordinate'})
            chunk_geo = chunk_geo.drop(columns=['geometry'])
            chunk_geo["coordinate"] = chunk_geo["coordinate"].apply(lambda p: p.wkt)
            csv_data = chunk_geo.to_csv(index=False)
            csv_file = io.StringIO(csv_data)
            

            mapping = {
                name: name.lower()
                for name in list_keys
            }

            try:

                Polygon.copy_manager.from_csv(
                    csv_file,
                    mapping,
                )
                
            except Exception as e:
                print("Eccezione", e)
                return str(e)


def rompo_tutto():
    #con questo nuovo, con 161k ha impiegato secondi
    # AdriaClim Indicators | MedCordex_IPSL | yearly | hist | txx

    # tempo 55 secondi circa
    #
    # AdriaClim Indicators | MedCordex_IPSL | seasonal | hist | csu ======> 161k
    # tempo 338 secondi circa
    # url_r95p_yearly = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/MedCordex_IPSL_ad60_605d_97a5.csv?txx%5B(1970-06-15T12:00:00Z):1:(2005-06-06T12:00:00Z)%5D%5B(46.888783):1:(37.288776)%5D%5B(10.24039):1:(21.663462)%5D"
    # url_micidiale = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/MedCordex_IPSL_c22c_bffc_1baa.csv?consecutive_summer_days_index_per_time_period%5B(1970-01-01):1:(2005-10-01T00:00:00Z)%5D%5B(46.888783):1:(37.288776)%5D%5B(10.240385):1:(21.663462)%5D"
    # url_r95p_monthly = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/adriaclim_WRF_c3bc_3ecd_2f3c.csv?very_wet_days_wrt_95th_percentile_of_reference_period%5B(1992-01-01):1:(2011-12-01T00:00:00Z)%5D%5B(37.00147):1:(46.97328)%5D%5B(10.0168):1:(21.98158)%5D"
    # url_r95p_seasonal = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/MedCordex_IPSL_2084_7a01_e870.csv?txx%5B(2006-01-01):1:(2050-10-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D"
    url_r95p_seasonal = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/MedCordex_IPSL_c22c_bffc_1baa.csv?consecutive_summer_days_index_per_time_period%5B(1970-01-01):1:(2005-10-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,number_of_csu_periods_with_more_than_5days_per_time_period%5B(1970-01-01):1:(2005-10-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D"
    #url_r95_monthly = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/atm_regional_4d78_6f74_63bc.csv?wind10m%5B(1969-12-30):1:(2005-11-20T00:00:00Z)%5D%5B(90):1:(-90)%5D%5B(-171.2326):1:(180.45724)%5D"
    # url_r95p_yearly = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/adriaclim_WRF_e73d_c8fa_d12a.csv?very_wet_days_wrt_95th_percentile_of_reference_period%5B(1992-01-01):1:(2011-01-01T00:00:00Z)%5D%5B(37.00147):1:(46.97328)%5D%5B(10.0168):1:(21.98158)%5D"
    # url_r95p_yearly = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/MedCordex_IPSL_ad60_605d_97a5.csv?txx%5B(1970-06-15T12:00:00Z):1:(2005-06-06T12:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D"
    # AdriaClim Indicators | MedCordex_IPSL | seasonal | proj | txx =====> 201k
    # tempo 299 secondi circa
    # try:
    #10293...
    # arrayVariabili = []
    # dataInizio = "1970-01-01"
    # dataFine = "2005-10-01T00:00:00Z"
    # latMax = "46.88878"
    # latMin = "37.28878"
    # lngMin = "10.24039"
    # lngMax = "21.66346"
    # url_final = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/MedCordex_IPSL_c22c_bffc_1baa.csv?"
    # for index, v in enumerate(arrayVariabili):
    #     if index == len(arrayVariabili) - 1:
    #         url_final += v + "%5B(" + dataInizio + "):1:(" + dataFine + ")%5D%5B(" + latMax + "):1:(" + latMin + ")%5D%5B(" + lngMin + "):1:(" + lngMax + ")%5D"
    #     else:
    #         url_final += v + "%5B(" + dataInizio + "):1:(" + dataFine + ")%5D%5B(" + latMax + "):1:(" + latMin + ")%5D%5B(" + lngMin + "):1:(" + lngMax + ")%5D,"
            
        

    #   polygons = Polygon.objects.filter(dataset_id ="MedCordex_IPSL_ad60_605d_97a5")
    #   print("Polygons =====", polygons)
    #   if polygons:
    #     for pol in polygons:
    #       print("Pol found=====", pol)
    #   else:
    #     print("Pol not found!!!!!!")

    # except Exception as e:
    #   print("Eccezione", e)
    # asyncio.run(delete_all("Polygon")) #to delete all polygons in the database
    # url_r95p_yearly = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/MedCordex_IPSL_2084_7a01_e870.csv?txx%5B(2006-01-01):1:(2050-10-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D"
    start_time = time.time()
    print("Sono iniziata ora!")
    # try:
    # n = Node.objects.get(id="MedCordex_IPSL_ad60_605d_97a5")
    # Polygon.objects.from_csv(
    #     url_r95p_yearly,
    #     dict=(dataset_id=n,)
    # )
    
    # INIZIO METODO CON UPDATE OR CREATE
    # #   print("Trovato",n)
    # # except Node.DoesNotExist:
    # #   print("Nodo MedCordex_IPSL_ad60_605d_97a5 non trovato!")

    chunksize = 10**6
    polygons = []
    dataset = Node.objects.get(id="MedCordex_IPSL_c22c_bffc_1baa")
    # asyncio.run(delete_all("Polygon",id=Node.objects.get(id="MedCordex_IPSL_c22c_bffc_1baa"))) #to delete all polygons in the database
    deletePoly("Polygon",id=dataset)
    dtypes = {'date_value': 'string', 'latitude': 'float32', 'longitude': 'float32'}
    names = ['date_value', 'latitude', 'longitude']
    
    if dataset.dimensions > 3:
        for name in dataset.dimension_names:
            if name != "time" and name != "latitude" and name != "longitude":
                dtypes[name] = 'float32'
                names.append(name)
    
    for i in range(0,dataset.variables):
        dtypes["value_" + str(i)] = 'float32'
        names.append("value_" + str(i))
    
    #print("names prima",names)
    dict_keys = names.copy()
    dict_keys.append("dataset_id")
    dict_keys.append("coordinate")
    # print("dict keys",dict_keys)
    #print("Names dopo",names)

    chunksize = 10**6
    for chunk in pd.read_table(
        url_r95p_seasonal,
        engine="c",
        sep=",",
        header=0,
        chunksize=chunksize,
        low_memory=False,
        names=names
    ):

        chunk.drop(index=chunk.index[0], axis=0, inplace=True)
        chunk = chunk.astype(dtypes)
        # print("chunk",chunk.head())
        # chunk["dataset_id"] = "MedCordex_IPSL_ad60_605d_97a5" # 4 sec circa
        # chunk["dataset_id"] = "adriaclim_WRF_c3bc_3ecd_2f3c" # monthly 10kk dati 742.37 sec
        # chunk["dataset_id"] = "MedCordex_IPSL_2084_7a01_e870" # seasonal 201k dati meno di 10 sec
        chunk["dataset_id"] = dataset.id # seasonal 161k dati 22 secondi
        # chunk.assign(coordinate=[*zip(chunk["latitude",chunk["longitude"]])])
        # chunk["dataset_id"] = "atm_regional_a4d7_6d53_fdfd"
        chunk_geo = gpd.GeoDataFrame(chunk, geometry=gpd.points_from_xy(chunk.latitude, chunk.longitude), crs="EPSG:4326")
        chunk_geo['coordinate'] = chunk_geo['geometry'].apply(lambda p: Point(p.y,p.x,srid=4326))
        # chunk_geo = chunk_geo.rename(columns={'geometry':'coordinate'})
        chunk_geo = chunk_geo.drop(columns=['geometry'])
        chunk_geo["coordinate"] = chunk_geo["coordinate"].apply(lambda p: p.wkt)
        csv_data = chunk_geo.to_csv(index=False)
        csv_file = io.StringIO(csv_data)
        # print("Ci arrivo")
        # print("chunk_geo",chunk_geo)
        # Convert the geometry column to WKT format and save the GeoDataFrame to a CSV file
        # csv_data = pd.DataFrame(chunk_geo.assign(geometry=chub["geometry"].apply(lambda p: p.wkt))).to_csv()
        # csv_data = chunk_geo.to_csv(index=False)
        # # print("csv_data",csv_data)  
        # csv_file = io.StringIO(csv_data)
        mapping = {
            name: name.lower()
            for name in dict_keys
        }
        # for name in dict_keys:
        #       if name != "coordinate":
        #           mapping[name] = name.lower()

        # print("mapping",mapping)

    

        try:
            #print("Test======",chunk.head())
            # if(Polygon.objects.filter(dataset_id="MedCordex_IPSL_c22c_bffc_1baa", date_value = date_value, latitude = chunk["latitude"], longitude = chunk["longitude"])):
            
        # Polygon.objects.filter(dataset_id=Node.objects.get(id="MedCordex_IPSL_c22c_bffc_1baa")).delete()
            Polygon.copy_manager.from_csv(
                csv_file,
                mapping,
            )  
        
                   
                    # create_point = Point(row["latitude"],row["longitude"])
                    # # print("create_point",create_point)
                    # # print("type",type(create_point))
                    # # print("create_point.wkb",create_point.wkb)
                    # # print("create_point.wkt",create_point.wkt)
                    # # print("create_point.ewkb",create_point.ewkb)
                    # # print("create_point.ewkt",create_point.ewkt)
                    # # print("create_point.srid",create_point.srid)
                   
                    # p= Polygon(dataset_id=Node.objects.get(id=row["dataset_id"]),  
                    #                        value_0=row["value_0"],
                    #                        value_1 = row["value_1"],
                    #                        date_value=row["date_value"],
                    #                        coordinate = create_point.ewkb,
                    #                        latitude = row["latitude"],
                    #                        longitude = row["longitude"]
                    #                        )
                    # p.save()
        
            

        except Exception as e:
            print("Eccezione", e)
            return str(e)
    # dtypes = {'date_value': 'string', 'latitude': 'float32', 'longitude': 'float32', 'value_0': 'float32'}
    # for chunk in pd.read_table(
    #     url_micidiale,
    #     engine="c",
    #     sep=",",
    #     header=0,
    #     chunksize=chunksize,
    #     low_memory=False,
    #     names=["date_value", "latitude", "longitude", "value_0"]
    # ):

    #     chunk.drop(index=chunk.index[0], axis=0, inplace=True)
    #     chunk = chunk.astype(dtypes)
    #     # chunk["dataset_id"] = "MedCordex_IPSL_ad60_605d_97a5" # 4 sec circa
    #     # chunk["dataset_id"] = "adriaclim_WRF_c3bc_3ecd_2f3c" # monthly 10kk dati 742.37 sec
    #     # chunk["dataset_id"] = "MedCordex_IPSL_2084_7a01_e870" # seasonal 201k dati meno di 10 sec
    #     chunk["dataset_id"] = "MedCordex_IPSL_c22c_bffc_1baa" # seasonal 161k dati 22 secondi
    #     # chunk["dataset_id"] = "atm_regional_a4d7_6d53_fdfd"
        
    #     csv_data = chunk.to_csv(index=False)
    #     csv_file = io.StringIO(csv_data)
        

    #     try:
    #         #print("Test======",chunk.head())
    #         # if(Polygon.objects.filter(dataset_id="MedCordex_IPSL_c22c_bffc_1baa", date_value = date_value, latitude = chunk["latitude"], longitude = chunk["longitude"])):
            
    #        # Polygon.objects.filter(dataset_id=Node.objects.get(id="MedCordex_IPSL_c22c_bffc_1baa")).delete()
    #         Polygon.copy_manager.from_csv(
    #             csv_file,
    #             dict(
    #                 dataset_id_id="dataset_id",
    #                 date_value="date_value",
    #                 latitude="latitude",
    #                 longitude="longitude",
    #                 value_0="value_0",
    #             ),
    #             # static_mapping = {
    #             #     'value_0': "value_0",
    #             # },
    #             # drop_constraints=False,
    #             # drop_indexes=False,
    #             # static_mapping={
    #             #     "dataset_id": "MedCordex_IPSL_ad60_605d_97a5",
    #             # },
    #         )
            

    #     except Exception as e:
    #         print("Eccezione", e)
    #         return str(e)
    

    # Bulk insert all polygons in a single database query
    # Polygon.objects.bulk_create(polygons)
    # FINE METODO CON UPDATE OR CREATE

    print("TIME ROMPO TUTTO {:.2f} seconds".format(time.time() - start_time))


def percentile(
    percentile,
    dataset_id,
    layer_name,
    time_start,
    time_finish,
    latitude1,
    longitude1,
    latitude2,
    longitude2,
    latitude3,
    longitude3,
    num_parameters,
    range_value,
    is_indicator,
    latMin,
    longMin,
    latMax,
    longMax,
):
    if is_indicator == "false":
        allData1 = getMaxMinMeanMomentGraphicGeneric(
            dataset_id,
            layer_name,
            time_start,
            time_finish,
            latitude1,
            longitude1,
            num_parameters,
            range_value,
            is_indicator,
            latMin,
            longMin,
            latMax,
            longMax,
        )
        allData2 = getMaxMinMeanMomentGraphicGeneric(
            dataset_id,
            layer_name,
            time_start,
            time_finish,
            latitude2,
            longitude2,
            num_parameters,
            range_value,
            is_indicator,
            latMin,
            longMin,
            latMax,
            longMax,
        )
        allData3 = getMaxMinMeanMomentGraphicGeneric(
            dataset_id,
            layer_name,
            time_start,
            time_finish,
            latitude3,
            longitude3,
            num_parameters,
            range_value,
            is_indicator,
            latMin,
            longMin,
            latMax,
            longMax,
        )
        result_percentile = []
        all_values1 = allData1[1]
        all_values2 = allData2[1]
        all_values3 = allData3[1]
        all_date = allData1[0]
        unit = allData1[len(allData1) - 1]
        allData = []
        i = 0
        for date, val1, val2, val3 in np.nditer(
            [all_date, all_values1, all_values2, all_values3], flags=["refs_ok"]
        ):
            array_percentile = [float(val1), float(val2), float(val3)]
            result_percentile.insert(
                i, percentileFunction(array_percentile, percentile)
            )

        result_percentile.reverse()
        allData = [all_date, result_percentile, layer_name, unit]
        return allData
    else:
        allData1 = getMaxMinMeanMomentGraphicGeneric(
            dataset_id,
            layer_name,
            time_start,
            time_finish,
            latitude1,
            longitude1,
            num_parameters,
            range_value,
            is_indicator,
            latMin,
            longMin,
            latMax,
            longMax,
        )
        result_percentile = []
        all_values1 = allData1[1]
        all_date = allData1[0]
        unit = "Not available"
        allData = []
        i = 0
        for date, val1 in np.nditer([all_date, all_values1], flags=["refs_ok"]):
            array_percentile = [float(val1)]
            result_percentile.insert(
                i, percentileFunction(array_percentile, percentile)
            )

        result_percentile.reverse()
        allData = [all_date, result_percentile, layer_name, unit]
        return allData


def percentile_new(n):
    def percentile_(x):
        return np.percentile(x, n)

    percentile_.__name__ = "percentile_%s" % n
    return percentile_


def percentileFunction(arr, percentile):
    # sort the array
    arr.sort()
    k = len(arr) * percentile
    if isinstance(k, int) & len(arr) > 1:
        # is an integer, mean between the k-nth and the (k+1)-nth value
        mean = (arr[k - 1] + arr[k]) / 2
        return mean
    else:
        index_array = round(k)
        return arr[index_array - 1]


def getDataVectorial(
    dataset_id,
    layer_name,
    date_start,
    latitude_start,
    latitude_end,
    longitude_start,
    longitude_end,
    num_param,
    range_value,
    is_indicator,
):
    # print("ARRIVO PRIMA DI URL_IS_IND")
    url = url_is_indicator(
        is_indicator,
        False,
        True,
        dataset_id=dataset_id,
        layer_name=layer_name,
        date_start=date_start,
        latitude_start=latitude_start,
        latitude_end=latitude_end,
        longitude_start=longitude_start,
        longitude_end=longitude_end,
        num_param=num_param,
        range_value=range_value,
    )
    #print("URL DATA VECTORIAL========", url)
    df = pd.read_csv(url, dtype="unicode")
    allData = []
    values = []
    lat_coordinates = []
    long_coordinates = []
    df = df.dropna(how="any", axis=0)

    i = 0
    for index, row in df.iterrows():
        values.insert(i, row[layer_name])
        lat_coordinates.insert(i, row["latitude"])
        long_coordinates.insert(i, row["longitude"])
        i += 1
    del values[0]
    del lat_coordinates[0]
    del long_coordinates[0]

    [float(i) for i in values]

    value_min = min(values)
    value_max = max(values)

    allData = [values, lat_coordinates, long_coordinates, value_min, value_max]

    return allData


def convertToTime(date_str):
    return dt.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")


def operation_before_after_cache(df_polygon, statistic, time_op):
    try:
        ops = {
            "avg": "mean",
            "min": "min",
            "max": "max",
            "sum": "sum",
            "median": "median",
            "10thPerc": percentile_new(10),
            "90thPerc": percentile_new(90),
            "min_mean_max": "min_mean_max",
            "min_10thPerc_median_90thPerc_max": "min_10thPerc_median_90thPerc_max",
        }
        groupby_col = (
            "date_value"
            if time_op == "default"
            else df_polygon["date_value"].dt.month
            if time_op == "annualMonth"
            else df_polygon["date_value"].dt.day
        )

        if ops[statistic] == "min_mean_max":
            agg_func = ["min", "mean", "max"]
        elif ops[statistic] == "min_10thPerc_median_90thPerc_max":
            agg_func = ["min", percentile_new(10), "median", percentile_new(90), "max"]
        else:
            agg_func = ops[statistic]
        # AGG IS USED TO APPLY AN AGGREGATE FUNCTION AND YOU NEED TO PASS IT THE NAME OF THE FUNCTION (min,avg,max etc)!!!

        res_values = df_polygon.groupby(groupby_col)["value_0"].agg(
            agg_func
        )  # AGG IS USED TO APPLY AN AGGREGATE FUNCTION
        #print("res_values", res_values)
        df_polygon = df_polygon.drop_duplicates(subset=["date_value"], keep="first")
        # print("MONTHS =", months)
        list_time = (
            list(res_values.index.strftime("%d/%m/%Y"))
            if time_op == "default"
            else [months[index] for index in res_values.index.tolist()]
            if time_op == "annualMonth"
            else list(res_values.index.strftime("%d/%m"))
        )
        # print("list_time",list_time)
        data_pol_list = []

        if ops[statistic] == "min_mean_max":
            list_min = res_values["min"].tolist()
            list_max = res_values["max"].tolist()
            list_mean = res_values["mean"].tolist()
            for i in range(len(list_time)):
                data_pol = {}
                data_pol["x"] = list_time[i]
                data_pol["Minimum"] = list_min[i]
                data_pol["Mean"] = list_mean[i]
                data_pol["Maximum"] = list_max[i]
                data_pol_list.append(data_pol)

        elif ops[statistic] == "min_10thPerc_median_90thPerc_max":
            list_10th_perc = res_values["percentile_10"].tolist()
            list_90th_perc = res_values["percentile_90"].tolist()
            list_min = res_values["min"].tolist()
            list_max = res_values["max"].tolist()
            list_median = res_values["median"].tolist()
            for i in range(len(list_time)):
                data_pol = {}
                data_pol["x"] = list_time[i]
                data_pol["Minimum"] = list_min[i]
                data_pol["10th Percentile"] = list_10th_perc[i]
                data_pol["90th Percentile"] = list_90th_perc[i]
                data_pol["Median"] = list_median[i]
                data_pol["Maximum"] = list_max[i]
                data_pol_list.append(data_pol)
        else:
            list_value = list(res_values.values)
            for i in range(len(list_time)):
                data_pol = {}
                data_pol["x"] = list_time[i]
                data_pol["y"] = list_value[i]
                data_pol_list.append(data_pol)

        # vale per entrambi allo stesso modo data_table_list e anche di allData
        return data_pol_list
    except Exception as e:
        print("eccezione========", e)
        return str(e)

#cambiare tutto il modo in cui ragiona, controllare prima la cache, se non c'è controllare il db e se non c'è prenderlo come ora dal dataserver
#se c'è nel db, elaborarlo e salvarlo nella cache!

def getDataPolygonNew(
    dataset_id,
    layer_name,
    date_start,
    date_end,
    lat_lng_obj,
    statistic,
    time_op,
    num_param,
    range_value,
    is_indicator,
    lat_min,
    lat_max,
    lng_min,
    lng_max,
    parametro_agg,
    circle_coords,
):
    start_time = time.time()
    print("STARTED GETDATAPOLYGONNEW!")
    vertices = []
    vertices_geos_poly = []

    for lat_lng in lat_lng_obj:
        vertices.append((float(lat_lng["lat"]), float(lat_lng["lng"])))
        vertices_geos_poly.append((float(lat_lng["lng"]), float(lat_lng["lat"])))

    shapely_polygon = ShapelyPolygon(vertices)
    shapely_polygon_inverse = ShapelyPolygon(vertices_geos_poly)
   
    try:
        geos_polygon = GeosPolygon.from_ewkt(shapely_polygon_inverse.wkt)
        # print("geos_polygon=======",geos_polygon)
    except Exception as e:
        print("exc",e)
        return str(e)
  
    shapely.speedups.enable()
    pol_vertices_str = str(vertices[0][0]).replace(" ", "")
    key_cached = dataset_id + "_" + pol_vertices_str #chiave della cache!
    xmin = None
    ymin = None
    xmax = None
    ymax = None
    area = None
    circ = None
    

    # print("check cache",cache.get(key=key_cached))
    #aggiungere controllo cache prima.....
    cache_result = cache.get(key=key_cached)
    
    if cache_result is not None:
        print("CACHE HIT!")
        #siamo nella cache
        #prendere tutti i dati memorizzati nella cache ed elaborarli e passarli al frontend
        #print("cache_result=======",cache_result)
        pol_from_cache = json.loads(cache_result)
        #print("pol_from_cache=======",pol_from_cache)
        dataframe_from_dict = pd.DataFrame.from_dict(pol_from_cache["dataBeforeOp"])
        # print("pol_from_cache=======",pol_from_cache)
        dataframe_from_dict["date_value"] = pd.to_datetime(dataframe_from_dict["date_value"])
        #print("dataframe_from_dict=======",dataframe_from_dict["date_value"])
        pol_from_cache["dataPol"] = operation_before_after_cache(dataframe_from_dict,statistic,time_op)
        return pol_from_cache

    else:
        # polygons = Polygon.objects.filter(
        #     dataset_id=dataset_id, pol_vertices_str=pol_vertices_str
        # 
        print("Check if it is in db!")
        polygons = Polygon.objects.filter(
            Q(dataset_id=dataset_id) & Q(coordinate__within=(geos_polygon)))
        if polygons.exists():
            print("DOPO FILTER")
            
            # qui siamo nel caso in cui è presente il poligono con quel dataset id e con i punti nel poligono selezionato!
            try:
                print("CACHE MISS AND DB HIT!")
                # print("pol",polygons)
                # all_points_poly = filter(lambda pol:Point(pol.latitude,pol.longitude).within(shapely_polygon),polygons)
                allData = {}
                data_table_list = []
                for pol in polygons:
                    #checkare se quel determinato punto del dataset sta nel poligono selezionato
                    #sta nel poligono selezionato 
                    data_table = {}
                    # print("dataTable[i]",dataTable[i])
                    data_table["time"] = pol.date_value
                    data_table["latitude"] = pol.latitude
                    data_table["longitude"] = pol.longitude
                    data_table[layer_name] = pol.value_0 if not pd.isna(pol.value_0) else "Value not defined"
                    
                    if parametro_agg != "None":
                        # print("Entro qui yeahhhhhh!!")
                        data_table[parametro_agg] = pol.parametro_agg
                    data_table_list.append(data_table)
                        
                        
                    #
                allData[
                    "dataTable"
                ] = data_table_list  # così abbiamo la tabella, ora ci serve il grafico.....
                # print("allData[dataTable]=======", allData["dataTable"])

                # pol["value"], pol["date_value"],pol["latitude"],pol["longitude"]
                #print("Test1")
                df_polygon_model = pd.DataFrame(
                    [
                        model_to_dict(p, fields=[field.name for field in p._meta.fields])
                        for p in polygons
                    ]
                )
                df_polygon_model = df_polygon_model.drop("coordinate",axis=1)
                #print("Test 2==========", df_polygon_model.head())
                df_polygon_model = df_polygon_model.drop_duplicates(
                    subset=["date_value", "latitude", "longitude", "value_0"], keep="first"
                )
                df_polygon_model = df_polygon_model.dropna(how="all", axis=1)
                allData["dataBeforeOp"] = df_polygon_model.to_dict(orient="records")
                date_value_to_list = df_polygon_model.copy()
                date_value_to_list = date_value_to_list.drop_duplicates(subset="date_value",keep="first")
                date_value_to_list["date_value"] = pd.to_datetime(date_value_to_list["date_value"])

               
                # a seconda del valore di operation e di time_op viene fatta l'operazione7
                df_polygon_model["date_value"] = pd.to_datetime(df_polygon_model["date_value"])

                trend_value_mean = df_polygon_model.groupby("date_value")["value_0"].mean().tolist()
                # print("Trend value_mean",trend_value_mean)
                trend_value = calculate_trend(date_value_to_list["date_value"].tolist(),trend_value_mean)
                
                # df_polygon_model["value_0"]
               
                mean = df_polygon_model["value_0"].mean()
                median = df_polygon_model["value_0"].median()
                std_dev = df_polygon_model["value_0"].std()
                allData["mean"] = mean
                allData["median"] = median
                allData["stdev"] = std_dev
                allData["trend_yr"] = trend_value
                cache.set(key=key_cached,value=json.dumps(allData),timeout=43200) #lo setta nella cache per 12 ore
                allData["dataPol"] = operation_before_after_cache(
                    df_polygon_model, statistic, time_op
                )

                # value, date_value, latitude, longitude
                print("DB TIME: ", time.time() - start_time)

                # pol_from_cache = json.loads(cache.get(key=key_cached))
                # print("pol_from_cache=======",pol_from_cache)
                # try:
                #   pol_from_cache["dataPol"] = operation_before_after_cache(pol_from_cache["dataBeforeOp"],statistic,time_op,True)
                # except Exception as e:
                # print("ueeeee errore",e)
                # return str(e)
                # print("pol_from_cache without json loads",cache.get(key_cached))
                # print("pol_from_cache=========",pol_from_cache)
                return allData
            except Exception as e:
                print("Errore", e)
                return str(e)

        else:
            print("DB AND CACHE MISS!")
            # Definisci i limiti del poligono

            # caso di circle coords

            xmin, ymin, xmax, ymax = shapely_polygon.bounds
            # distanze = []
            circ = shapely_polygon.length
            area = shapely_polygon.area

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

            # anomaly 0.01 2378 points 625.62 seconds poligono più piccolo
            # anomaly 0.05 75 points 19.05 seconds poligono più piccolo
            # anomaly 0.05 1244 points 335.21 seconds croazia(poligono più grande)
            # r95p yearly 0.05 75 points 23.31 seconds poligono più piccolo

            # Salva tutte le coordinate dei punti interni al poligono
            points_inside_polygon = []
            try:
                if len(circle_coords) > 0:
                    for coord in circle_coords:
                        # print("Cooord",coord)
                        point = ShapelyPoint(coord["lat"], coord["lng"])
                        if point.within(shapely_polygon):
                            points_inside_polygon.append((coord["lat"], coord["lng"]))
                else:
                    for x in range(int(xmin / step), int(xmax / step)):
                        for y in range(int(ymin / step), int(ymax / step)):
                            point = ShapelyPoint(x * step, y * step)
                            if point.within(shapely_polygon):
                                points_inside_polygon.append((x * step, y * step))
            except Exception as coord:
                print("Eccezione", coord)
                return str(coord)

            # Visualizza le coordinate dei punti all'interno del poligono
            # print("PUNTI INTERNI AL POLIGONO =", points_inside_polygon)
            print("PUNTI INTERNI AL POLIGONO LENGHT =", len(points_inside_polygon))
            df_polygon = pd.DataFrame(columns=["date_value", "lat_lng", "value_0"])

            i = 0
            dataTable = []
            for point in points_inside_polygon:
                if is_indicator == "false":
                    url = url_is_indicator(
                        is_indicator,
                        True,
                        False,
                        dataset_id=dataset_id,
                        layer_name=layer_name,
                        time_start=date_start,
                        time_finish=date_end,
                        latitude=str(point[0]),
                        longitude=str(point[1]),
                        num_parameters=num_param,
                        range_value=range_value,
                    )
                    df = pd.read_csv(url, dtype="unicode")
                else:
                    # print("Entro quiiiiiii!!!!")
                    try:
                        url = url_is_indicator(
                            is_indicator,
                            True,
                            True,
                            dataset_id=dataset_id,
                            layer_name=layer_name,
                            time_start=date_start,
                            time_finish=date_end,
                            latitude=str(point[0]),
                            longitude=str(point[1]),
                            num_parameters=num_param,
                            range_value=range_value,
                        )
                        #print("URL DATA VECTORIAL========", url)
                        df = pd.read_csv(url, dtype="unicode")
                    except Exception as e:
                        print("fdkjsjk", e)
                        continue

                # print("LAYER NAME PRIMA DI TUTTO =", layer_name)
                # DA SISTEMARE QUI!!!!!!!!!!!***********************************
                try:
                    for index,row in enumerate(df.to_dict(orient="records")):
                        # print("PARAMETRO AGGIUNTIVO =", type(parametro_agg))
                        # print("PARAMETRO AGGIUNTIVO",parametro_agg)
                        if parametro_agg != "None":
                            if len(dataTable) == 0:
                                # print("LAYER NAME SE PARAMETRO =", row[layer_name])
                                dat_tab = {}
                                dat_tab["time"] = row["time"]
                                dat_tab["latitude"] = row["latitude"]
                                dat_tab["longitude"] = row["longitude"]
                                dat_tab[parametro_agg] = row[parametro_agg]
                                dat_tab[layer_name] = (
                                    row[layer_name]
                                    if not pd.isna(row[layer_name])
                                    else "Value not defined"
                                )
                                dataTable.append(dat_tab)
                                # EOBS_de0d_3ca1_a77a_45.60425767756453_avg
                                # EOBS_de0d_3ca1_a77a_45.60425767756453_avg
                            if index > 0:
                                dat_tab = {}
                                dat_tab["time"] = convertToTime(row["time"])
                                dat_tab["latitude"] = row["latitude"]
                                dat_tab["longitude"] = row["longitude"]
                                dat_tab[parametro_agg] = row[parametro_agg]
                                dat_tab[layer_name] = (
                                    row[layer_name]
                                    if not pd.isna(row[layer_name])
                                    else "Value not defined"
                                )
                                dataTable.append(dat_tab)
                                df_polygon.loc[i] = [
                                    row["time"],
                                    "(" + row["latitude"] + "," + row["longitude"] + ")",
                                    row[layer_name],
                                ]
                                defaults = {
                                    "value_0": float(row[layer_name]),
                                    "pol_vertices_str": pol_vertices_str,
                                    "parametro_agg": row[parametro_agg],
                                }
                                Polygon.objects.update_or_create(
                                                dataset_id=Node.objects.get(id=dataset_id),
                                                date_value=convertToTime(row["time"]),
                                                latitude=float(row["latitude"]),
                                                longitude=float(row["longitude"]),
                                                coordinate = Point(float(row["longitude"]), float(row["latitude"])),
                                                defaults=defaults,
                                                                )
                                # pol = Polygon(pol_vertices_str = pol_vertices_str, value_0 = float(row[layer_name]), dataset_id = Node.objects.get(id=dataset_id), date_value = convertToTime(row["time"]),
                                #               latitude = float(row["latitude"]), longitude = float(row["longitude"]), parametro_agg = row[parametro_agg])
                                # pol.save()
                                # dataTable.append({"time": row["time"], "latitude": row["latitude"],"longitude": row["longitude"],parametro_agg:row[parametro_agg],layer_name:row[layer_name]})
                                i += 1
                        else:
                            if len(dataTable) == 0:
                                # print("LAYER NAME SE NON PARAMETRO PRIMO =", row[layer_name])
                                dat_tab = {}
                                dat_tab["time"] = row["time"]
                                dat_tab["latitude"] = row["latitude"]
                                dat_tab["longitude"] = row["longitude"]
                                # dat_tab[parametro_agg] = row[parametro_agg]
                                # print("Sono arrvato qui")
                                dat_tab[layer_name] = (
                                    row[layer_name]
                                    if not pd.isna(row[layer_name])
                                    else "Value not defined"
                                )
                                dataTable.append(dat_tab)
                                #  dataTable.append(dat)
                            if index > 0:
                                # print("LAYER NAME SE NON PARAMETRO SECONDO =", row[layer_name])
                                dat_tab = {}
                                dat_tab["time"] = convertToTime(row["time"])
                                dat_tab["latitude"] = row["latitude"]
                                dat_tab["longitude"] = row["longitude"]
                                # dat_tab[parametro_agg] = row[parametro_agg]
                                dat_tab[layer_name] = (
                                    row[layer_name]
                                    if not pd.isna(row[layer_name])
                                    else "Value not defined"
                                )
                                dataTable.append(dat_tab)
                                df_polygon.loc[i] = [
                                    row["time"],
                                    "(" + row["latitude"] + "," + row["longitude"] + ")",
                                    row[layer_name],
                                ]
                            # pol = Polygon(pol_vertices_str = pol_vertices_str, value_0 = float(row[layer_name]), dataset_id = Node.objects.get(id=dataset_id), date_value = convertToTime(row["time"]),
                                #             latitude = float(row["latitude"]), longitude = float(row["longitude"]))
                                #pol.save()
                                defaults = {
                                    "value_0": float(row[layer_name]),
                                    "pol_vertices_str": pol_vertices_str,
                                }
                                Polygon.objects.update_or_create(
                                                dataset_id=Node.objects.get(id=dataset_id),
                                                date_value=convertToTime(row["time"]),
                                                latitude=float(row["latitude"]),
                                                longitude=float(row["longitude"]),
                                                coordinate = Point(float(row["longitude"]), float(row["latitude"])),
                                                defaults=defaults,
                                                                )
                                # dataTable.append({"time": row["time"], "latitude": row["latitude"],"longitude": row["longitude"],layer_name:row[layer_name]})
                                i += 1
                                # TIME GETDATAPOLYGONNEW 8.58 seconds r95p monthly senza save su db
                                # TIME GETDATAPOLYGONNEW 1960.06 seconds Snowfall rate (projections, day)
                except Exception as e:
                    print("EXCEPTION 3", e)
                    return str(e)

            try:
                df_polygon = df_polygon.drop_duplicates(
                    subset=["date_value", "lat_lng", "value_0"], keep="first"
                )
                df_polygon = df_polygon.dropna(how="all", axis=1)
                allData = {}
                
                df_polygon["value_0"] = pd.to_numeric(df_polygon["value_0"])
                allData["dataBeforeOp"] = df_polygon.to_dict(orient="records")
                #calcolare la media di tutti i valori raggruppati per data
                # date_value_to_list = df_polygon["date_value"].tolist()
               
                # a seconda del valore di operation e di time_op viene fatta l'operazione7
                # print("PRIMA DEL TREND")
                date_value_to_list = df_polygon.copy()
                date_value_to_list = date_value_to_list.drop_duplicates(subset="date_value",keep="first")
                date_value_to_list["date_value"] = pd.to_datetime(date_value_to_list["date_value"])

               
                # a seconda del valore di operation e di time_op viene fatta l'operazione7
                df_polygon["date_value"] = pd.to_datetime(df_polygon["date_value"])
                trend_value_mean = df_polygon.groupby("date_value")["value_0"].mean().tolist()
                # print("Trend value_mean",trend_value_mean)
                trend_value = calculate_trend(date_value_to_list["date_value"].tolist(),trend_value_mean)
                # df_polygon["date_value"] = pd.to_datetime(df_polygon["date_value"]
                # trend_value_mean = df_polygon.groupby("date_value")["value_0"].mean().tolist()
                # print("Trend value_mean",trend_value_mean)
                # trend_value = calculate_trend(date_value_to_list,trend_value_mean)
                mean = df_polygon["value_0"].mean()
                median = df_polygon["value_0"].median()
                std_dev = df_polygon["value_0"].std()
                data_table_list = []
                for i in range(len(dataTable)):
                    data_table = {}
                    # print("dataTable[i]",dataTable[i])
                    data_table["time"] = dataTable[i]["time"]
                    data_table["latitude"] = dataTable[i]["latitude"]
                    data_table["longitude"] = dataTable[i]["longitude"]
                    data_table[layer_name] = dataTable[i][layer_name]
                    if parametro_agg != "None":
                        # print("Entro qui yeahhhhhh!!")
                        data_table[parametro_agg] = dataTable[i][parametro_agg]
                    data_table_list.append(data_table)

                allData["dataTable"] = data_table_list
                allData["mean"] = mean
                allData["median"] = median
                allData["stdev"] = std_dev
                allData["trend_yr"] = trend_value
                # Mi setto la cache prima di fare l'operazione richiesta ma con tutte le date e tutti i valori!
                cache.set(key=key_cached,value=json.dumps(allData),timeout=43200) #12 ore di cache
                print("DB AND CACHE setted!")

                allData["dataPol"] = operation_before_after_cache(
                    df_polygon, statistic, time_op
                )
                print(
                    "TIME GETDATAPOLYGONNEW {:.2f} seconds".format(time.time() - start_time)
                )
            except Exception as e:
                print("EXCEPTION 1", e)
                return str(e)
                # print("allData",allData)

                # print("list(df_polygon['time'])",list(df_polygon["time"]))
            return allData


def createArrow(
    datasetId1,
    datasetId2,
    layer_name1,
    date_start1,
    num_param1,
    range_value1,
    layer_name2,
    date_start2,
    latitude_start,
    latitude_end,
    longitude_start,
    longitude_end,
    num_param2,
    range_value2,
):
    lat_coordinates1 = []
    long_coordinates1 = []
    lat_coordinates2 = []
    long_coordinates2 = []
    values1 = []
    values2 = []
    allValuesArrow = []

    if num_param1 > 3:
        url1 = (
            ERDDAP_URL
            + "/griddap/"
            + datasetId1
            + ".csv?"
            + layer_name1
            + "%5B("
            + date_start1
            + "):1:("
            + date_start1
            + ")%5D%5B("
            + str(range_value1)
            + "):1:("
            + str(range_value1)
            + ")%5D%5B("
            + latitude_start
            + "):1:("
            + latitude_end
            + ")%5D%5B("
            + longitude_start
            + "):1:("
            + longitude_end
            + ")%5D"
        )
    else:
        url1 = (
            ERDDAP_URL
            + "/griddap/"
            + datasetId1
            + ".csv?"
            + layer_name1
            + "%5B("
            + date_start1
            + "):1:("
            + date_start1
            + ")%5D%5B("
            + latitude_start
            + "):1:("
            + latitude_end
            + ")%5D%5B("
            + longitude_start
            + "):1:("
            + longitude_end
            + ")%5D"
        )

    if num_param2 > 3:
        url2 = (
            ERDDAP_URL
            + "/griddap/"
            + datasetId2
            + ".csv?"
            + layer_name2
            + "%5B("
            + date_start2
            + "):1:("
            + date_start2
            + ")%5D%5B("
            + str(range_value2)
            + "):1:("
            + str(range_value2)
            + ")%5D%5B("
            + latitude_start
            + "):1:("
            + latitude_end
            + ")%5D%5B("
            + longitude_start
            + "):1:("
            + longitude_end
            + ")%5D"
        )
    else:
        url2 = (
            ERDDAP_URL
            + "/griddap/"
            + datasetId2
            + ".csv?"
            + layer_name2
            + "%5B("
            + date_start2
            + "):1:("
            + date_start2
            + ")%5D%5B("
            + latitude_start
            + "):1:("
            + latitude_end
            + ")%5D%5B("
            + longitude_start
            + "):1:("
            + longitude_end
            + ")%5D"
        )

    print(url1)
    print(url2)
    df1 = pd.read_csv(url1, dtype="unicode")
    df2 = pd.read_csv(url2, dtype="unicode")

    i = 0
    for index, row in df1.iterrows():
        values1.insert(i, row[layer_name1])
        lat_coordinates1.insert(i, row["latitude"])
        long_coordinates1.insert(i, row["longitude"])
        i += 1

    del values1[0]
    del lat_coordinates1[0]
    del long_coordinates1[0]

    j = 0
    for index, row in df2.iterrows():
        values2.insert(j, row[layer_name2])
        lat_coordinates2.insert(j, row["latitude"])
        long_coordinates2.insert(j, row["longitude"])
        j += 1

    del values2[0]
    del lat_coordinates2[0]
    del long_coordinates2[0]

    allValuesArrow = [
        lat_coordinates1,
        long_coordinates1,
        values1,
        lat_coordinates2,
        long_coordinates2,
        values2,
    ]
    return allValuesArrow
