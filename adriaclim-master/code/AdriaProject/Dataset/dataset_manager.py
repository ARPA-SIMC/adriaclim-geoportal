import re
import time
import asyncio
import logging
import requests
import numpy as np
import pandas as pd

from django.db import transaction
from django.core.cache import cache
from Dataset.models import Node, Indicator
from AdriaProject.settings import ERDDAP_URL
from typing import List, Dict, Any, Optional
from myFunctions.utils import download_with_cache_as_csv
from myFunctions.database_operations import is_database_almost_full, delete_all

logger = logging.getLogger(__name__)  

DATASET_COLUMNS = [
    "griddap", "subset", "tabledap", "MakeAGraph", "wms", "files", "Title",
    "Summary", "FGDC", "ISO 19115", "Info", "BackgroundInfo", "RSS",
    "Email", "Institution", "DatasetID",
]
INFO_COLUMNS = ["RowType", "VariableName", "AttributeName", "DataType", "Value"]

def fetch_datasets() -> pd.DataFrame:
    url_datasets = f"{ERDDAP_URL}/info/index.csv?page=1&itemsPerPage=100000"
    try:
        df = pd.read_table(
            download_with_cache_as_csv(url_datasets),
            header=0,
            sep=",",
            engine="c",
            names=DATASET_COLUMNS,
            na_values="Value not available",
        ).fillna("")

        if not df.empty:
            df.drop(index=df.index[0], axis=0, inplace=True)

        return df
    except Exception as e:
        logger.error(f"Error fetching datasets: {e}")
        return pd.DataFrame()

def process_metadata(info_url: str) -> List[Dict[str, Any]]:
    try:
        metadata = pd.read_table(
            download_with_cache_as_csv(info_url),
            header=None,
            sep=",",
            engine="c",
            names=INFO_COLUMNS,
        ).fillna("nan")
        metadata.drop(index=metadata.index[0], axis=0, inplace=True)
        return metadata.to_dict(orient="records")
    except Exception as e:
        logger.error(f"Error processing metadata: {e}")
        return []

def save_node_to_db(node_id: str, defaults: Dict[str, Any]) -> None:
    if not is_database_almost_full():
        with transaction.atomic():
            Node.objects.update_or_create(id=node_id, defaults=defaults)

def process_dataset_row(row: Dict[str, Any]) -> None:
    metadata = process_metadata(row["Info"])
    if not metadata:
        return

    adriaclim_scale = adriaclim_dataset = adriaclim_timeperiod = adriaclim_model = adriaclim_type = None
    institution = "UNKNOWN"
    time_start = time_end = ""
    lat_min = lat_max = lng_min = lng_max = None
    variables = dimensions = 0
    variable_names = variable_types = dimension_names = ""
    param_min = param_max = param_step = 0
    node_id = row["DatasetID"]
    griddap_url = row["griddap"]

    for meta_row in metadata:
        row_type = meta_row["RowType"]
        var_name = meta_row["VariableName"]
        attr_name = meta_row["AttributeName"]
        attr_value = meta_row["Value"]

        if row_type == "dimension":
            dimensions += 1
            dimension_names += f"{var_name} "

        if row_type == "variable":
            variables += 1
            variable_names += f"{var_name} "
            variable_types += f"{meta_row['DataType']} "

        if attr_name == "adriaclim_dataset":
            adriaclim_dataset = attr_value
        elif attr_name == "adriaclim_model":
            adriaclim_model = attr_value
        elif attr_name == "adriaclim_scale":
            adriaclim_scale = attr_value
        elif attr_name == "adriaclim_timeperiod":
            adriaclim_timeperiod = attr_value
        elif attr_name == "adriaclim_type":
            adriaclim_type = attr_value
        elif attr_name == "institution":
            institution = attr_value
        elif attr_name == "time_coverage_start":
            time_start = attr_value
        elif attr_name == "time_coverage_end":
            time_end = attr_value
        elif attr_name == "geospatial_lat_min":
            lat_min = attr_value
        elif attr_name == "geospatial_lat_max":
            lat_max = attr_value
        elif attr_name == "geospatial_lon_min":
            lng_min = attr_value
        elif attr_name == "geospatial_lon_max":
            lng_max = attr_value

        if griddap_url:
            if attr_name == "actual_range" and var_name not in ["time", "latitude", "longitude"]:
                try:
                    parts = attr_value.split(",")
                    param_min = float(parts[0])
                    param_max = float(parts[1].strip())
                except Exception:
                    pass
            elif row_type == "dimension" and var_name not in ["time", "Times", "latitude", "longitude"]:
                try:
                    spacing = attr_value
                    average_spacing_others = spacing.split(",")[2]
                    param_step = abs(float(average_spacing_others.split("=")[1]))
                except Exception:
                    pass

    if time_start and time_end:
        defaults = {
            "adriaclim_dataset": adriaclim_dataset,
            "adriaclim_model": adriaclim_model,
            "adriaclim_timeperiod": adriaclim_timeperiod,
            "adriaclim_scale": adriaclim_scale,
            "adriaclim_type": adriaclim_type,
            "title": row["Title"],
            "metadata_url": row["Info"],
            "institution": institution,
            "lat_min": lat_min,
            "lat_max": lat_max,
            "lng_min": lng_min,
            "lng_max": lng_max,
            "time_start": time_start,
            "time_end": time_end,
            "param_min": param_min,
            "param_max": param_max,
            "param_step": param_step,
            "tabledap_url": row["tabledap"],
            "dimensions": dimensions,
            "dimension_names": dimension_names.strip(),
            "variables": variables,
            "variable_names": variable_names.strip(),
            "variable_types": variable_types.strip(),
            "griddap_url": griddap_url,
            "wms_url": row["wms"],
        }
        save_node_to_db(node_id, defaults)

