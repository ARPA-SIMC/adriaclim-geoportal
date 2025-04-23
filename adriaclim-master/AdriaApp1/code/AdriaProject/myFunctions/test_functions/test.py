
# import pytest
# from unittest.mock import patch
# import urllib.request
# import io


# # Function -> download_with_cache.py
# _fake_cache = {}

# def fake_cache_get(key):
#     return _fake_cache.get(key)

# def fake_cache_set(key, value, timeout=None):
#     _fake_cache[key] = value

# def download_with_cache(u):
#     cache_key = u
#     cache_time = 43200
#     output_value = fake_cache_get(cache_key)
#     if output_value is None:
#         try:
#             output_value = urllib.request.urlopen(cache_key).read()
#         except Exception:
#             return "fuoriWms"
#         if output_value:
#             output_value = output_value.decode("utf-8")
#             fake_cache_set(cache_key, output_value, cache_time)
#             return output_value
#     else:
#         return output_value

# @patch("urllib.request.urlopen")
# def test_download_with_cache_fetches_and_caches_data(mock_urlopen):
#     _fake_cache.clear()
#     mock_urlopen.return_value.read.return_value = b"mocked response"
#     url = "http://example.com/test"
#     result = download_with_cache(url)
#     assert result == "mocked response"
#     assert _fake_cache[url] == "mocked response"

# @patch("urllib.request.urlopen")
# def test_download_with_cache_uses_cached_data(mock_urlopen):
#     _fake_cache.clear()
#     url = "http://example.com/test"
#     _fake_cache[url] = "cached response"
#     result = download_with_cache(url)
#     assert result == "cached response"
#     mock_urlopen.assert_not_called()

# @patch("urllib.request.urlopen")
# def test_download_with_cache_handles_fetch_error(mock_urlopen):
#     _fake_cache.clear()
#     mock_urlopen.side_effect = Exception("Network error")
#     url = "http://example.com/test"
#     result = download_with_cache(url)
#     assert result == "fuoriWms"
    
# # TEST OK!

# # Function -> remove_from_cache.py
# _fake_cache = {}

# def fake_cache_get(key):
#     return _fake_cache.get(key)

# def fake_cache_set(key, value, timeout=None):
#     _fake_cache[key] = value

# def fake_cache_delete(key):
#     _fake_cache.pop(key, None)

# def remove_from_cache(u):
#     cache_key = u
#     output_value = fake_cache_get(cache_key)
#     if output_value:
#         if isinstance(output_value, bytes):
#             output_value = output_value.decode("utf-8")
#         fake_cache_delete(cache_key)
#         return output_value
#     else:
#         return None

# def test_remove_from_cache_removes_and_returns_value():
#     _fake_cache.clear()
#     url = "http://example.com/test"
#     _fake_cache[url] = "cached response"
#     result = remove_from_cache(url)
#     assert result == "cached response"
#     assert url not in _fake_cache

# def test_remove_from_cache_returns_none_if_not_exists():
#     _fake_cache.clear()
#     url = "http://example.com/unknown"
#     result = remove_from_cache(url)
#     assert result is None
    
# # TEST OK!


# # # Function -> download_with_cache_as_csv.py
# _fake_cache = {}

# def fake_cache_get(key):
#     return _fake_cache.get(key)

# def download_with_cache(u):
#     output_value = fake_cache_get(u)
#     if output_value is None:
#         raise Exception("No data")
#     return output_value

# def download_with_cache_as_csv(u):
#     try:
#         q = download_with_cache(u)
#         if q:
#             return io.StringIO(q)
#         else:
#             return None
#     except Exception:
#         return "fuoriWms"

# def test_download_with_cache_as_csv_returns_stringio():
#     _fake_cache.clear()
#     url = "http://example.com/data.csv"
#     _fake_cache[url] = "col1,col2\nval1,val2"
#     result = download_with_cache_as_csv(url)
#     assert isinstance(result, io.StringIO)
#     assert result.read() == "col1,col2\nval1,val2"

# def test_download_with_cache_as_csv_handles_missing_data():
#     _fake_cache.clear()
#     url = "http://example.com/missing.csv"
#     result = download_with_cache_as_csv(url)
#     assert result == "fuoriWms"

# # TEST OK!  


# _fake_cache = {}

# def fake_cache_get(key):
#     return _fake_cache.get(key)

# def download_with_cache(u):
#     output_value = fake_cache_get(u)
#     if output_value is None:
#         raise Exception("No data")
#     return output_value

