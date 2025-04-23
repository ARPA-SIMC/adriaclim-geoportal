# Da views.py

# def index(request):
#     form=DatasetForm()
#     datasets=Node.objects.all()
#     indicators=Indicator.objects.filter(~Q(adriaclim_dataset="no"))
#     response=render(request,"homepage.html",{'form':form,'datasets':datasets,'indicators':indicators})
#     return response

# def overlays(request,dataset_id):
#     service=request.GET['service']
#     request1=request.GET['request']
#     layers=request.GET['layers']
#     styles=request.GET['styles']
#     format=request.GET['format']
#     transparent=request.GET['transparent']
#     version=request.GET['version']
#     width=request.GET['width']
#     height=request.GET['height']
#     crs=request.GET['crs']
#     bbox=request.GET['bbox']
#     bgcolor=request.GET['bgcolor']
#     url=ERDDAP_URL+"/wms/"+dataset_id+"/request?&service="+service+"&request="+request1+"&layers="+layers+"&styles="+styles+"&format="+format+"&transparent="+transparent+"&version="+version+"&bgcolor="+bgcolor+"&width="+width+"&height="+height+"&crs="+crs+"&bbox="+bbox
#     print(url)
#     requests_response = requests.get(url)
#     django_response = HttpResponse(
#             content=requests_response.content,
#             status=requests_response.status_code,
#             content_type=requests_response.headers['Content-Type']
#         )
        
#     return django_response

# def layers2D(request):
#     service=request.GET['service']
#     request1=request.GET['request']
#     layers=request.GET['layers']
#     styles=request.GET['styles']
#     format=request.GET['format']
#     transparent=request.GET['transparent']
#     version=request.GET['version']
#     width=request.GET['width']
#     height=request.GET['height']
#     crs=request.GET['crs']
#     bbox=request.GET['bbox']
#     time=request.GET['time']
#     bgcolor=request.GET['bgcolor']
#     dataset_id=layers.partition(":")[0]
#     url=ERDDAP_URL+"/wms/"+dataset_id+"/request?&service="+service+"&request="+request1+"&layers="+layers+"&styles="+styles+"&format="+format+"&transparent="+transparent+"&version="+version+"&bgcolor="+bgcolor+"&time="+time+"&width="+width+"&height="+height+"&crs="+crs+"&bbox="+bbox
#     requests_response = requests.get(url)
#     django_response = HttpResponse(
#             content=requests_response.content,
#             status=requests_response.status_code,
#             content_type=requests_response.headers['Content-Type']
#         )
        
#     return django_response

# def layers3D(request,parameter):
#     service=request.GET['service']
#     request1=request.GET['request']
#     layers=request.GET['layers']
#     styles=request.GET['styles']
#     format=request.GET['format']
#     transparent=request.GET['transparent']
#     version=request.GET['version']
#     width=request.GET['width']
#     height=request.GET['height']
#     crs=request.GET['crs']
#     bbox=request.GET['bbox']
#     time=request.GET['time']
#     bgcolor=request.GET['bgcolor']
#     value_param=request.GET[parameter]
#     dataset_id=layers.partition(":")[0]
#     url=ERDDAP_URL+"/wms/"+dataset_id+"/request?&service="+service+"&request="+request1+"&layers="+layers+"&styles="+styles+"&format="+format+"&transparent="+transparent+"&version="+version+"&bgcolor="+bgcolor+"&time="+time+"&"+parameter+"="+value_param+"&width="+width+"&height="+height+"&crs="+crs+"&bbox="+bbox
#     print(url)
#     requests_response = requests.get(url)
#     django_response = HttpResponse(
#             content=requests_response.content,
#             status=requests_response.status_code,
#             content_type=requests_response.headers['Content-Type']
#         )
        
#     return django_response


# def getTitle(request):
#     titles=allFunctions.getTitle()
#     return JsonResponse({'title':titles})

# def getIndicators(request):
#     indicators = allFunctions.getIndicators()
#     return JsonResponse({'indicators':indicators})

# @csrf_exempt
# def getTest(request):
#     print("test")
#     # return JsonResponse({'test':'test'})

# @csrf_exempt
# @api_view(['GET', 'POST'])
# def getPippo(request):
#     inputEs = request.data.get('inputEsterno')
#     return JsonResponse({'pippo':'pippo'})

