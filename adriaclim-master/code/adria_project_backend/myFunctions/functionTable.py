import requests
from datetime import datetime
from myFunctions.indicator_manager import getIndicatorQueryUrl

def correct_start_time_if_needed(start_time_str):
    try:
        dt = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
        if dt.hour == 0 and dt.minute == 0:
            dt = dt.replace(hour=12)
        return dt.isoformat().replace("+00:00", "Z")
    except Exception:
        return start_time_str

def getDataFunctionsTable(
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
        time_start = correct_start_time_if_needed(time_start)
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
        r = requests.get(url=url)
        data = r.json()
        return data

    except Exception as e:
        return "fuoriWms"