import re
import time
import asyncio
import requests
import numpy as np
import pandas as pd
from django.db import connection
from django.db import transaction
from django.core.cache import cache
from AdriaProject.logger_config import setup_logger
from Dataset.models import Node, Indicator
from AdriaProject.settings import ERDDAP_URL
from typing import List, Dict, Any, Optional
from myFunctions.utils import download_with_cache_as_csv
from myFunctions.database_operations import is_database_almost_full, delete_all

logger = setup_logger(__name__)  

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
    # Estrae i metadati associati al dataset
    metadata = process_metadata(row["Info"])
    if not metadata:
        return

    # Inizializzazione delle variabili di supporto
    adriaclim_scale = adriaclim_dataset = adriaclim_timeperiod = adriaclim_model = adriaclim_type = None
    institution = "UNKNOWN"
    time_start = time_end = ""
    lat_min = lat_max = lng_min = lng_max = None
    variables = dimensions = 0
    variable_names = variable_types = dimension_names = ""
    param_min = param_max = param_step = 0
    node_id = row["DatasetID"]
    griddap_url = row["griddap"]

    # Ciclo su ciascun riga dei metadati
    for meta_row in metadata:
        row_type = meta_row["RowType"]
        var_name = meta_row["VariableName"]
        attr_name = meta_row["AttributeName"]
        attr_value = meta_row["Value"]

        # Conteggio delle dimensioni e costruzione stringa nomi dimensioni
        if row_type == "dimension":
            dimensions += 1
            dimension_names += f"{var_name} "

        # Conteggio variabili e tipologie
        if row_type == "variable":
            variables += 1
            variable_names += f"{var_name} "
            variable_types += f"{meta_row['DataType']} "

        # Estrazione metadati personalizzati AdriaClim e metadati globali
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

        # Estrazione range e passo parametri da griddap
        if griddap_url:
            if attr_name == "actual_range" and var_name not in ["time", "latitude", "longitude"]:
                try:
                    parts = attr_value.split(",")
                    param_min = float(parts[0])
                    param_max = float(parts[1].strip())
                except Exception:
                    pass  # Range non valido o malformato
            elif row_type == "dimension" and var_name not in ["time", "Times", "latitude", "longitude"]:
                try:
                    spacing = attr_value
                    average_spacing_others = spacing.split(",")[2]
                    param_step = abs(float(average_spacing_others.split("=")[1]))
                except Exception:
                    pass  # Nessuno spacing calcolabile

    # Se presenti time_start e time_end, si salva il dataset nel DB
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

        # Salvataggio nodo nel database
        save_node_to_db(node_id, defaults)


