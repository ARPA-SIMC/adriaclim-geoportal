from myFunctions.allFunctions import getIndicatorQueryUrl
import requests

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
        r = requests.get(url=url)
        data = r.json()
        return data

    except Exception as e:
        print("EXEPTION =", e)
        return "fuoriWms"