# @api_view(['GET', 'POST'])
# def getPluto(request):
#     prova = Indicator.objects.get(dataset_id = "adriaclim_WRF_5e78_b419_ec8a")
#     provaSer = serializers.serialize('json', [prova, ])
#     provaJson = json.loads(provaSer)
#     return JsonResponse({"pluto": provaJson})

# def rompiamo_tutto(request):
#     try:
#         allFunctions.rompo_tutto()
#         return "Ho aggiustato tutto!!!!"
#     except Exception as e:
#         print("Ho rotto tutto!!!!!",e)
#         return str(e)

# def download_big_data(request):
#     try:
#         allFunctions.download_big_data()
#         return "Ho aggiustato tutto!!!!"
#     except Exception as e:
#         print("Ho rotto tutto!!!!! Final Version",e)
#         return str(e)

# def getWMS(request):
#     wms=allFunctions.getWMS()
#     # return JsonResponse({'wms':wms})

# def getDataTableIndicator(request,dataset_id,layer_name,time_start,time_finish,lat_min,lat_max,long_min,long_max,num_parameters,range_value):
#     data=allFunctions.getDataTableIndicator(dataset_id,layer_name,time_start,time_finish,lat_min,lat_max,long_min,long_max,num_parameters,range_value)
#     headers=[col for col in data.fieldnames]
#     out=[[row[h] for h in headers] for row in data]
#     return render(request,"getData.html",{"data":out,"headers":headers})

# def getMetadata(request,title):
#     metadata=allFunctions.getMetadataTime1(title)
#     return JsonResponse({'metadata':metadata})

# def getDataGraphicPolygon(request,dataset_id,layer_name,operation,context,time_start,time_finish,latMin,longMin,latMax,longMax,range_value):
#     allData=allFunctions.getDataGraphicGeneric(dataset_id,layer_name,time_start,time_finish,None,None,0,range_value,0,latMin,longMin,latMax,longMax,operation=operation,context=context,cache="yes")
#     return JsonResponse({'allData':allData})

# def getMetadataUrl(request,dataset_id):
#     metadata=allFunctions.getMetadataOfASpecificDataset(dataset_id)
#     return HttpResponse(metadata)

# def getDataExport(request,dataset_id,selectedType,layer_name,time_start,time_finish,latitude,longitude):
#     urlCall=ERDDAP_URL+"griddap/"+dataset_id+"."+selectedType+"?"+layer_name+"%5B("+time_start+"):1:("+time_finish+")%5D%5B("+latitude+"):1:("+latitude+")%5D%5B("+longitude+"):1:("+longitude+")%5D"
#     nameOfTheFile=dataset_id+"."+selectedType
#     file_path = os.path.join(settings.MEDIA_ROOT, urlCall)
#     if os.path.exists(file_path):
#         with open(file_path, 'rb') as fh:
#             response = HttpResponse(fh.read(), content_type="application/"+selectedType)
#             response['Content-Disposition'] = 'inline; filename=' + nameOfTheFile
#             return response
#     raise Http404

# def getDataGraphic(request,dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,num_parameters,range_value,is_indicator,latMin,longMin,latMax,longMax):
#     allData=allFunctions.getDataGraphic(dataset_id,layer_name,time_start,time_finish,latitude1,longitude1,
#                                         num_parameters,range_value,is_indicator,latMin,longMin,latMax,longMax)
#     return JsonResponse({'allData':allData})

# def getDataGraphicNew(request,dataset_id,layer_name,operation,context,time_start,time_finish,latitude,longitude,range_value,latMin,longMin,latMax,longMax):
#     allData=allFunctions.getDataGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude,longitude,0,range_value,0,latMin,longMin,latMax,longMax,operation=operation,context=context)
#     return JsonResponse({'allData':allData})

# def getDataGraphicCsv(request,dataset_id,layer_name,operation,context,time_start,time_finish,latitude,longitude,range_value,latMin,longMin,latMax,longMax):
#     allData=allFunctions.getDataGraphicGeneric(dataset_id,layer_name,time_start,time_finish,latitude,longitude,0,range_value,0,
#                                                latMin,longMin,latMax,longMax,operation=operation,context=context,output="csv")
#     return HttpResponse(
#             content=allData,
#             status=200,
#             content_type="text/csv"
#         )

