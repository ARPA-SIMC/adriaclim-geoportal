from celery import shared_task,chain



@shared_task
def task_get_all_data():
    from myFunctions import allFunctions
    # print("get_all_datasets!")
    # Call your function here
    allFunctions.getAllDatasets()


@shared_task
def download_big_data_yearly():
    from myFunctions import allFunctions
    # print("yearly!")
    # Call your function here
    allFunctions.download_big_data("yearly")

@shared_task
def download_big_data_seasonal():
    from myFunctions import allFunctions
    #print("shared_task!")
    # print("seasonal")
    # Call your function here
    allFunctions.download_big_data("seasonal")

@shared_task
def download_big_data_monthly():
    from myFunctions import allFunctions
    #print("shared_task!")
    # print("monthly")
    # Call your function here
    allFunctions.download_big_data("monthly")

@shared_task
def download_all_data():
    #from myFunctions import allFunctions
    # print("shared_task!")
    # Call your function here
    ch = chain(download_big_data_yearly(),download_big_data_seasonal(),download_big_data_monthly())()

@shared_task
def task_get_data_polygon(request_data):
    try:
        from myFunctions import allFunctions
        from django.http.response import JsonResponse
        print("REQUEST DATA CELERY =", request_data)
        dataset = request_data["dataset"]
        print("DATASET:",dataset)
        # print("DATASET ID:",dataset.get('id'))
        dataset_id = request_data["dataset"]['id']
        date_start = request_data["dataset"]['time_start']
        date_end = request_data["dataset"]['time_end']
        layer_name = request_data['selVar']
        print("LAYER NAME:",layer_name)
        range = str(request_data['range'])
        num_param = request_data["dataset"]['dimensions']
        parametro_agg = str(request_data['parametro_agg'])
        print("PARAMETRO AGG:",parametro_agg)
        lat_min = request_data["dataset"]['lat_min']
        lat_max = request_data["dataset"]['lat_max']
        lng_min = request_data["dataset"]['lng_min']
        lng_max = request_data["dataset"]['lng_max']
        time_op = request_data['operation']
        statistic = request_data['statistic']
        circle_coords = request_data['circleCoords']
        print("CIRCLE_COORDS",circle_coords)
        print("STATISTIC:",statistic)
        print("time_op:",time_op)
        lat_lng_obj = request_data['latLngObj']
        print("LAT LNG OBJ: ", lat_lng_obj)
        is_indicator = request_data['isIndicator']
        print("IS INDICATOR:",is_indicator)
        allFunctions.getDataPolygonNew(dataset_id,layer_name,date_start,date_end,lat_lng_obj,statistic,time_op,num_param,range,is_indicator,lat_min,lat_max,lng_min,lng_max,parametro_agg,circle_coords)
    except Exception as e:
        print("eccezione task",e)
        return str(e)