# def download_with_cache_as_csv(u):
#     try:
#         q = download_with_cache(u)
#         if q:
#             return io.StringIO(q)
#         else:
#             return None
#     except Exception:
#         return "fuoriWms"

# def test_download_with_cache_as_csv_returns_stringio():
#     _fake_cache.clear()
#     url = "http://example.com/data.csv"
#     _fake_cache[url] = "col1,col2\nval1,val2"
#     result = download_with_cache_as_csv(url)
#     assert isinstance(result, io.StringIO)
#     assert result.read() == "col1,col2\nval1,val2"

# def test_download_with_cache_as_csv_handles_missing_data():
#     _fake_cache.clear()
#     url = "http://example.com/missing.csv"
#     result = download_with_cache_as_csv(url)
#     assert result == "fuoriWms"

# # Function -> getIndicator e getIndicatorBaseUrl
# class MockNode:
#     def __init__(self, id, griddap_url=None, tabledap_url=None):
#         self.id = id
#         self.griddap_url = griddap_url
#         self.tabledap_url = tabledap_url

# class MockQuerySet:
#     def __init__(self, results):
#         self.results = results

#     def count(self):
#         return len(self.results)

#     def __getitem__(self, index):
#         return self.results[index]

# # Funzioni da testare con mock

# def getIndicator(id):
#     q = MockQuerySet([node for node in _mock_db if node.id == id])
#     if q.count() == 0:
#         return None
#     else:
#         return q[0]

# def getIndicatorBaseUrl(ind):
#     if ind is None:
#         return None
#     if ind.griddap_url is not None and ind.griddap_url != "":
#         return ind.griddap_url
#     if ind.tabledap_url is not None and ind.tabledap_url != "":
#         return ind.tabledap_url
#     return None

# _mock_db = []

# def test_getIndicator_returns_node_if_exists():
#     _mock_db.clear()
#     _mock_db.append(MockNode(id=1))
#     node = getIndicator(1)
#     assert node is not None
#     assert node.id == 1

# def test_getIndicator_returns_none_if_not_found():
#     _mock_db.clear()
#     node = getIndicator(99)
#     assert node is None

# def test_getIndicatorBaseUrl_prefers_griddap():
#     node = MockNode(id=1, griddap_url="http://griddap.url", tabledap_url="http://tabledap.url")
#     assert getIndicatorBaseUrl(node) == "http://griddap.url"

# def test_getIndicatorBaseUrl_uses_tabledap_if_no_griddap():
#     node = MockNode(id=1, griddap_url=None, tabledap_url="http://tabledap.url")
#     assert getIndicatorBaseUrl(node) == "http://tabledap.url"

# def test_getIndicatorBaseUrl_returns_none_if_none():
#     node = MockNode(id=1)
#     assert getIndicatorBaseUrl(node) is None
#     assert getIndicatorBaseUrl(None) is None
# # TEST OK!

# # Function -> getIndicatorDataFormat, getIndicatorDimensions, getIndicatorVariables, getVariableAliases
# class MockIndicator:
#     def __init__(self, griddap_url=None, tabledap_url=None, dimension_names="", variable_names=""):
#         self.griddap_url = griddap_url
#         self.tabledap_url = tabledap_url
#         self.dimension_names = dimension_names
#         self.variable_names = variable_names

# def getIndicatorDataFormat(ind):
#     if ind is None:
#         return None
#     if ind.griddap_url is not None and ind.griddap_url != "":
#         return "griddap"
#     if ind.tabledap_url is not None and ind.tabledap_url != "":
#         return "tabledap"
#     return None

# def getIndicatorDimensions(ind):
#     if ind is None:
#         return None
#     return ind.dimension_names.split()

# def getIndicatorVariables(ind):
#     if ind is None:
#         return None
#     return ind.variable_names.split()

# def getVariableAliases(variable):
#     if variable == "depth":
#         return ["plev", "range"]
#     if variable == "plev":
#         return ["depth", "range"]
#     else:
#         return [variable, "range"]

# def test_getIndicatorDataFormat_griddap():
#     ind = MockIndicator(griddap_url="http://griddap.example.com")
#     assert getIndicatorDataFormat(ind) == "griddap"

# def test_getIndicatorDataFormat_tabledap():
#     ind = MockIndicator(tabledap_url="http://tabledap.example.com")
#     assert getIndicatorDataFormat(ind) == "tabledap"

# def test_getIndicatorDataFormat_none():
#     ind = MockIndicator()
#     assert getIndicatorDataFormat(ind) is None
#     assert getIndicatorDataFormat(None) is None