# def allDatasets(request):
#         allData=allFunctions.listAllDatasets()
#         headers=[col for col in allData.fieldnames]
#         out=[[row[h] for h in headers] for row in allData]
#         return render(request,"allDatasets.html",{"data":out,"headers":headers})

# def getDataVectorial(request,dataset_id,layer_name,date_start,latitude_start,latitude_end,longitude_start,longitude_end,num_param,range_value,is_indicator):
#     dataVect=allFunctions.getDataVectorial(dataset_id,layer_name,date_start,latitude_start,latitude_end,longitude_start,longitude_end,num_param,range_value,is_indicator)
#     return JsonResponse({'dataVect':dataVect})

# def getWindArrows(request,datasetId1,datasetId2,layer_name1,date_start1,num_param1,range_value1,layer_name2,date_start2,latitude_start,latitude_end,longitude_start,longitude_end,num_param2,range_value2):
#     windArrows=allFunctions.createArrow(datasetId1,datasetId2,layer_name1,date_start1,num_param1,range_value1,layer_name2,date_start2,latitude_start,latitude_end,longitude_start,longitude_end,num_param2,range_value2)
#     return JsonResponse({'windArrows':windArrows})

# @api_view(['GET', 'POST'])
# def getInd(request):
#     ind = Indicator.objects.all()
#     data = [model_to_dict(i) for i in ind]
#     return JsonResponse({"ind": data})














# da Metadata/view.py


# def getMetadataForm(request,dataset_id):
#     if request.method=="GET":
#         form=DatasetForm(request.GET)
#         if form.is_valid():
#             id_passed=form.cleaned_data['dataset_id']
#             allFunctions.getMetadataOfASpecificDataset(id_passed)
#             return render(request,"specificDataset.html")

#     allFunctions.getMetadataOfASpecificDataset(dataset_id)
#     return render(request,"specificDataset.html")
































# da allFunctions.py

# def getTitle():
#     start_time = time.time()
#     print("Started getTitle()")
#     url_datasets = ERDDAP_URL + "/info/index.csv?page=1&itemsPerPage=100000"
#     df = pd.read_csv(
#         download_with_cache_as_csv(url_datasets),
#         header=0,
#         sep=",",
#         names=[
#             "griddap",
#             "subset",
#             "tabledap",
#             "Make A Graph",
#             "wms",
#             "files",
#             "Title",
#             "Summary",
#             "FGDC",
#             "ISO 19115",
#             "Info",
#             "Background Info",
#             "RSS",
#             "Email",
#             "Institution",
#             "Dataset ID",
#         ],
#         na_values="Value not available",
#     )
#     titleList = []

#     df1 = df.replace(np.nan, "", regex=True)

#     for index, row in df1.iterrows():
#         if (
#             row["Title"] != "* The List of All Active Datasets in this ERDDAP *"
#             and row["wms"] != "wms"
#             and not re.search("^indicat*", row["Dataset ID"])
#         ):
#             titleList.append(row["Title"])

#     print(
#         "Time to finish getTitle() ========= {:.2f} seconds".format(
#             time.time() - start_time
#         )
#     )
#     return titleList


# def getIndicators():
#     start_time = time.time()
#     print("Started getIndicators()")
#     url_datasets = ERDDAP_URL + "/info/index.csv?page=1&itemsPerPage=100000"
#     df = pd.read_table(
#         download_with_cache_as_csv(url_datasets),
#         header=0,
#         sep=",",
#         engine="c",
#         names=[
#             "griddap",
#             "subset",
#             "tabledap",
#             "Make A Graph",
#             "wms",
#             "files",
#             "Title",
#             "Summary",
#             "FGDC",
#             "ISO 19115",
#             "Info",
#             "Background Info",
#             "RSS",
#             "Email",
#             "Institution",
#             "Dataset ID",
#         ],
#         na_values="Value not available",
#     )
#     indicator_list = []
#     dataset_list = []
#     scale_list = []
#     print(
#         "Time to finish first read_csv getIndicators() ========= {:.2f} seconds".format(
#             time.time() - start_time
#         )
#     )
#     df = df.fillna("")
#     Indicator.objects.all().delete()
#     for index, row in df.iterrows():
#         if (
#             row["Info"] != "Info"
#             and row["Dataset ID"] != "allDatasets"
#             and re.search("indicator", row["Title"], re.IGNORECASE)
#         ):
#             # if the dataset_id starts with indicat...For now we assume that indicators have this thing in common......
#             # we found an indicator so we need to explore its metadata!
#             adriaclim_scale = None
#             adriaclim_dataset = None
#             adriaclim_timeperiod = None
#             adriaclim_model = None
#             adriaclim_type = None
#             institution = "UNKNOWN"
#             time_start = None
#             time_end = None
#             lat_min = None
#             lat_max = None
#             lng_min = None
#             lng_max = None

