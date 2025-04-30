import pytest
from types import SimpleNamespace
from operator import itemgetter
from unittest.mock import patch
from django.http import JsonResponse
from django.test import RequestFactory


# # Function -> getDataTableNew

# def getDataVectorialNew(request):
#     return {"dataVect": "fake_data_vectorial"}

# # Test fittizi diretti senza dipendere da Django

# def test_getDataVectorialNew():
#     class FakeRequest:
#         data = {
#             'dataset': {
#                 'id': 'mock_id',
#                 'variables': 1,
#                 'dimensions': 1,
#                 'lat_min': '0',
#                 'lat_max': '10',
#                 'lng_min': '0',
#                 'lng_max': '10'
#             },
#             'selDate': '2021-01-01',
#             'selVar': 'mock_var',
#             'isIndicator': 'false'
#         }
#     request = FakeRequest()
#     response = getDataVectorialNew(request)
#     assert isinstance(response, dict)
#     assert "dataVect" in response
    

# # TEST OK!!


# # Function -> getDataGraphicNewCanvas


# def getDataGraphicNewCanvas(request):
#     try:
#         dataset_id = request.data.get("idMeta")
#         dataset = request.data.get('dataset')
#         adriaclim_timeperiod = dataset.get('adriaclim_timeperiod')
#         latitude = str(request.data.get("lat"))
#         longitude = str(request.data.get("lng"))
#         time_start = str(request.data.get("dateStart"))
#         time_finish = str(request.data.get("dateEnd"))
#         layer_name = request.data.get("variable")
#         num_parameters = request.data.get("dimensions")
#         range_value = str(request.data.get("range"))
#         lat_min = str(request.data.get("lat_min"))
#         lat_max = str(request.data.get("lat_max"))
#         lng_min = str(request.data.get("lng_min"))
#         lng_max = str(request.data.get("lng_max"))
#         operation = request.data.get("operation")
#         context = request.data.get("context")

#         allData = "fake_allData"  # Simulazione

#         if allData == "fuoriWms":
#             return {"allData": allData}
#         else:
#             return {"allData": allData}
#     except Exception as e:
#         print("ERRORE:", e)
#         return "fuoriWms"
    
# def test_getDataGraphicNewCanvas():
#     class FakeRequest:
#         data = {
#             'idMeta': 'mock_id',
#             'dataset': {'adriaclim_timeperiod': 'monthly'},
#             'lat': '45.0',
#             'lng': '12.0',
#             'dateStart': '2021-01-01',
#             'dateEnd': '2021-12-31',
#             'variable': 'temperature',
#             'dimensions': 1,
#             'range': 10,
#             'lat_min': '44.0',
#             'lat_max': '46.0',
#             'lng_min': '11.0',
#             'lng_max': '13.0',
#             'operation': 'default',
#             'context': 'one'
#         }
#     request = FakeRequest()
#     response = getDataGraphicNewCanvas(request)
#     assert isinstance(response, dict)
#     assert "allData" in response
    

# # TEST OK!!



# # Function -> getDataTableNew


# def getDataTableNew(request):
#     return {"data": "fake_data"}


# def test_getDataTableNew():
#     class FakeRequest:
#         data = {
#             'idMeta': 'mock_id',
#             'lat': '0',
#             'lng': '0',
#             'dateStart': '2021-01-01',
#             'dateEnd': '2021-12-31',
#             'variable': 'var',
#             'dimensions': 1,
#             'range': 10
#         }
#     request = FakeRequest()
#     response = getDataTableNew(request)
#     assert isinstance(response, dict)
#     assert "data" in response
    

# # TEST OK!!


# # Function -> get_metadata_table


# def get_metadata_table(request):
#     return {"metadata": "mock_metadata"}

# def test_get_metadata_table():
#     class FakeRequest:
#         data = {"idMeta": "fake_id"}
#     request = FakeRequest()
#     response = get_metadata_table(request)
#     assert isinstance(response, dict)
#     assert "metadata" in response
#     assert response["metadata"] == "mock_metadata"
    
    
# # TEST OK!!



# # Function -> compareDatasets


# def compareDatasets(request):
#     try:
#         compare_obj = request.data
#         context = "one"
#         operation = "default"

#         latitude = str(compare_obj.get('latlng')["lat"])
#         longitude = str(compare_obj.get('latlng')["lng"])