# def test_getIndicatorDimensions():
#     ind = MockIndicator(dimension_names="lat lon depth")
#     assert getIndicatorDimensions(ind) == ["lat", "lon", "depth"]

# def test_getIndicatorDimensions_none():
#     assert getIndicatorDimensions(None) is None

# def test_getIndicatorVariables():
#     ind = MockIndicator(variable_names="temp sal")
#     assert getIndicatorVariables(ind) == ["temp", "sal"]

# def test_getIndicatorVariables_none():
#     assert getIndicatorVariables(None) is None

# def test_getVariableAliases_depth():
#     assert getVariableAliases("depth") == ["plev", "range"]

# def test_getVariableAliases_plev():
#     assert getVariableAliases("plev") == ["depth", "range"]

# def test_getVariableAliases_other():
#     assert getVariableAliases("temp") == ["temp", "range"]
    
# # TEST OK!

# # Function -> getIndicatorQueryUrl
# class MockIndicator:
#     def __init__(self, griddap_url=None, tabledap_url=None, dimension_names="", variable_names=""):
#         self.griddap_url = griddap_url
#         self.tabledap_url = tabledap_url
#         self.dimension_names = dimension_names
#         self.variable_names = variable_names

# def getIndicatorDataFormat(ind):
#     if ind is None:
#         return None
#     if ind.griddap_url is not None and ind.griddap_url != "":
#         return "griddap"
#     if ind.tabledap_url is not None and ind.tabledap_url != "":
#         return "tabledap"
#     return None

# def getIndicatorDimensions(ind):
#     if ind is None:
#         return None
#     return ind.dimension_names.split()

# def getIndicatorVariables(ind):
#     if ind is None:
#         return None
#     return ind.variable_names.split()

# def getVariableAliases(variable):
#     if variable == "depth":
#         return ["plev", "range"]
#     if variable == "plev":
#         return ["depth", "range"]
#     else:
#         return [variable, "range"]

# def getIndicatorBaseUrl(ind):
#     if ind and ind.griddap_url:
#         return ind.griddap_url
#     if ind and ind.tabledap_url:
#         return ind.tabledap_url
#     return "0"

# def getIndicatorQueryUrl(ind, onlyFirstVariable, skipDimensions, **kwargs):
#     if isinstance(ind, str):
#         return "http://mock/"  # simplified stub for testing

#     url = getIndicatorBaseUrl(ind) or "0"
#     if "format" in kwargs:
#         url = url + "." + kwargs["format"]

#     di = getIndicatorDimensions(ind) or []
#     va = getIndicatorVariables(ind) or []

#     tipo = getIndicatorDataFormat(ind)
#     griddap = tipo == "griddap"

#     if griddap and onlyFirstVariable and len(va) > 1:
#         va = [va[0]]

#     if griddap and "variable" in kwargs:
#         va = [kwargs["variable"]]

#     if skipDimensions:
#         di = []

#     query = "?"
#     if griddap:
#         for v in va:
#             if query != "?":
#                 query += ","
#             query += v
#             for d in di:
#                 query += f"%5B({kwargs.get(d + 'Min', '0')}):1:({kwargs.get(d + 'Max', '0')})%5D"
#     else:
#         for v in va:
#             if query != "?":
#                 query += "%2C"
#             query += v
#         for d in va:
#             if d.lower() in ["time", "latitude", "longitude"]:
#                 query += f"&{d}%3E={kwargs.get(d + 'Min', '0')}"
#                 query += f"&{d}%3C={kwargs.get(d + 'Max', '0')}"

#     result = url + query
#     return result.replace("None", "0")

# def test_getIndicatorQueryUrl_griddap_basic():
#     ind = MockIndicator(griddap_url="http://griddap.example.com", dimension_names="time lat lon", variable_names="temp")
#     url = getIndicatorQueryUrl(ind, onlyFirstVariable=True, skipDimensions=False, format="json", timeMin="2020-01-01", timeMax="2020-12-31")
#     assert url.startswith("http://griddap.example.com.json?")
#     assert "temp" in url
#     assert "%5B(" in url  # encoded bracket check

# def test_getIndicatorQueryUrl_tabledap_basic():
#     ind = MockIndicator(tabledap_url="http://tabledap.example.com", variable_names="temp")
#     url = getIndicatorQueryUrl(ind, onlyFirstVariable=True, skipDimensions=True, format="csv")
#     assert url.startswith("http://tabledap.example.com.csv?")
#     assert "temp" in url

# def test_getIndicatorQueryUrl_handles_none_fields():
#     ind = MockIndicator()
#     url = getIndicatorQueryUrl(ind, onlyFirstVariable=True, skipDimensions=True)
#     assert url.startswith("0?")