#             variables = 0
#             variable_names = ""
#             dimensions = 0
#             dimension_names = ""

#             dataset_id = row["Dataset ID"]
#             metadata_url = row["Info"]
#             tabledap_url = row["tabledap"]
#             griddap_url = row["griddap"]
#             get_info = pd.read_table(
#                 download_with_cache_as_csv(row["Info"]),
#                 header=None,
#                 sep=",",
#                 engine="c",
#                 names=[
#                     "Row Type",
#                     "Variable Name",
#                     "Attribute Name",
#                     "Data Type",
#                     "Value",
#                 ],
#             ).fillna("nan")
#             for index1, row1 in get_info.iterrows():
#                 # now we create our indicators that we put in our db

#                 if row1["Row Type"] == "dimension":
#                     if dimensions > 0:
#                         dimension_names = dimension_names + " "
#                     dimensions = dimensions + 1
#                     dimension_names = dimension_names + row1["Variable Name"]

#                 if row1["Row Type"] == "variable":
#                     if variables > 0:
#                         variable_names = variable_names + " "
#                     variables = variables + 1
#                     variable_names = variable_names + row1["Variable Name"]

#                 if row1["Attribute Name"] == "adriaclim_dataset":
#                     adriaclim_dataset = row1["Value"]
#                 if row1["Attribute Name"] == "adriaclim_model":
#                     adriaclim_model = row1["Value"]
#                 if row1["Attribute Name"] == "adriaclim_scale":
#                     adriaclim_scale = row1["Value"]
#                 if row1["Attribute Name"] == "adriaclim_timeperiod":
#                     adriaclim_timeperiod = row1["Value"]
#                 if row1["Attribute Name"] == "adriaclim_type":
#                     adriaclim_type = row1["Value"]
#                 if row1["Attribute Name"] == "title":
#                     title = row1["Value"]
#                 if row1["Attribute Name"] == "institution":
#                     institution = row1["Value"]
#                 if row1["Attribute Name"] == "time_coverage_start":
#                     time_start = row1["Value"]
#                 if row1["Attribute Name"] == "time_coverage_end":
#                     time_end = row1["Value"]
#                 if row1["Attribute Name"] == "geospatial_lat_min":
#                     lat_min = row1["Value"]
#                 if row1["Attribute Name"] == "geospatial_lat_max":
#                     lat_max = row1["Value"]
#                 if row1["Attribute Name"] == "geospatial_lon_min":
#                     lng_min = row1["Value"]
#                 if row1["Attribute Name"] == "geospatial_lon_max":
#                     lng_max = row1["Value"]


#             if adriaclim_scale is None:
#                 adriaclim_scale = "large"

#             if adriaclim_model is None:
#                 adriaclim_model = "UNKNOWN"

#             if adriaclim_type is None:
#                 adriaclim_type = "UNKNOWN"

#             if adriaclim_dataset is None:
#                 adriaclim_dataset = "indicator"


#             if adriaclim_timeperiod is None:
#                 if "yearly" in row["Title"].lower():
#                     adriaclim_timeperiod = "yearly"
#                 if "monthly" in row["Title"].lower():
#                     adriaclim_timeperiod = "monthly"
#                 if "seasonal" in row["Title"].lower():
#                     adriaclim_timeperiod = "seasonal"
#             if adriaclim_timeperiod is None:
#                 adriaclim_timeperiod = "yearly"