def getAllDatasets():
    start_time = time.time()
    print("Started getAllDatasets()")
    url_datasets = ERDDAP_URL + "/info/index.csv?page=1&itemsPerPage=100000"
    asyncio.run(delete_all("Node"))  
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

        df = df.fillna("")
        df.drop(index=df.index[0], axis=0, inplace=True)
    except Exception as e:
        print("Error", e)
        return str(e)
    for row in df.to_dict(orient="records"):
        info = row["Info"]
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
        variable_types = ""
        dimensions = 0
        dimension_names = ""
        param_min = 0
        param_max = 0
        param_step = 0
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
        get_info.drop(index=get_info.index[0], axis=0, inplace=True)
        get_info = get_info.to_dict(orient="records")
        for row1 in get_info:
            if row1 == get_info[-1] and time_start != "" and time_end != "":
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
                    "param_step": param_step,
                    "tabledap_url": tabledap_url,
                    "dimensions": dimensions,
                    "dimension_names": dimension_names,
                    "variables": variables,
                    "variable_names": variable_names,
                    "variable_types": variable_types,
                    "griddap_url": griddap_url,
                    "wms_url": wms_url,
                }
                if not is_database_almost_full():
                    Node.objects.update_or_create(id=node_id, defaults=defaults)
            else:
                if row1["RowType"] == "dimension":
                    if dimensions > 0:
                        dimension_names = dimension_names + " "

                    dimensions = dimensions + 1
                    dimension_names = dimension_names + row1["VariableName"]

                if row1["RowType"] == "variable":
                    if variables > 0:
                        variable_names = variable_names + " "
                        variable_types = variable_types + " "

                    variables = variables + 1
                    variable_names = variable_names + row1["VariableName"]
                    variable_types = variable_types + row1["DataType"]

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
                    elif (
                        row1["RowType"] == "dimension"
                        and row1["VariableName"] != "time"
                        and row1["VariableName"] != "Times"
                        and row1["VariableName"] != "latitude"
                        and row1["VariableName"] != "longitude"
                    ):
                        try:
                            spacing = row1["Value"]
                            average_spacing_others = spacing.split(",")[2]
                            param_step = abs(float(average_spacing_others.split("=")[1]))
                        except Exception as e:
                            pass
                    
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


