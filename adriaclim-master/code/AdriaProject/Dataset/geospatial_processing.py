import time
import datetime as dt
from django.forms import model_to_dict
import pandas as pd
import json
import numpy as np
import logging  # Aggiunto
from typing import List, Dict, Any, Union
from django.db.models import Q
from django.contrib.gis.geos import Polygon as GeosPolygon
from shapely.geometry import Polygon as ShapelyPolygon, Point as ShapelyPoint
import shapely.speedups
from django.core.cache import cache
from Dataset.models import Node, Polygon

from myFunctions.database_operations import is_database_almost_full
from myFunctions.data_analysis import calculate_trend, operation_before_after_cache, processOperation, packageGraphData
from myFunctions.utils import download_with_cache_as_csv
from myFunctions.indicator_manager import getIndicatorQueryUrl, url_is_indicator
from myFunctions.time_processing import convertToTime, get_season

logger = logging.getLogger(__name__)  # Inizializzazione logger

# Constants
CACHE_TIMEOUT = 43200  # 12 hours
MAX_SAMPLING_POINTS = 1000

def log_error(message: str, exception: Exception) -> None:
    """Log errors with a consistent format."""
    logger.error(f"{message}: {exception}")

def create_geos_polygon(vertices: List[tuple]) -> Union[GeosPolygon, str]:
    """Create a GEOS polygon from vertices."""
    shapely_polygon_inverse = ShapelyPolygon(vertices)
    shapely.speedups.enable()
    try:
        return GeosPolygon.from_ewkt(shapely_polygon_inverse.wkt)
    except Exception as e:
        log_error("Error creating GEOS Polygon", e)
        return str(e)

def fetch_from_cache(key: str) -> Union[Dict[str, Any], None]:
    """Fetch data from cache."""
    cache_result = cache.get(key=key)
    if cache_result is not None:
        logger.info("CACHE HIT!")
        return json.loads(cache_result)
    logger.info("CACHE MISS!")
    return None

def save_to_cache(key: str, data: Dict[str, Any]) -> None:
    """Save data to cache."""
    cache.set(key, json.dumps(data), timeout=CACHE_TIMEOUT)

def calculate_statistics(df: pd.DataFrame, values: List[float], time_op: str, adriaclim_timeperiod: str) -> Dict[str, Any]:
    """Calculate statistics like mean, median, standard deviation, and trend."""
    stats = {}
    if values:
        stats["mean"] = np.mean(values)
        stats["median"] = np.median(values)
        stats["stdev"] = np.std(values)
        stats["trend_yr"] = calculate_trend(df["date_value"].tolist(), values, timeperiod=adriaclim_timeperiod)
    return stats