#             if time_start is not None and time_end is not None:
#                 new_indicator = Indicator(
#                     dataset_id=dataset_id,
#                     adriaclim_dataset=adriaclim_dataset,
#                     adriaclim_model=adriaclim_model,
#                     adriaclim_scale=adriaclim_scale,
#                     adriaclim_timeperiod=adriaclim_timeperiod,
#                     adriaclim_type=adriaclim_type,
#                     title=row["Title"],
#                     metadata_url=metadata_url,
#                     institution=institution,
#                     lat_min=lat_min,
#                     lng_min=lng_min,
#                     lat_max=lat_max,
#                     lng_max=lng_max,
#                     time_start=time_start,
#                     time_end=time_end,
#                     tabledap_url=tabledap_url,
#                     dimensions=dimensions,
#                     dimension_names=dimension_names,
#                     variables=variables,
#                     variable_names=variable_names,
#                     griddap_url=griddap_url,
#                     wms_url=row["wms"],
#                 )
#                 new_indicator.save()
#                 indicator_list.append(new_indicator.title)
#                 dataset_list.append(adriaclim_dataset)
#                 scale_list.append(adriaclim_scale)

#     print(
#         "Time to finish getIndicators() ========= {:.2f} seconds".format(
#             time.time() - start_time
#         )
#     )
#     return [indicator_list, dataset_list, scale_list]


# def download_big_data(timeperiod):
#     start_effettivo = time.time()
#     all_datasets = Node.objects.filter(Q(adriaclim_dataset="indicator") & Q(adriaclim_timeperiod=timeperiod))[:2]
#     for dataset in all_datasets:
#         start_time = time.time()
#         print("Sono iniziata ora final version!!!")
#         url_csv = ""
#         if dataset.griddap_url != "":
#             # https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/MedCordex_IPSL_bda7_23d0_0f98.csv?consecutive_summer_days_index_per_time_period%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,number_of_csu_periods_with_more_than_5days_per_time_period%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,fg%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,heat_wave_duration_index_wrt_mean_of_reference_period%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,heat_waves_per_time_period%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,summer_days_index_per_time_period%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,tg%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,tropical_nights_index_per_time_period%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,txn%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D,txx%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(46.88878):1:(37.28878)%5D%5B(10.24039):1:(21.66346)%5D
#             # https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/WAVES_VTM10_5da8_8ef6_cf64
#             url_csv += dataset.griddap_url + ".csv?"
#             variable_names = dataset.variable_names.split(" ")
#             for index, var in enumerate(variable_names):
#                 if dataset.dimensions > 3:
#                     if index < len(variable_names) - 1:
#                         # https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/atm_regional_1f91_1673_845b.htmlTable?vegetfrac%5B(2005-11-20T00:00:00Z):1:(2005-11-20T00:00:00Z)%5D%5B(1.0):1:(13.0)%5D%5B(90.0):1:(-90.0)%5D%5B(-171.2326):1:(180.4572)%5D
#                         url_csv += (
#                             var
#                             + "%5B("
#                             + dataset.time_start
#                             + "):1:("
#                             + dataset.time_end
#                             + ")%5D%5B("
#                             + str(dataset.param_min)
#                             + "):1:("
#                             + str(dataset.param_max)
#                             + ")%5D%5B("
#                             + dataset.lat_max
#                             + "):1:("
#                             + dataset.lat_min
#                             + ")%5D%5B("
#                             + dataset.lng_min
#                             + "):1:("
#                             + dataset.lng_max
#                             + ")%5D,"
#                         )
#                     else:
#                         url_csv += (
#                             var
#                             + "%5B("
#                             + dataset.time_start
#                             + "):1:("
#                             + dataset.time_end
#                             + ")%5D%5B("
#                             + str(dataset.param_min)
#                             + "):1:("
#                             + str(dataset.param_max)
#                             + ")%5D%5B("
#                             + dataset.lat_max
#                             + "):1:("
#                             + dataset.lat_min
#                             + ")%5D%5B("
#                             + dataset.lng_min
#                             + "):1:("
#                             + dataset.lng_max
#                             + ")%5D"
#                         )

