from Dataset.models import Node
from typing import Optional, List
from AdriaProject.settings import ERDDAP_URL

from AdriaProject.logger_config import setup_logger

logger = setup_logger(__name__)

def getIndicator(id: int) -> Optional[Node]:
    """Retrieve an indicator by its ID."""
    return Node.objects.filter(id=id).first()


def getIndicatorBaseUrl(ind: Node) -> Optional[str]:
    """Get the base URL for the indicator."""
    if not ind:
        return None
    return ind.griddap_url or ind.tabledap_url


def getIndicatorDataFormat(ind: Node) -> Optional[str]:
    """Get the data format for the indicator."""
    if not ind:
        return None
    if ind.griddap_url:
        return "griddap"
    if ind.tabledap_url:
        return "tabledap"
    return None


def getIndicatorDimensions(ind: Node) -> Optional[List[str]]:
    """Get the dimensions of the indicator."""
    return ind.dimension_names.split() if ind else None


def getIndicatorVariables(ind: Node) -> Optional[List[str]]:
    """Get the variables of the indicator."""
    return ind.variable_names.split() if ind else None


def getVariableAliases(variable: str) -> List[str]:
    """Get aliases for a variable."""
    aliases = {
        "depth": ["plev", "range"],
        "plev": ["depth", "range"]
    }
    return aliases.get(variable, [variable, "range"])


def buildQueryString(variables: List[str], dimensions: List[str], griddap: bool, **kwargs) -> str:
    """Build the query string for the indicator."""
    query = "?"
    if griddap:
        for var in variables:
            query += f"{',' if query != '?' else ''}{var}"
            for dim in dimensions:
                query += f"%5B({kwargs.get(dim + 'Min', kwargs.get(dim, '0'))}):1:({kwargs.get(dim + 'Max', kwargs.get(dim, '0'))})%5D"
    else:
        query += "%2C".join(variables)
        for dim in dimensions:
            if dim.lower() in ["time", "latitude", "longitude"]:
                min_val = kwargs.get(dim + "Min", kwargs.get(dim, "0"))
                max_val = kwargs.get(dim + "Max", kwargs.get(dim, "0"))
                query += f"&{dim}%3E={min_val}&{dim}%3C={max_val}"
    return query

def safe_str(val, default=""):
    return str(val) if val is not None else default

def get_dim_value(dim_name, kwargs, bound_type):
    """
    Recupera il valore minimo o massimo da kwargs (es. "timeMin", "timeMax").
    Se non trovato, prova con alias.
    """
    if bound_type not in ["Min", "Max"]:
        raise ValueError("bound_type must be 'Min' or 'Max'")
    
    direct = kwargs.get(dim_name + bound_type)
    if direct:
        return direct

    aliases = getVariableAliases(dim_name)
    for al in aliases:
        val = kwargs.get(al + bound_type)
        if val:
            return val
    return kwargs.get(dim_name) or "0"

def getIndicatorQueryUrl(ind, onlyFirstVariable, skipDimensions, **kwargs):
    if isinstance(ind, str):
        ind = getIndicator(ind)

    url = getIndicatorBaseUrl(ind)

    if "format" in kwargs and kwargs["format"] is not None:
        url += "." + safe_str(kwargs.get("format"))

    di = getIndicatorDimensions(ind)
    va = getIndicatorVariables(ind)
    tipo = getIndicatorDataFormat(ind)
    griddap = tipo == "griddap"

    if griddap and onlyFirstVariable and va.count() > 1:
        va = [va[0]]
    if griddap and "variable" in kwargs:
        va = [kwargs["variable"]]
    if skipDimensions:
        di = []

    query = "?"

    if griddap:
        for v in va:
            if query != "?":
                query += ","
            query += v
            for d in di:
                query += "%5B(" + get_dim_value(d, kwargs, "Min") + "):1:(" + get_dim_value(d, kwargs, "Max") + ")%5D"
    else:
        for v in va:
            if query != "?":
                query += "%2C"
            query += v

        for d in va:
            if "time" in d.lower() or d in ["latitude", "longitude"]:
                query += "&" + d + "%3E=" + get_dim_value(d, kwargs, "Min")
                query += "&" + d + "%3C=" + get_dim_value(d, kwargs, "Max")

    result = url + query
    if "None" in result:
        result = result.replace("None", "0")

    logger.debug(f"Final query URL: {result}")
    return result