# # TEST OK!!

# # Function -> getIndicatorQueryUrlPoint
# class MockIndicator:
#     def __init__(self, griddap_url=None, tabledap_url=None, dimension_names="", variable_names=""):
#         self.griddap_url = griddap_url
#         self.tabledap_url = tabledap_url
#         self.dimension_names = dimension_names
#         self.variable_names = variable_names

# def getIndicatorDataFormat(ind):
#     if ind is None:
#         return None
#     if ind.griddap_url is not None and ind.griddap_url != "":
#         return "griddap"
#     if ind.tabledap_url is not None and ind.tabledap_url != "":
#         return "tabledap"
#     return None

# def getIndicatorDimensions(ind):
#     if ind is None:
#         return None
#     return ind.dimension_names.split()

# def getIndicatorVariables(ind):
#     if ind is None:
#         return None
#     return ind.variable_names.split()

# def getVariableAliases(variable):
#     if variable == "depth":
#         return ["plev", "range"]
#     if variable == "plev":
#         return ["depth", "range"]
#     else:
#         return [variable, "range"]

# def getIndicatorBaseUrl(ind):
#     if ind and ind.griddap_url:
#         return ind.griddap_url
#     if ind and ind.tabledap_url:
#         return ind.tabledap_url
#     return "0"

# def getIndicatorQueryUrl(ind, onlyFirstVariable, skipDimensions, **kwargs):
#     if isinstance(ind, str):
#         return "http://mock/"  # simplified stub for testing

#     url = getIndicatorBaseUrl(ind) or "0"
#     if "format" in kwargs:
#         url = url + "." + kwargs["format"]

#     di = getIndicatorDimensions(ind) or []
#     va = getIndicatorVariables(ind) or []

#     tipo = getIndicatorDataFormat(ind)
#     griddap = tipo == "griddap"

#     if griddap and onlyFirstVariable and len(va) > 1:
#         va = [va[0]]

#     if griddap and "variable" in kwargs:
#         va = [kwargs["variable"]]

#     if skipDimensions:
#         di = []

#     query = "?"
#     if griddap:
#         for v in va:
#             if query != "?":
#                 query += ","
#             query += v
#             for d in di:
#                 query += f"%5B({kwargs.get(d + 'Min', '0')}):1:({kwargs.get(d + 'Max', '0')})%5D"
#     else:
#         for v in va:
#             if query != "?":
#                 query += "%2C"
#             query += v
#         for d in va:
#             if d.lower() in ["time", "latitude", "longitude"]:
#                 query += f"&{d}%3E={kwargs.get(d + 'Min', '0')}"
#                 query += f"&{d}%3C={kwargs.get(d + 'Max', '0')}"

#     result = url + query
#     return result.replace("None", "0")

# def getIndicatorQueryUrlPoint(ind, onlyFirstVariable, skipDimensions, lat, lon, time, range, **kwargs):
#     return getIndicatorQueryUrl(
#         ind,
#         onlyFirstVariable,
#         skipDimensions,
#         latitude=lat,
#         longitude=lon,
#         time=time,
#         range=range,
#     )

# def test_getIndicatorQueryUrl_griddap_basic():
#     ind = MockIndicator(griddap_url="http://griddap.example.com", dimension_names="time lat lon", variable_names="temp")
#     url = getIndicatorQueryUrl(ind, onlyFirstVariable=True, skipDimensions=False, format="json", timeMin="2020-01-01", timeMax="2020-12-31")
#     assert url.startswith("http://griddap.example.com.json?")
#     assert "temp" in url
#     assert "%5B(" in url  # encoded bracket check

# def test_getIndicatorQueryUrl_tabledap_basic():
#     ind = MockIndicator(tabledap_url="http://tabledap.example.com", variable_names="temp")
#     url = getIndicatorQueryUrl(ind, onlyFirstVariable=True, skipDimensions=True, format="csv")
#     assert url.startswith("http://tabledap.example.com.csv?")
#     assert "temp" in url

# def test_getIndicatorQueryUrl_handles_none_fields():
#     ind = MockIndicator()
#     url = getIndicatorQueryUrl(ind, onlyFirstVariable=True, skipDimensions=True)
#     assert url.startswith("0?")