#                 else:
#                     #niente param aggiuntivo
#                     if index < len(variable_names) - 1:
#                         url_csv += (
#                             var
#                             + "%5B("
#                             + dataset.time_start
#                             + "):1:("
#                             + dataset.time_end
#                             + ")%5D%5B("
#                             + dataset.lat_max
#                             + "):1:("
#                             + dataset.lat_min
#                             + ")%5D%5B("
#                             + dataset.lng_min
#                             + "):1:("
#                             + dataset.lng_max
#                             + ")%5D,"
#                         )
#                     else:
#                         url_csv += (
#                             var
#                             + "%5B("
#                             + dataset.time_start
#                             + "):1:("
#                             + dataset.time_end
#                             + ")%5D%5B("
#                             + dataset.lat_max
#                             + "):1:("
#                             + dataset.lat_min
#                             + ")%5D%5B("
#                             + dataset.lng_min
#                             + "):1:("
#                             + dataset.lng_max
#                             + ")%5D"
#                         )


#             # print("url_csv=======", url_csv)
#             generic_big_data_download(url_csv,dataset,dataset.variables,False)

#         else:
#             #siamo nel caso di tabledap!
#             url_csv += dataset.tabledap_url + ".csv?"
#             variable_names = dataset.variable_names.split(" ")
#             for index, var in enumerate(variable_names):
#                 if index < len(variable_names) - 1:
#                     url_csv += var + "%2C"
#                 else:
#                     url_csv += var + "&"

#             url_csv += (
#                 "time%3E="
#                 + dataset.time_start
#                 + "&time%3C="
#                 + dataset.time_end
#                 + "&latitude%3E="
#                 + dataset.lat_min
#                 + "&latitude%3C="
#                 + dataset.lat_max
#                 + "&longitude%3E="
#                 + dataset.lng_min
#                 + "&longitude%3C="
#                 + dataset.lng_max
#             )
#             # print("url_csv=======", url_csv)
#             generic_big_data_download(url_csv,dataset,dataset.variables,True)
            
#         print("TIME FOR A DATASET {:.2f} seconds".format(time.time() - start_time))

#     print("TIME FOR DOWNLOAD BIG DATA {:.2f} seconds".format(time.time() - start_effettivo))


# def getWMS():
#     url_datasets = ERDDAP_URL + "/info/index.csv?page=1&itemsPerPage=1000000000"
#     df = pd.read_csv(
#         url_datasets,
#         header=None,
#         sep=",",
#         names=[
#             "griddap",
#             "subset",
#             "tabledap",
#             "Make A Graph",
#             "wms",
#             "files",
#             "Title",
#             "Summary",
#             "FGDC",
#             "ISO 19115",
#             "Info",
#             "Background Info",
#             "RSS",
#             "Email",
#             "Institution",
#             "Dataset ID",
#         ],
#         na_values="",
#     )
#     df1 = df.replace(np.nan, "", regex=True)
#     wmsList = []
#     for index, row in df1.iterrows():
#         wmsList.append(row["wms"])

#     return wmsList


# def getDataTableIndicator(
#     dataset_id,
#     layer_name,
#     time_start,
#     time_finish,
#     lat_start,
#     lat_end,
#     long_start,
#     long_end,
#     num_parameters,
#     range_value,
# ):
#     url = url_is_indicator(
#         "true",
#         True,
#         False,
#         dataset_id=dataset_id,
#         layer_name=layer_name,
#         time_start=time_start,
#         time_finish=time_finish,
#         latMin=lat_start,
#         longMin=long_start,
#         latMax=lat_end,
#         longMax=long_end,
#         num_parameters=num_parameters,
#         range_value=range_value,
#     )
#     print(url)
#     url = getIndicatorQueryUrl(
#         dataset_id,
#         False,
#         False,
#         latitude=latitude,
#         longitude=longitude,
#         timeMin=time_start,
#         timeMax=time_finish,
#         range=range_value,
#         format="json",
#     )
#     # https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/indicators_wsdi_aba0_0062_8939.csv?time%2Clatitude%2Clongitude%2Cwsdi&time%3E=2021-07-01&time%3C=2050-07-01&latitude%3E=39.688777923584&latitude%3C=41.22824901518532&longitude%3E=14.740385055542&longitude%3C=15.183105468750002
#     r = requests.get(url=url)
#     data = r.json()
#     return data


# def getDataTable(
#     dataset_id,
#     layer_name,
#     time_start,
#     time_finish,
#     latitude,
#     longitude,
#     num_parameters,
#     range_value,
# ):
#     try:
        