def safe_insert_node(node_id, defaults):
    """Inserisce il nodo ignorando i duplicati."""
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                INSERT INTO "Dataset_node" (
                    id, adriaclim_dataset, adriaclim_model, adriaclim_timeperiod, adriaclim_scale,
                    adriaclim_type, title, metadata_url, institution, lat_min, lat_max,
                    lng_min, lng_max, time_start, time_end, param_min, param_max, param_step,
                    tabledap_url, dimensions, dimension_names, variables, variable_names,
                    variable_types, griddap_url, wms_url
                ) VALUES (
                    %(id)s, %(adriaclim_dataset)s, %(adriaclim_model)s, %(adriaclim_timeperiod)s, %(adriaclim_scale)s,
                    %(adriaclim_type)s, %(title)s, %(metadata_url)s, %(institution)s, %(lat_min)s, %(lat_max)s,
                    %(lng_min)s, %(lng_max)s, %(time_start)s, %(time_end)s, %(param_min)s, %(param_max)s, %(param_step)s,
                    %(tabledap_url)s, %(dimensions)s, %(dimension_names)s, %(variables)s, %(variable_names)s,
                    %(variable_types)s, %(griddap_url)s, %(wms_url)s
                )
                ON CONFLICT (id) DO NOTHING
            """, {"id": node_id, **defaults})
        except Exception as e:
            logger.warning(f"Errore durante l'inserimento di {node_id}: {e}")


def getAllDatasets():
    start_time = time.time()
    logger.info("Started getAllDatasets()")

    url_datasets = "https://erddap-adriaclim.cmcc-opa.eu/erddap/info/index.csv?page=1&itemsPerPage=100000"
    asyncio.run(delete_all("Node"))

    try:
        df = pd.read_table(
            download_with_cache_as_csv(url_datasets),
            header=0,
            sep=",",
            engine="c",
            names=[
                "griddap", "subset", "tabledap", "MakeAGraph", "wms", "files", "Title", "Summary",
                "FGDC", "ISO 19115", "Info", "BackgroundInfo", "RSS", "Email", "Institution", "DatasetID"
            ],
            na_values="Value not available"
        )
        df = df.fillna("")
        df.drop(index=df.index[0], axis=0, inplace=True)
    except Exception as e:
        logger.error(f"Errore durante il download o parsing dei dataset: {e}")
        return str(e)

    processed_ids = set()

    for row in df.to_dict(orient="records"):
        node_id = row["DatasetID"]
        if node_id in processed_ids:
            continue
        processed_ids.add(node_id)

        info = row["Info"]
        adriaclim_scale = adriaclim_dataset = adriaclim_timeperiod = adriaclim_model = adriaclim_type = None
        institution = "UNKNOWN"
        time_start = time_end = ""
        lat_min = lat_max = lng_min = lng_max = None
        variables = dimensions = 0
        variable_names = variable_types = dimension_names = ""
        param_min = param_max = param_step = 0
        metadata_url = row["Info"]
        tabledap_url = row["tabledap"]
        griddap_url = row["griddap"]
        wms_url = row["wms"]

        try:
            get_info = pd.read_table(
                download_with_cache_as_csv(info),
                header=None,
                sep=",",
                engine="c",
                names=["RowType", "VariableName", "AttributeName", "DataType", "Value"]
            ).fillna("nan")
            get_info.drop(index=get_info.index[0], axis=0, inplace=True)
        except Exception as e:
            logger.warning(f"Errore durante il parsing dei metadata per {node_id}: {e}")
            continue

        get_info = get_info.to_dict(orient="records")

        for row1 in get_info:
            if row1["RowType"] == "dimension":
                if dimensions > 0:
                    dimension_names += " "
                dimensions += 1
                dimension_names += row1["VariableName"]

            if row1["RowType"] == "variable":
                if variables > 0:
                    variable_names += " "
                    variable_types += " "
                variables += 1
                variable_names += row1["VariableName"]
                variable_types += row1["DataType"]

            if row1["AttributeName"] == "adriaclim_dataset":
                adriaclim_dataset = row1["Value"]
            elif row1["AttributeName"] == "adriaclim_model":
                adriaclim_model = row1["Value"]
            elif row1["AttributeName"] == "adriaclim_scale":
                adriaclim_scale = row1["Value"]
            elif row1["AttributeName"] == "adriaclim_timeperiod":
                adriaclim_timeperiod = row1["Value"]
            elif row1["AttributeName"] == "adriaclim_type":
                adriaclim_type = row1["Value"]
            elif row1["AttributeName"] == "institution":
                institution = row1["Value"]
            elif row1["AttributeName"] == "time_coverage_start":
                time_start = row1["Value"]
            elif row1["AttributeName"] == "time_coverage_end":
                time_end = row1["Value"]
            elif row1["AttributeName"] == "geospatial_lat_min":
                lat_min = row1["Value"]
            elif row1["AttributeName"] == "geospatial_lat_max":
                lat_max = row1["Value"]
            elif row1["AttributeName"] == "geospatial_lon_min":
                lng_min = row1["Value"]
            elif row1["AttributeName"] == "geospatial_lon_max":
                lng_max = row1["Value"]

            if griddap_url:
                if (
                    row1["AttributeName"] == "actual_range"
                    and row1["VariableName"] not in ["time", "latitude", "longitude"]
                ):
                    try:
                        param_agg = row1["Value"].split(",")
                        param_min = float(param_agg[0])
                        param_max = float(param_agg[1].strip())
                    except Exception:
                        pass
                elif (
                    row1["RowType"] == "dimension"
                    and row1["VariableName"] not in ["time", "Times", "latitude", "longitude"]
                ):
                    try:
                        spacing = row1["Value"]
                        average_spacing_others = spacing.split(",")[2]
                        param_step = abs(float(average_spacing_others.split("=")[1]))
                    except Exception:
                        pass

        # Inferenze automatiche
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
            elif "monthly" in row["Title"].lower():
                adriaclim_timeperiod = "monthly"
            elif "seasonal" in row["Title"].lower():
                adriaclim_timeperiod = "seasonal"
            elif is_indicator:
                adriaclim_timeperiod = "yearly"
            else:
                adriaclim_timeperiod = "UNKNOWN"

        if time_start and time_end:
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
            safe_insert_node(node_id, defaults)

    logger.info("Completata getAllDatasets() in %.2f secondi", time.time() - start_time)


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
        if row["DatasetID"] != dataset_id:
            continue

        metadata = pd.read_csv(
            download_with_cache_as_csv(row["Info"]),
            header=None,
            sep=",",
            names=["Row Type", "Variable Name", "Attribute Name", "Data Type", "Value"],
        ).fillna("nan")

        # Inizializzazione variabili
        variable_meta = title_meta = layer_name = values_time = attribution_layer = ""
        values_others = average_spacing_others = positive_negative = ""
        latitude_range = longitude_range = ""
        lat_min = lat_max = long_min = long_max = ""
        dimensions = "time, latitude, longitude"

        for _, row1 in metadata.iterrows():
            row_type = row1["Row Type"]
            var_name = row1["Variable Name"]
            attr_name = row1["Attribute Name"]
            value = row1["Value"]

            if row_type == "variable":
                variable_meta = value
                layer_name = var_name

            elif row_type == "attribute":
                if attr_name == "title":
                    title_meta = value
                elif var_name in ["time", "Times"] and attr_name == "actual_range":
                    values_time = value
                elif attr_name == "institution":
                    attribution_layer = value
                elif var_name not in ["time", "Times", "latitude", "longitude"] and attr_name == "actual_range":
                    values_others = value
                elif attr_name == "positive":
                    positive_negative = value
                elif var_name == "latitude" and attr_name == "actual_range":
                    latitude_range = value
                elif var_name == "longitude" and attr_name == "actual_range":
                    longitude_range = value

            elif row_type == "dimension" and var_name not in ["time", "Times", "latitude", "longitude"]:
                dimensions += f", {var_name}"
                try:
                    average_spacing_others = value.split(",")[2]
                except Exception:
                    pass

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
    """
    Estrae e struttura i metadati associati a un dataset specifico.
    """
    all_metadata = getMetadataTime1(dataset_id)
    min_max_value = []
    average_spacing_others = []
    final_list = []

    if len(all_metadata) < 2:
        logger.warning(f"Metadati insufficienti per dataset {dataset_id}")
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
    """
    Recupera i metadati in formato JSON per un dataset o indicatore specifico.
    """
    try:
        x = Node.objects.get(id=dataset_id)
        url = x.metadata_url.replace(".csv", ".json")
        r = requests.get(url=url)
        return r.json()
    except Node.DoesNotExist:
        logger.warning(f"Dataset non trovato in Node: {dataset_id}")
        try:
            indicator = Indicator.objects.get(pk=dataset_id)
            url = indicator.metadata_url.replace(".csv", ".json")
            r = requests.get(url=url)
            return r.json()
        except Indicator.DoesNotExist:
            logger.error(f"Dataset non trovato nemmeno in Indicator: {dataset_id}")
            return None

def download_big_data(request):
    try:
        download_big_data()
        return "Ho aggiustato tutto!!!!"
    except Exception as e:
        return str(e)