def url_is_indicator(is_indicator, is_graph, is_annual, **kwargs):
    try:
        if is_indicator == "true" and is_graph == False:
            url = (
                ERDDAP_URL
                + "/tabledap/"
                + kwargs["dataset_id"]
                + ".csv?"
                + "time%2Clatitude%2Clongitude%2C"
                + kwargs["layer_name"]
                + "&time%3E="
                + kwargs["date_start"]
                + "&time%3C="
                + kwargs["date_start"]
            )

        elif is_indicator == "true" and is_graph and is_annual:
            try:
                url = (
                    ERDDAP_URL
                    + "/tabledap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + "time%2Clatitude%2Clongitude%2C"
                    + kwargs["layer_name"]
                    + "&time%3E="
                    + kwargs["time_start"]
                    + "&time%3C="
                    + kwargs["time_finish"]
                    + "&latitude%3E="
                    + kwargs["latitude"]
                    + "&latitude%3C="
                    + kwargs["latitude"]
                    + "&longitude%3E="
                    + kwargs["longitude"]
                    + "&longitude%3C="
                    + kwargs["longitude"]
                )
            except Exception as e1:
                return str(e1)
            
        # elif is_indicator == "true" and is_graph and is_annual and kwargs["boolNostraFunzione"]:
        #     try:
                # https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/ARPAE_f903_2ae5_11cb.htmlTable?
                # longitude,latitude,a_95_BO_9_m&time%3E=2022-11-25&time%3C=2022-12-02&longitude%3E=11.877&longitude%3C=12.877&latitude%3E=43.62&latitude%3C=44.62&.draw=markers&.marker=5%7C5&.color=0x000000&.colorBar=%7C%7C%7C%7C%7C&.bgColor=0xffccccff
                # url = (
                #     ERDDAP_URL
                #     + "/tabledap/"
                #     + kwargs["dataset_id"]
                #     + ".csv?"
                #     + "logitude,latitude,"
                #     + kwargs["layer_name"]
                #     + "&time%3E="
                #     + kwargs["time_start"]
                #     + "&time%3C="
                #     + kwargs["time_finish"]
                #     + "&longitude%3E="
                #     + kwargs["longMin"]
                #     + "&longitude%3C="
                #     + kwargs["longMax"]
                #     + "&latitude%3E="
                #     + kwargs["latMin"]
                #     + "&latitude%3C="
                #     + kwargs["latMax"]
                # )
            #     url = "ok"
            # except Exception as e1:
            #     # return str(e1)
            #     return "ok errore"
        elif is_indicator == "true" and is_graph and not is_annual:
            url = (
                ERDDAP_URL
                + "/tabledap/"
                + kwargs["dataset_id"]
                + ".csv?"
                + "time%2Clatitude%2Clongitude%2C"
                + kwargs["layer_name"]
                + "&time%3E="
                + kwargs["time_start"]
                + "&time%3C="
                + kwargs["time_finish"]
                + "&latitude%3E="
                + kwargs["latMin"]
                + "&latitude%3C="
                + kwargs["latMax"]
                + "&longitude%3E="
                + kwargs["longMin"]
                + "&longitude%3C="
                + kwargs["longMax"]
            )

        elif is_indicator == "false" and is_graph == False and is_annual == False:
            time_stride = str(kwargs.get("time_stride", 1))
            lat_stride  = str(kwargs.get("lat_stride", 1))
            lon_stride  = str(kwargs.get("lon_stride", 1))

            if kwargs.get("num_param", 0) > 3:
                url = (
                    ERDDAP_URL
                    + "/griddap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + kwargs["layer_name"]
                    + "%5B("
                    + kwargs["time_start"]
                    + "):" + time_stride + ":("
                    + kwargs["time_finish"]
                    + ")%5D%5B("
                    + str(kwargs["range_value"])
                    + "):1:("
                    + str(kwargs["range_value"])
                    + ")%5D%5B("
                    + kwargs["latitude_start"]
                    + "):" + lat_stride + ":("
                    + kwargs["latitude_end"]
                    + ")%5D%5B("
                    + kwargs["longitude_start"]
                    + "):" + lon_stride + ":("
                    + kwargs["longitude_end"]
                    + ")%5D"
                )
            else:
                url = (
                    ERDDAP_URL
                    + "/griddap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + kwargs["layer_name"]
                    + "%5B("
                    + kwargs["time_start"]
                    + "):" + time_stride + ":("
                    + kwargs["time_finish"]
                    + ")%5D%5B("
                    + kwargs["latitude_start"]
                    + "):" + lat_stride + ":("
                    + kwargs["latitude_end"]
                    + ")%5D%5B("
                    + kwargs["longitude_start"]
                    + "):" + lon_stride + ":("
                    + kwargs["longitude_end"]
                    + ")%5D"
                )
        # elif is_indicator == "false" and is_graph == False and is_annual == False:
        #     if kwargs["num_param"] > 3:
        #         url = (
        #             ERDDAP_URL
        #             + "/griddap/"
        #             + kwargs["dataset_id"]
        #             + ".csv?"
        #             + kwargs["layer_name"]
        #             + "%5B("
        #             + kwargs["time_start"]
        #             + "):1:("
        #             + kwargs["time_finish"]
        #             + ")%5D%5B("
        #             + str(kwargs["range_value"])
        #             + "):1:("
        #             + str(kwargs["range_value"])
        #             + ")%5D%5B("
        #             + kwargs["latitude_start"]
        #             + "):1:("
        #             + kwargs["latitude_end"]
        #             + ")%5D%5B("
        #             + kwargs["longitude_start"]
        #             + "):1:("
        #             + kwargs["longitude_end"]
        #             + ")%5D"
        #         )
        #     else:
        #         url = (
        #             ERDDAP_URL
        #             + "/griddap/"
        #             + kwargs["dataset_id"]
        #             + ".csv?"
        #             + kwargs["layer_name"]
        #             + "%5B("
        #             + kwargs["time_start"]
        #             + "):1:("
        #             + kwargs["time_finish"]
        #             + ")%5D%5B("
        #             + kwargs["latitude_start"]
        #             + "):1:("
        #             + kwargs["latitude_end"]
        #             + ")%5D%5B("
        #             + kwargs["longitude_start"]
        #             + "):1:("
        #             + kwargs["longitude_end"]
        #             + ")%5D"
        #         )

        elif is_indicator == "false" and is_graph and is_annual == False:
            if kwargs["num_parameters"] > 3:
                url = (
                    ERDDAP_URL
                    + "/griddap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + kwargs["layer_name"]
                    + "%5B("
                    + kwargs["time_start"]
                    + "):1:("
                    + kwargs["time_finish"]
                    + ")%5D%5B("
                    + str(kwargs["range_value"])
                    + "):1:("
                    + str(kwargs["range_value"])
                    + ")%5D%5B("
                    + kwargs["latitude"]
                    + "):1:("
                    + kwargs["latitude"]
                    + ")%5D%5B("
                    + kwargs["longitude"]
                    + "):1:("
                    + kwargs["longitude"]
                    + ")%5D"
                )
            else:
                url = (
                    ERDDAP_URL
                    + "/griddap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + kwargs["layer_name"]
                    + "%5B("
                    + kwargs["time_start"]
                    + "):1:("
                    + kwargs["time_finish"]
                    + ")%5D%5B("
                    + kwargs["latitude"]
                    + "):1:("
                    + kwargs["latitude"]
                    + ")%5D%5B("
                    + kwargs["longitude"]
                    + "):1:("
                    + kwargs["longitude"]
                    + ")%5D"
                )

        elif is_indicator == "false" and is_graph and is_annual:
            if kwargs["num_parameters"] > 3:
                url = (
                    ERDDAP_URL
                    + "/griddap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + kwargs["layer_name"]
                    + "%5B("
                    + kwargs["time_start"]
                    + "):1:("
                    + kwargs["time_finish"]
                    + ")%5D%5B("
                    + str(kwargs["range_value"])
                    + "):1:("
                    + str(kwargs["range_value"])
                    + ")%5D%5B("
                    + kwargs["latMax"]
                    + "):1:("
                    + kwargs["latMin"]
                    + ")%5D%5B("
                    + kwargs["longMax"]
                    + "):1:("
                    + kwargs["longMin"]
                    + ")%5D"
                )

            else:
                url = (
                    ERDDAP_URL
                    + "/griddap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + kwargs["layer_name"]
                    + "%5B("
                    + kwargs["time_start"]
                    + "):1:("
                    + kwargs["time_finish"]
                    + ")%5D%5B("
                    + kwargs["latMax"]
                    + "):1:("
                    + kwargs["latMin"]
                    + ")%5D%5B("
                    + kwargs["longMax"]
                    + "):1:("
                    + kwargs["longMin"]
                    + ")%5D"
                )

        elif is_indicator == "false" and is_graph == False and is_annual:
            if kwargs["num_param"] > 3:
                url = (
                    ERDDAP_URL
                    + "/griddap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + kwargs["layer_name"]
                    + "%5B("
                    + kwargs["date_start"]
                    + "):1:("
                    + kwargs["date_start"]
                    + ")%5D%5B("
                    + str(kwargs["range_value"])
                    + "):1:("
                    + str(kwargs["range_value"])
                    + ")%5D%5B("
                    + kwargs["latitude_start"]
                    + "):1:("
                    + kwargs["latitude_end"]
                    + ")%5D%5B("
                    + kwargs["longitude_start"]
                    + "):1:("
                    + kwargs["longitude_end"]
                    + ")%5D"
                )
            else:
                url = (
                    ERDDAP_URL
                    + "/griddap/"
                    + kwargs["dataset_id"]
                    + ".csv?"
                    + kwargs["layer_name"]
                    + "%5B("
                    + kwargs["date_start"]
                    + "):1:("
                    + kwargs["date_start"]
                    + ")%5D%5B("
                    + kwargs["latitude_start"]
                    + "):1:("
                    + kwargs["latitude_end"]
                    + ")%5D%5B("
                    + kwargs["longitude_start"]
                    + "):1:("
                    + kwargs["longitude_end"]
                    + ")%5D"
                )

        return url
    except Exception as e:
        return str(e)