def getMetadataTime1(dataset_id: str) -> List[Any]:
    url_datasets = f"{ERDDAP_URL}/info/index.csv?page=1&itemsPerPage=1000000000"
    df = pd.read_csv(
        download_with_cache_as_csv(url_datasets),
        header=None,
        sep=",",
        names=DATASET_COLUMNS,
        na_values=""
    ).replace(np.nan, "", regex=True)

    for _, row in df.iterrows():
        if row["DatasetID"] == dataset_id:
            metadata = pd.read_csv(
                download_with_cache_as_csv(row["Info"]),
                header=None,
                sep=",",
                names=["Row Type", "Variable Name", "Attribute Name", "Data Type", "Value"],
            ).fillna("nan")

            variable_meta = title_meta = layer_name = values_time = attribution_layer = ""
            values_others = average_spacing_others = positive_negative = ""
            latitude_range = longitude_range = ""
            dimensions = "time, latitude, longitude"
            lat_min = lat_max = long_min = long_max = ""

            for _, row1 in metadata.iterrows():
                if row1["Row Type"] == "variable":
                    variable_meta = row1["Value"]
                    layer_name = row1["Variable Name"]
                if row1["Row Type"] == "attribute" and row1["Attribute Name"] == "title":
                    title_meta = row1["Value"]
                if row1["Row Type"] == "attribute" and row1["Variable Name"] in ["time", "Times"] and row1["Attribute Name"] == "actual_range":
                    values_time = row1["Value"]
                if row1["Row Type"] == "attribute" and row1["Attribute Name"] == "institution":
                    attribution_layer = row1["Value"]
                if row1["Row Type"] == "attribute" and row1["Variable Name"] not in ["time", "Times", "latitude", "longitude"] and row1["Attribute Name"] == "actual_range":
                    values_others = row1["Value"]
                if row1["Row Type"] == "dimension" and row1["Variable Name"] not in ["time", "Times", "latitude", "longitude"]:
                    dimensions += ", " + row1["Variable Name"]
                    try:
                        average_spacing_others = row1["Value"].split(",")[2]
                    except Exception:
                        pass
                if row1["Row Type"] == "attribute" and row1["Attribute Name"] == "positive":
                    positive_negative = row1["Value"]
                if row1["Row Type"] == "attribute" and row1["Variable Name"] == "latitude" and row1["Attribute Name"] == "actual_range":
                    latitude_range = row1["Value"]
                if row1["Row Type"] == "attribute" and row1["Variable Name"] == "longitude" and row1["Attribute Name"] == "actual_range":
                    longitude_range = row1["Value"]

            if variable_meta != "nan":
                return [
                    values_others, variable_meta, values_time, title_meta,
                    layer_name, average_spacing_others, attribution_layer,
                    positive_negative, latitude_range, longitude_range
                ]
            else:
                return [
                    values_others, dimensions, values_time, title_meta,
                    layer_name, average_spacing_others, attribution_layer,
                    positive_negative, latitude_range, longitude_range, True
                ]
    return []

def getMetadata(dataset_id: str) -> List[Any]:
    all_metadata = getMetadataTime1(dataset_id)
    min_max_value = []
    average_spacing_others = []
    final_list = []

    if len(all_metadata) < 2:
        return []

    for item in all_metadata[1].split(","):
        if item.strip():
            min_max_value.append(all_metadata[0])
            average_spacing_others.append(all_metadata[5] if len(all_metadata) > 5 else 0)
        else:
            min_max_value.append(0)
            average_spacing_others.append(0)

    return [all_metadata, min_max_value, average_spacing_others]

def getMetadataOfASpecificDataset(dataset_id: str) -> Optional[Dict[str, Any]]:
    try:
        x = Node.objects.get(id=dataset_id)
        url = x.metadata_url.replace(".csv", ".json")
        r = requests.get(url=url)
        return r.json()
    except Node.DoesNotExist:
        try:
            indicator = Indicator.objects.get(pk=dataset_id)
            url = indicator.metadata_url.replace(".csv", ".json")
            r = requests.get(url=url)
            return r.json()
        except Indicator.DoesNotExist:
            return None