#         url = getIndicatorQueryUrl(
#             dataset_id,
#             False,
#             False,
#             latitude=str(latitude),
#             longitude=str(longitude),
#             timeMin=str(time_start),
#             timeMax=str(time_finish),
#             range=str(range_value),
#             format="json",
#             variable=str(layer_name),
#         )
#         print("URL SUPER FUNZIONE =", url)
#         r = requests.get(url=url)
#         data = r.json()
#         return data

#     except Exception as e:
#         print("EXEPTION =", e)
#         return "fuoriWms"

# def generic_big_data_download(url_dataset,dataset,num_variables,is_tabledap):
#     deletePoly("Polygon",id=dataset)
#     if is_tabledap:
#         dtypes = {'date_value': 'string', 'latitude': 'float32', 'longitude': 'float32'}
#         names = ['date_value', 'latitude', 'longitude']
#         chunksize = 10**6
#         variable_names = dataset.variable_names.split(" ")
#         if dataset.variables > 3:
#             for index,name in enumerate(variable_names):
#                 if name != "time" and name != "latitude" and name != "longitude":
#                     dtypes["value_"+str(index)] = 'float32'
#                     names.append("value_" + str(index))
        
#         list_keys = names.copy()
#         list_keys.append("dataset_id")
#         list_keys.append("coordinate")

#         for chunk in pd.read_table(
#             url_dataset,
#             engine="c",
#             sep=",",
#             header=0,
#             chunksize=chunksize,
#             low_memory=False,
#             names=names
#         ):
        

#             chunk.drop(index=chunk.index[0], axis=0, inplace=True)
#             chunk = chunk.astype(dtypes)
#             chunk["dataset_id"] = dataset.id
#             chunk_geo = gpd.GeoDataFrame(chunk, geometry=gpd.points_from_xy(chunk.latitude, chunk.longitude), crs="EPSG:4326")
#             chunk_geo['coordinate'] = chunk_geo['geometry'].apply(lambda p: Point(p.y,p.x,srid=4326))
#             # chunk_geo = chunk_geo.rename(columns={'geometry':'coordinate'})
#             chunk_geo = chunk_geo.drop(columns=['geometry'])
#             chunk_geo["coordinate"] = chunk_geo["coordinate"].apply(lambda p: p.wkt)

#             csv_data = chunk_geo.to_csv(index=False)
#             csv_file = io.StringIO(csv_data)

                        
#             mapping = {
#                 name: name.lower()
#                 for name in list_keys
#             }

#             try:
#                 if not is_database_almost_full():

#                     Polygon.copy_manager.from_csv(
#                         csv_file,
#                         mapping,
                    
#                     )
                    

#             except Exception as e:
#                 print("Eccezione", e)
#                 return str(e)
#     else:
#         #siamo nel caso di griddap
#         dtypes = {'date_value': 'string', 'latitude': 'float32', 'longitude': 'float32'}
#         names = ['date_value', 'latitude', 'longitude']
        
#         dimensions = dataset.dimension_names.split(" ")
#         if dataset.dimensions > 3:
#             for name in dimensions:
#                 if name != "time" and name != "latitude" and name != "longitude":
#                     dtypes[name] = 'float32'
#                     names.append(name)
        
#         for i in range(0,num_variables):
#             dtypes["value_" + str(i)] = 'float32'
#             names.append("value_" + str(i))
        
#         list_keys = names.copy()
#         list_keys.append("dataset_id") 
#         list_keys.append("coordinate")

#         chunksize = 10**6
#         for chunk in pd.read_table(
#             url_dataset,
#             engine="c",
#             sep=",",
#             header=0,
#             chunksize=chunksize,
#             low_memory=False,
#             names=names
#         ):

#             chunk.drop(index=chunk.index[0], axis=0, inplace=True)
#             chunk = chunk.astype(dtypes)
#             chunk["dataset_id"] = dataset.id 
#             chunk_geo = gpd.GeoDataFrame(chunk, geometry=gpd.points_from_xy(chunk.latitude, chunk.longitude), crs="EPSG:4326")
#             chunk_geo['coordinate'] = chunk_geo['geometry'].apply(lambda p: Point(p.y,p.x,srid=4326))
#             chunk_geo = chunk_geo.drop(columns=['geometry'])
#             chunk_geo["coordinate"] = chunk_geo["coordinate"].apply(lambda p: p.wkt)
#             csv_data = chunk_geo.to_csv(index=False)
#             csv_file = io.StringIO(csv_data)
            