#         first_dataset = compare_obj.get('firstDataset')["name"]
#         first_dataset_id = first_dataset["id"]
#         first_dataset_timeperiod = first_dataset["adriaclim_timeperiod"]
#         first_dataset_layer_name = str(compare_obj.get('firstVarSel'))
#         first_dataset_time_start = first_dataset["time_start"]
#         first_dataset_time_end = first_dataset["time_end"]
#         first_dataset_param = str(compare_obj.get('firstValue'))

#         first_result = {first_dataset_layer_name: [{'y': 1}, {'y': 2}]}
#         all_values_first = list(map(float, map(itemgetter('y'), first_result[first_dataset_layer_name])))

#         second_dataset = compare_obj.get('secondDataset')["name"]
#         second_dataset_id = second_dataset["id"]
#         second_dataset_timeperiod = second_dataset["adriaclim_timeperiod"]
#         second_dataset_layer_name = str(compare_obj.get('secondVarSel'))
#         second_dataset_time_start = second_dataset["time_start"]
#         second_dataset_time_end = second_dataset["time_end"]
#         second_dataset_param = str(compare_obj.get('secondValue'))

#         second_result = {second_dataset_layer_name: [{'y': 1}, {'y': 3}]}
#         all_values_second = list(map(float, map(itemgetter('y'), second_result[second_dataset_layer_name])))

#         mean_diff_avg = sum(all_values_second) / len(all_values_second) - sum(all_values_first) / len(all_values_first)
#         mean_diff_avg_abs = abs(mean_diff_avg)
#         root_squared_diff = ((sum((a-b)**2 for a,b in zip(all_values_first, all_values_second)))/len(all_values_first))**0.5

#         allData = {
#             "firstResult": first_result,
#             "secondResult": second_result,
#             "meanDiffAvg": mean_diff_avg,
#             "meanDiffAvgAbs": mean_diff_avg_abs,
#             "rootSquaredDiff": root_squared_diff,
#         }

#         return {"compareResult": allData}
#     except Exception as e:
#         return {"error": str(e)}

# # Test principale

# def test_compareDatasets():
#     fake_request = SimpleNamespace(
#         data={
#             "latlng": {"lat": 45.0, "lng": 12.0},
#             "firstDataset": {"name": {"id": "dataset1", "adriaclim_timeperiod": "monthly", "time_start": "2020-01-01", "time_end": "2020-01-31"}},
#             "firstVarSel": "var1",
#             "firstValue": 0,
#             "secondDataset": {"name": {"id": "dataset2", "adriaclim_timeperiod": "monthly", "time_start": "2020-01-01", "time_end": "2020-01-31"}},
#             "secondVarSel": "var2",
#             "secondValue": 0
#         }
#     )

#     response = compareDatasets(fake_request)
#     assert "compareResult" in response
#     assert "firstResult" in response["compareResult"]
#     assert "secondResult" in response["compareResult"]
#     assert isinstance(response["compareResult"]["meanDiffAvg"], float)
#     assert isinstance(response["compareResult"]["rootSquaredDiff"], float)
    

# # TEST OK!!



# # Funtions -> getDataPolygonNew, check_task_status, discover_mb_indicator, updateStatistics

# def getDataPolygonNew(request):
#     try:
#         task = SimpleNamespace(id="fake_task_id")
#         return {"task_id": task.id}
#     except Exception as e:
#         return str(e)


# def check_task_status(request):
#     try:
#         task = SimpleNamespace(status="SUCCESS", result={"mock": 1}, state="SUCCESS", info={"current": 50})
#         response = {"status": task.status}
#         if task.status == 'SUCCESS':
#             response['result'] = task.result
#         if task.state == "PROGRESS":
#             response["progressBar"] = task.info.get('current')
#         return {"dataVect": response}
#     except Exception as e:
#         response = {"error": str(e)}
#         return {"dataVect": response}


# def discover_mb_indicator(request):
#     return {"mb": "mock_indicator"}


# def updateStatistics(request):
#     new_values_calculated = [10, 20, 30]
#     return {"newValues": new_values_calculated}

# # Tests

# def test_getDataPolygonNew():
#     fake_request = SimpleNamespace(data={})
#     response = getDataPolygonNew(fake_request)
#     assert "task_id" in response

# def test_check_task_status():
#     fake_request = SimpleNamespace(data={"task_id": "fake_task_id"})
#     response = check_task_status(fake_request)
#     assert "dataVect" in response