def getDataPolygonNew(
    dataset_id,
    adriaclim_timeperiod,
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
    # print("ADRIACLIM_TIMEPERIOD======",adriaclim_timeperiod)
    vertices = []
    vertices_geos_poly = []

    for lat_lng in lat_lng_obj:
        vertices.append((float(lat_lng["lat"]), float(lat_lng["lng"])))
        vertices_geos_poly.append((float(lat_lng["lng"]), float(lat_lng["lat"])))

    shapely_polygon = ShapelyPolygon(vertices)
    shapely_polygon_inverse = ShapelyPolygon(vertices_geos_poly)
   
    try:
        geos_polygon = GeosPolygon.from_ewkt(shapely_polygon_inverse.wkt)
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

    #aggiungere controllo cache prima.....
    cache_result = cache.get(key=key_cached)
    
    if cache_result is not None:
        print("CACHE HIT!")
        #siamo nella cache
        #prendere tutti i dati memorizzati nella cache ed elaborarli e passarli al frontend
        pol_from_cache = json.loads(cache_result)
        dataframe_from_dict = pd.DataFrame.from_dict(pol_from_cache["dataBeforeOp"])
        dataframe_from_dict = dataframe_from_dict.dropna(how="any")
        dataframe_from_dict["date_value"] = pd.to_datetime(dataframe_from_dict["date_value"])
        pol_from_cache["dataPol"] = operation_before_after_cache(dataframe_from_dict,statistic,time_op)

        # a seconda del valore di operation e di time_op viene fatta l'operazione7
        # df_polygon_model["date_value"] = pd.to_datetime(df_polygon_model["date_value"])
        pol_from_cache_dataframe = pd.DataFrame(pol_from_cache["dataPol"])
        # date_value_to_list = pol_from_cache_dataframe.copy()
        # date_value_to_list = date_value_to_list.drop_duplicates(subset="x",keep="first")
        # # date_value_to_list["x"] = pd.to_datetime(date_value_to_list["x"])
        pol_from_cache_values = pol_from_cache_dataframe["y"].tolist()
        if len(pol_from_cache_values) == 1:
            # print("LEN 1 =", pol_from_cache_values)
            mean = pol_from_cache_values[0]
            median = pol_from_cache_values[0]
            std_dev = pol_from_cache_values[0]
            trend_value = pol_from_cache_values[0]
        else:
            trend_value = calculate_trend(pol_from_cache_dataframe["x"].tolist(),pol_from_cache_dataframe["y"].tolist())
            mean = pol_from_cache_dataframe["y"].mean()
            median = pol_from_cache_dataframe["y"].median()
            std_dev = pol_from_cache_dataframe["y"].std()
        
        pol_from_cache["mean"] = mean
        pol_from_cache["median"] = median
        pol_from_cache["stdev"] = std_dev
        pol_from_cache["trend_yr"] = trend_value
        if parametro_agg != "None":
            pol_from_cache["dataTable"][0][parametro_agg] = (
                pol_from_cache["dataTable"][0][parametro_agg]
                if not pd.isna(pol_from_cache["dataTable"][0][parametro_agg])
                else "Value not defined"
                ) 
        return pol_from_cache

    else:
        print("Check if it is in db!")
        polygons = Polygon.objects.filter(
            Q(dataset_id=dataset_id) & Q(coordinate__within=(geos_polygon)))
        if polygons.exists():
            # print("DOPO FILTER")
            
            # qui siamo nel caso in cui è presente il poligono con quel dataset id e con i punti nel poligono selezionato!
            try:
                print("CACHE MISS AND DB HIT!")
                allData = {}
                data_table_list = []
                for pol in polygons:
                    #checkare se quel determinato punto del dataset sta nel poligono selezionato
                    #sta nel poligono selezionato 
                    data_table = {}
                    data_table["time"] = pol.date_value
                    data_table["latitude"] = pol.latitude
                    data_table["longitude"] = pol.longitude
                    data_table[layer_name] = pol.value_0 if not pd.isna(pol.value_0) else "Value not defined"
                    
                    if parametro_agg != "None":
                        data_table[parametro_agg] = pol.parametro_agg if not pd.isna(pol.parametro_agg) else "Value not defined"
                    data_table_list.append(data_table)
                        
                        
                    #
                allData[
                    "dataTable"
                ] = data_table_list  # così abbiamo la tabella, ora ci serve il grafico.....

                df_polygon_model = pd.DataFrame(
                    [
                        model_to_dict(p, fields=[field.name for field in p._meta.fields])
                        for p in polygons
                    ]
                )
                df_polygon_model = df_polygon_model.drop("coordinate",axis=1)
                df_polygon_model = df_polygon_model.drop_duplicates(
                    subset=["date_value", "latitude", "longitude", "value_0"], keep="first"
                )
                df_polygon_model = df_polygon_model.dropna(how="all", axis=1)
                allData["dataBeforeOp"] = df_polygon_model.to_dict(orient="records")

                if time_op == "default":
                    date_value_to_list = df_polygon_model.copy()
                    date_value_to_list = date_value_to_list.drop_duplicates(subset="date_value",keep="first")
                    date_value_to_list["date_value"] = pd.to_datetime(date_value_to_list["date_value"])

                    # a seconda del valore di operation e di time_op viene fatta l'operazione7
                    df_polygon_model["date_value"] = pd.to_datetime(df_polygon_model["date_value"])

                    pol_from_db_values = df_polygon_model["value_0"].tolist()
                    trend_value_mean = df_polygon_model.groupby("date_value")["value_0"].mean().tolist()
                    if len(pol_from_db_values) == 1:
                        # print("LEN DB =", pol_from_db_values)
                        mean = pol_from_db_values[0]
                        median = pol_from_db_values[0]
                        std_dev = pol_from_db_values[0]
                        trend_value = pol_from_db_values[0]
                    else:
                        if len(trend_value_mean) == 1:
                            trend_value = trend_value_mean[0]
                        else:
                            trend_value = calculate_trend(date_value_to_list["date_value"].tolist(),trend_value_mean,timeperiod=adriaclim_timeperiod)
                            
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
                        point = ShapelyPoint(coord["lat"], coord["lng"]) # type: ignore
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
                                dat_tab[parametro_agg] = (
                                    row[parametro_agg]
                                    if not pd.isna(row[parametro_agg])
                                    else "Value not defined"
                                )
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
                                dat_tab[parametro_agg] = (
                                    row[parametro_agg]
                                    if not pd.isna(row[parametro_agg])
                                    else "Value not defined"
                                )
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
                                if not is_database_almost_full():
                                    Polygon.objects.update_or_create(
                                                    dataset_id=Node.objects.get(id=dataset_id),
                                                    date_value=convertToTime(row["time"]),
                                                    latitude=float(row["latitude"]),
                                                    longitude=float(row["longitude"]),
                                                    coordinate = point(float(row["longitude"]), float(row["latitude"])),
                                                    defaults=defaults,
                                                                    )
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

                                defaults = {
                                    "value_0": float(row[layer_name]),
                                    "pol_vertices_str": pol_vertices_str,
                                }
                                if not is_database_almost_full():
                                    Polygon.objects.update_or_create(
                                                    dataset_id=Node.objects.get(id=dataset_id),
                                                    date_value=convertToTime(row["time"]),
                                                    latitude=float(row["latitude"]),
                                                    longitude=float(row["longitude"]),
                                                    coordinate = point(float(row["longitude"]), float(row["latitude"])),
                                                    defaults=defaults,
                                                                    )
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
                if time_op == "default":
                    date_value_to_list = df_polygon.copy()
                    date_value_to_list = date_value_to_list.drop_duplicates(subset="date_value",keep="first")
                    date_value_to_list["date_value"] = pd.to_datetime(date_value_to_list["date_value"])

                
                    # a seconda del valore di operation e di time_op viene fatta l'operazione7
                    df_polygon["date_value"] = pd.to_datetime(df_polygon["date_value"])
                    pol_values = df_polygon["value_0"].tolist()

                    # print("POL_VALUESSSS=============",pol_values)
                    trend_value_mean = df_polygon.groupby("date_value")["value_0"].mean().tolist()
                    if len(pol_values) == 1:
                        trend_value = pol_values[0]
                        mean = pol_values[0]
                        median = pol_values[0]
                        std_dev = pol_values[0]
                    else:
                        if len(trend_value_mean) == 1:
                            trend_value = trend_value_mean[0]
                        else:
                            trend_value = calculate_trend(date_value_to_list["date_value"].tolist(),trend_value_mean,timeperiod=adriaclim_timeperiod)
        
                        mean = df_polygon["value_0"].mean()
                        median = df_polygon["value_0"].median()
                        std_dev = df_polygon["value_0"].std()
                    
                    allData["mean"] = mean
                    allData["median"] = median
                    allData["stdev"] = std_dev
                    allData["trend_yr"] = trend_value

                data_table_list = []
                for i in range(len(dataTable)):
                    data_table = {}
                    data_table["time"] = dataTable[i]["time"]
                    data_table["latitude"] = dataTable[i]["latitude"]
                    data_table["longitude"] = dataTable[i]["longitude"]
                    data_table[layer_name] = dataTable[i][layer_name]
                    if parametro_agg != "None":
                        data_table[parametro_agg] = dataTable[i][parametro_agg]
                    data_table_list.append(data_table)

                allData["dataTable"] = data_table_list
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
            
            return allData

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
seasons = {
    0: "Winter",
    1: "Spring",
    2: "Summer",
    3: "Autumn",
}

season_trend = {
    "01": "Winter",
    "02": "Spring",
    "03": "Summer",
    "04": "Autumn",
}

def getDataGraphicGeneric(
    dataset_id,
    adriaclim_timeperiod,
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
        print("ARRIVO QUI")
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

        print("PRIMA URL=====")
        if cache == 1:
            url = download_with_cache_as_csv(url)
        if url == "fuoriWms":
            return url
        # print("ARRIVO QUO")
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
        print("DF Test",df.head())
        n_values = len(df)
        allData = []
        values = []
        dates = []
        layerName = []
        lats = []
        longs = []
        i = 0
        # print("ARRIVO QUA")
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
            try:
                output = None
                if "output" in kwargs:
                    output = kwargs["output"]

                return packageGraphData(
                    processOperation(operation, values, dates, unit, layerName, lats, longs),
                    output=output,
                    operation=operation,
                    adriaclim_timeperiod=adriaclim_timeperiod,
                )
            except Exception as e:
                print("Exception in packageGraphData or processOperation===" + e)
                return str(e)
    except Exception as e:
        print("ARRIVO QUO")
        print("ECCEZIONE NO WMS ==", e)
        return str(e)


def check_dates_format_trend(dates):
    #gestire tutti i possibili formati delle date per i trend!!!!!!!!!
    if type(dates[0]) is str:
        if dates[0].startswith("0000"):
                #annual month by month point
            # print("month by month point",dates[0])
            try:
                dates = [dt.datetime.strptime(d.replace("0000","2000"), "%Y-%m-%dT%H:%M:%SZ") for d in dates]
            except Exception as e: 
                return 'Invalid date format: '+ str(e)
                # dates = [dt.datetime.strptime(d.replace('0000',"2000"), "%Y-%m-%d") for d in dates]
        elif len(dates[0].split("-")) == 2: #01-01 1 gennaio 2000-01-01
                 #annual day by day point
            for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%SZ', '%d/%m/%Y'):
                try:
                    dates = [dt.datetime.strptime("2000-" + d, fmt) for d in dates]
                except ValueError:
                    pass
        elif dates[0] == "Jan":
                #annual month by month polygon
            create_dates = []
            for d in dates:
            #annual month by month polygon
                for key, val in months.items():
                    if val ==  d:
                        month_number = key
                        create_dates.append(dt.datetime.strptime("2000-01-" + str(month_number), "%Y-%d-%m"))

            dates = list(create_dates)
        elif dates[0] == "Winter" or dates[0] == "Spring" or dates[0] == "Summer" or dates[0] == "Autumn":
            #annual season by season polygon
            create_dates = []
            for d in dates:
                for key, val in season_trend.items():
                    if val == d:
                        season_number = key
                        create_dates.append(dt.datetime.strptime("2000-01-" + str(season_number), "%Y-%d-%m"))
            
            dates = list(create_dates)
        else:
            for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%SZ', '%d/%m/%Y'):
                try:
                    dates = [dt.datetime.strptime(str(d), fmt) for d in dates]
                except ValueError:
                    pass
             
    return dates

def subtract_mean_trend(dates,values,timeperiod):
    #creation of a dataFrame with dates and values
    df_mean_trend = pd.DataFrame({"date":dates,"value":values})
    df_mean_trend["date"] = pd.to_datetime(df_mean_trend["date"])
    if timeperiod == "monthly":
        groupby_col = df_mean_trend["date"].dt.month
    if timeperiod == "daily":
        df_mean_trend["day_month"] = df_mean_trend["date"].dt.strftime('%m-%d')
        groupby_col = df_mean_trend["day_month"]
    if timeperiod == "seasonal":
        df_mean_trend["season"] = df_mean_trend["date"].apply(get_season)
        groupby_col = df_mean_trend["season"]
    
    #raggrupparle a seconda della scala temporale del dataset e calcolarne la media
    df_mean_trend["mean_timeperiod"] = df_mean_trend.groupby(groupby_col)["value"].transform("mean")

    # print("DF_MEAN_TREND AFTER MEAN=====",df_mean_trend.head(20))
    #sottrarre ad ogni data di un mese o di una stagione o di un giorno il valore della media calcolato
    df_mean_trend["value"] = df_mean_trend["value"] - df_mean_trend["mean_timeperiod"]
    # print("DF_MEAN_TREND AFTER MEAN=====",df_mean_trend.head(20))

    return df_mean_trend["value"].values