# def test_getIndicatorQueryUrlPoint_griddap():
#     ind = MockIndicator(griddap_url="http://griddap.example.com", dimension_names="time latitude longitude range", variable_names="temp")
#     url = getIndicatorQueryUrlPoint(
#         ind,
#         onlyFirstVariable=True,
#         skipDimensions=False,
#         lat="45",
#         lon="13",
#         time="2020-01-01T00:00:00Z",
#         range="0"
#     )
#     assert url.startswith("http://griddap.example.com?")
#     assert "temp" in url
#     assert "%5B(" in url  # encoded bracket check

# # TEST OK!!

# # Function -> url_is_indicator

# ERDDAP_URL = "http://mock.erddap.org"

# class MockIndicator:
#     def __init__(self, griddap_url=None, tabledap_url=None, dimension_names="", variable_names=""):
#         self.griddap_url = griddap_url
#         self.tabledap_url = tabledap_url
#         self.dimension_names = dimension_names
#         self.variable_names = variable_names

# def getIndicatorDataFormat(ind):
#     if ind is None:
#         return None
#     if ind.griddap_url is not None and ind.griddap_url != "":
#         return "griddap"
#     if ind.tabledap_url is not None and ind.tabledap_url != "":
#         return "tabledap"
#     return None

# def getIndicatorDimensions(ind):
#     if ind is None:
#         return None
#     return ind.dimension_names.split()

# def getIndicatorVariables(ind):
#     if ind is None:
#         return None
#     return ind.variable_names.split()

# def getVariableAliases(variable):
#     if variable == "depth":
#         return ["plev", "range"]
#     if variable == "plev":
#         return ["depth", "range"]
#     else:
#         return [variable, "range"]

# def getIndicatorBaseUrl(ind):
#     if ind and ind.griddap_url:
#         return ind.griddap_url
#     if ind and ind.tabledap_url:
#         return ind.tabledap_url
#     return "0"

# def getIndicatorQueryUrl(ind, onlyFirstVariable, skipDimensions, **kwargs):
#     if isinstance(ind, str):
#         return "http://mock/"  # simplified stub for testing

#     url = getIndicatorBaseUrl(ind) or "0"
#     if "format" in kwargs:
#         url = url + "." + kwargs["format"]

#     di = getIndicatorDimensions(ind) or []
#     va = getIndicatorVariables(ind) or []

#     tipo = getIndicatorDataFormat(ind)
#     griddap = tipo == "griddap"

#     if griddap and onlyFirstVariable and len(va) > 1:
#         va = [va[0]]

#     if griddap and "variable" in kwargs:
#         va = [kwargs["variable"]]

#     if skipDimensions:
#         di = []

#     query = "?"
#     if griddap:
#         for v in va:
#             if query != "?":
#                 query += ","
#             query += v
#             for d in di:
#                 query += f"%5B({kwargs.get(d + 'Min', '0')}):1:({kwargs.get(d + 'Max', '0')})%5D"
#     else:
#         for v in va:
#             if query != "?":
#                 query += "%2C"
#             query += v
#         for d in va:
#             if d.lower() in ["time", "latitude", "longitude"]:
#                 query += f"&{d}%3E={kwargs.get(d + 'Min', '0')}"
#                 query += f"&{d}%3C={kwargs.get(d + 'Max', '0')}"

#     result = url + query
#     return result.replace("None", "0")

# def getIndicatorQueryUrlPoint(ind, onlyFirstVariable, skipDimensions, lat, lon, time, range, **kwargs):
#     return getIndicatorQueryUrl(
#         ind,
#         onlyFirstVariable,
#         skipDimensions,
#         latitude=lat,
#         longitude=lon,
#         time=time,
#         range=range,
#     )

# def url_is_indicator(is_indicator, is_graph, is_annual, **kwargs):
#     try:
#         if is_indicator == "true" and is_graph is False:
#             return (
#                 ERDDAP_URL
#                 + "/tabledap/"
#                 + kwargs["dataset_id"]
#                 + ".csv?time%2Clatitude%2Clongitude%2C"
#                 + kwargs["layer_name"]
#                 + "&time%3E="
#                 + kwargs["date_start"]
#                 + "&time%3C="
#                 + kwargs["date_start"]
#             )
#     except Exception as e:
#         return str(e)

# def test_url_is_indicator_basic_tabledap():
#     result = url_is_indicator(
#         is_indicator="true",
#         is_graph=False,
#         is_annual=False,
#         dataset_id="mock_dataset",
#         layer_name="mock_layer",
#         date_start="2024-01-01"
#     )
#     assert result.startswith("http://mock.erddap.org/tabledap/mock_dataset.csv?")
#     assert "mock_layer" in result
#     assert "&time%3E=2024-01-01" in result
#     assert "&time%3C=2024-01-01" in result

# # TEST OK!!


 