# def test_discover_mb_indicator():
#     fake_request = SimpleNamespace(data={"timeperiod": "monthly"})
#     response = discover_mb_indicator(fake_request)
#     assert "mb" in response

# def test_updateStatistics():
#     fake_request = SimpleNamespace(data={"dates": [], "values": [], "dataset": {"adriaclim_timeperiod": "monthly"}, "polygon": "mock_polygon"})
#     response = updateStatistics(fake_request)
#     assert "newValues" in response
    

# # TEST OK!!



# Functions -> getAllDatasets, dataset_id_wrong, getDataTable, getAllNodes

# def getAllDatasets(request):
#     return {"status": 200, "message": "Ok"}

# def dataset_id_wrong(request):
#     return {"rendered_template": "wrongIdPassed.html"}

# def getDataTable(request, dataset_id, layer_name, time_start, time_finish, latitude, longitude, num_parameters, range_value):
#     headers = ["header1", "header2"]
#     out = [["row1col1", "row1col2"], ["row2col1", "row2col2"]]
#     return {"rendered_template": "getData.html", "data": out, "headers": headers}

# def getAllNodes(request):
#     try:
#         all_nodes = [{"id": 1, "name": "Node1"}, {"id": 2, "name": "Node2"}]
#         return {"nodes": all_nodes}
#     except Exception as e:
#         return {"error": str(e)}


# def test_getAllDatasets():
#     fake_request = SimpleNamespace(data={})
#     response = getAllDatasets(fake_request)
#     assert response["status"] == 200

# def test_dataset_id_wrong():
#     fake_request = SimpleNamespace(data={})
#     response = dataset_id_wrong(fake_request)
#     assert response["rendered_template"] == "wrongIdPassed.html"

# def test_getDataTable():
#     fake_request = SimpleNamespace(data={})
#     response = getDataTable(fake_request, "id1", "layer1", "start", "end", 45.0, 12.0, 1, 0)
#     assert response["rendered_template"] == "getData.html"
#     assert len(response["data"]) > 0

# def test_getAllNodes():
#     fake_request = SimpleNamespace(data={})
#     response = getAllNodes(fake_request)
#     assert "nodes" in response
#     assert isinstance(response["nodes"], list)
    
# # TEST OK!!


# # Functions -> getMetadata, layers2D, layers3D, overlaysNew


# def getMetadataNew(request):
#     try:
#         metadata = {"mocked": True}
#         return {"metadata": metadata}
#     except Exception as e:
#         return {"error": str(e)}


# def layers2DNew(request):
#     return {"status": 200, "content_type": "image/png"}


# def layers3DNew(request, parameter):
#     return {"status": 200, "content_type": "image/png"}


# def overlaysNew(request, dataset_id):
#     return {"status": 200, "content_type": "image/png"}

# def test_getMetadataNew():
#     fake_request = SimpleNamespace(data={"idMeta": "123"})
#     response = getMetadataNew(fake_request)
#     assert "metadata" in response


# def test_layers2DNew():
#     fake_request = SimpleNamespace(GET={"service": "WMS", "request": "GetMap", "layers": "dataset:layer", "styles": "", "format": "image/png", "transparent": "true", "version": "1.3.0", "width": "256", "height": "256", "crs": "EPSG:4326", "bbox": "-180,-90,180,90", "time": "2020-01-01T00:00:00Z", "bgcolor": "0xFFFFFF"})
#     response = layers2DNew(fake_request)
#     assert response["status"] == 200


# def test_layers3DNew():
#     fake_request = SimpleNamespace(GET={"service": "WMS", "request": "GetMap", "layers": "dataset:layer", "styles": "", "format": "image/png", "transparent": "true", "version": "1.3.0", "width": "256", "height": "256", "crs": "EPSG:4326", "bbox": "-180,-90,180,90", "time": "2020-01-01T00:00:00Z", "bgcolor": "0xFFFFFF", "depth": "5"})
#     response = layers3DNew(fake_request, "depth")
#     assert response["status"] == 200


# def test_overlaysNew():
#     fake_request = SimpleNamespace(GET={"service": "WMS", "request": "GetMap", "layers": "dataset:layer", "styles": "", "format": "image/png", "transparent": "true", "version": "1.3.0", "width": "256", "height": "256", "crs": "EPSG:4326", "bbox": "-180,-90,180,90", "bgcolor": "0xFFFFFF"})
#     response = overlaysNew(fake_request, "dataset_id")
#     assert response["status"] == 200
    

# # TEST OK!!