#             mapping = {
#                 name: name.lower()
#                 for name in list_keys
#             }

#             try:
#                 if not is_database_almost_full():
#                     Polygon.copy_manager.from_csv(
#                         csv_file,
#                         mapping,
#                     )
                
#             except Exception as e:
#                 print("Eccezione", e)
#                 return str(e)

# def deletePoly(param, **kwargs):
#     # print("PARAM =", par)
#     if param == "Node":
#         Node.objects.all().delete()
#     elif param == "Polygon":
#         obj = Polygon.objects.filter(dataset_id=kwargs["id"])
#         obj.delete()


# def getDataVectorial(
#     dataset_id,
#     layer_name,
#     date_start,
#     latitude_start,
#     latitude_end,
#     longitude_start,
#     longitude_end,
#     num_param,
#     range_value,
#     is_indicator,
# ):
    
#     try:
#         # print("DATASET ID =", dataset_id)
#         # print("LAYER NAME =", layer_name)
#         # print("DATE START =", date_start)
#         # print("LATITUDE START =", latitude_start)
#         # print("LATITUDE END =", latitude_end)
#         # print("LONGITUDE START =", longitude_start)
#         # print("LONGITUDE END =", longitude_end)
#         # print("NUM PARAM =", num_param)
#         # print("RANGE VALUE =", range_value)
#         # print("IS INDICATOR =", is_indicator)
#         # https://erddap.cmcc-opa.eu/erddap/tabledap/ARPAE_f903_2ae5_11cb.htmlTable?time%2Clatitude%2Clongitude%2Ca_95_BO_9_m&time%3E=2022-11-24&time%3C=2022-12-01&latitude%3E=44.214583&latitude%3C=44.214583&longitude%3E=12.47585&longitude%3C=12.47585
#         url = url_is_indicator(
#             is_indicator,
#             False,
#             True,
#             dataset_id=dataset_id,
#             layer_name=layer_name,
#             date_start=date_start,
#             latitude_start=latitude_start,
#             latitude_end=latitude_end,
#             longitude_start=longitude_start,
#             longitude_end=longitude_end,
#             num_param=num_param,
#             range_value=range_value,
#         )
#         print("LAYER NAME =", layer_name)
#         print("URL =", url)
#         start_time = time.time()
#         df = pd.read_csv(url, dtype="unicode")
#         print("DATAFRAME =", df)
#         allData = []
#         values = []
#         lat_coordinates = []
#         long_coordinates = []
#         df = df.dropna(how="any", axis=0) # per la seconda prova la riga è da scommentare
#         # df = df.dropna(subset=[layer_name])
#         i = 0
#         for index, row in df.iterrows():

#             try:
#                 value = float(row[layer_name])
#             except ValueError:
#                 value = 0.0

#             values.insert(i, value)

#             # values.insert(i, row[layer_name])
#             lat_coordinates.insert(i, row["latitude"])
#             long_coordinates.insert(i, row["longitude"])
#             i += 1
        
#         if values:
#             value_min = min(values)
#             value_max = max(values)
#         else:
#             value_min = 0.0 # valore predefinito se non ci sono valori validi
#             value_max = 0.0 # valore predefinito se non ci sono valori validi

#         # per la seconda prova questi if sono da commentare
#         # if 'degrees_north' in lat_coordinates:
#         #     lat_coordinates.remove('degrees_north')
#         # if 'degrees_east' in long_coordinates:
#         #     long_coordinates.remove('degrees_east')
            
#         allData = [values, lat_coordinates, long_coordinates, value_min, value_max]

#         return allData
#     except Exception as e:
#         print("ECCEZIONE VETTORIALE", e)
#         return str(e)


# def listAllDatasets():
#     url_datasets = ERDDAP_URL + "/info/index.csv?page=1&itemsPerPage=1000000000"
#     url_open = urllib.request.urlopen(url_datasets)
#     csvfile = csv.DictReader(
#         io.TextIOWrapper(url_open, encoding="utf-8"), delimiter=","
#     )
#     return csvfile








