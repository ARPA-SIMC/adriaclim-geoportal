"""
Funzioni per la gestione, estrazione e parsing dei metadati dei dataset.
"""
import requests
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional

from Dataset.models import Node, Indicator
from AdriaProject.logger_config import setup_logger
from AdriaProject.settings import ERDDAP_URL
from myFunctions.utils import download_with_cache_as_csv

logger = setup_logger(__name__)


DATASET_COLUMNS = [
    "griddap", "subset", "tabledap", "MakeAGraph", "wms", "files", "Title",
    "Summary", "FGDC", "ISO 19115", "Info", "BackgroundInfo", "RSS",
    "Email", "Institution", "DatasetID",
]
INFO_COLUMNS = ["RowType", "VariableName", "AttributeName", "DataType", "Value"]

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