from Dataset.models import Node
from AdriaProject.settings import ERDDAP_URL
from urllib.parse import urlencode
from typing import Optional, List


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

def getIndicatorQueryUrl(ind, onlyFirstVariable, skipDimensions, **kwargs):
    if type(ind) == str:
        ind = getIndicator(ind)

    # print("INDICATOR ========",ind)
    url = getIndicatorBaseUrl(ind)

    # print("URL GET INDICATOR QUERY URL ========",url)
    if "format" in kwargs and kwargs["format"] is not None:
        url = url + "." + safe_str(kwargs.get("format"))

    di = getIndicatorDimensions(ind)
    # print("All dimensions=======",di)

    va = getIndicatorVariables(ind)
    # print("All VARIABLES=========",va)

    selVar = [kwargs["variable"]]

    tipo = getIndicatorDataFormat(ind)

    griddap = tipo == "griddap"

    if griddap and onlyFirstVariable and va.count() > 1:
        va = [va[0]]

    if griddap and "variable" in kwargs:
        va = [kwargs["variable"]]

    if skipDimensions:
        di = []
    
    # va = selVar       

    query = "?"

    if griddap:
        for v in va:
            # print("VARIABLE GRIDDAP:",v)

            if query != "?":
                query = query + ","
            query = query + v
            for d in di:
                query = query + "%5B("

                if d in kwargs and not (d + "Min") in kwargs:
                    query = query + kwargs[d]
                elif (d + "Min") in kwargs:
                    query = query + kwargs[d + "Min"]
                else:
                    alias = getVariableAliases(d)
                    # print("Alias ========",alias)
                    for al in alias:
                        if al in kwargs:
                            query = query + kwargs[al]
                        elif (al + "Min") in kwargs:
                            query = query + kwargs[al + "Min"]

                query = query + "):1:("

                if d in kwargs and not (d + "Max") in kwargs:
                    query = query + kwargs[d]
                elif (d + "Max") in kwargs:
                    query = query + kwargs[d + "Max"]
                else:
                    alias = getVariableAliases(d)

                    for al in alias:
                        if al in kwargs:  
                            query = query + kwargs[al]
                        elif (al + "Max") in kwargs:
                            query = query + kwargs[al + "Max"]

                query = query + ")%5D"

    else:
        for v in va:
            # print("VARIABLE TABLEDAP:",v)
            # print("URL + QUERY =", url + query)
            if query != "?":
                query = query + "%2C"
            query = query + v

        for d in va:
            if d.lower().find("time") != -1 or d == "latitude" or d == "longitude":
            # if d != "Indicator":
                if d in kwargs and not (d + "Min") in kwargs:
                    query = query + "&" + d + "%3E=" + kwargs[d]
                elif (d + "Min") in kwargs:
                    query = query + "&" + d + "%3E=" + kwargs[d + "Min"]
                else:
                    alias = getVariableAliases(d)
                    # print("alias",alias)
                    for al in alias:
                        if al in kwargs:
                            query = query + "&" + d + "%3E=" + kwargs[al]
                        elif (al + "Min") in kwargs:
                            query = query + "&" + d + "%3E=" + kwargs[al + "Min"]

                if d in kwargs and not (d + "Max") in kwargs:
                    query = query + "&" + d + "%3C=" + kwargs[d]
                elif (d + "Max") in kwargs:
                    query = query + "&" + d + "%3C=" + kwargs[d + "Max"]
                else:
                    alias = getVariableAliases(d)
                    for al in alias:
                        if al in kwargs:
                            query = query + "&" + d + "%3C=" + kwargs[al]
                        elif (al + "Max") in kwargs:
                            query = query + "&" + d + "%3C=" + kwargs[al + "Max"]

    result = url + query
    # print("URL + QUERY =", url + query)
    if result.find("None") != -1:
        result = result.replace("None","0")
    
    print("final result =", result)
    # https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/EOBS_a583_d8f2_21c0.json?very_wet_days_wrt_95th_percentile_of_reference_period%5B(2020-12-31T00:00:00Z):1:(2020-12-31T00:00:00Z)%5D%5B(46.94985982579791):1:(46.94985982579791)%5D%5B(21.94986030317809):1:(21.94986030317809)%5D
    return result


def url_is_indicator(is_indicator, is_graph, is_annual, **kwargs):
    # true, true, false
    try:
        # print("ENTRO IN URL_IS_INDICATOR LATO TABLEDAP!")
        # print("IS INDICATOR=====", is_indicator)
        # print("IS GRAPH=====", is_graph)
        # print("IS ANNUAL=====", is_annual)
        if is_indicator == "true" and is_graph == False:
            #print("ENTRO IN URL_IS_INDICATOR LATO TABLEDAP!")
            # print("DENTRO IND TRUE IS GRAPH FALSE")
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
            # print("DENTRO IND TRUE IS GRAPH TRUE IS ANNUAL TRUE")
            try:
                #print("Entro qui parte 2!!!!!!")
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
                print("Eccezione 2", e1)
                return str(e1)
        elif is_indicator == "true" and is_graph and not is_annual:
            # print("DENTRO IND TRUE IS GRAPH TRUE IS ANNUAL FALSE")
            #  url = url_is_indicator(is_indicator,True,False,dataset_id=dataset_id,layer_name=layer_name,time_start=date_start,time_finish=date_end,latitude=str(point[0]),
            #                     longitude=str(point[1]),num_parameters=num_param,range_value=range_value)
            # https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/indicators_wsdi_aba0_0062_8939.csv?time%2Clatitude%2Clongitude%2Cwsdi&time%3E=2021-07-01&time%3C=2050-07-01&latitude%3E=39.688777923584&latitude%3C=41.22824901518532&longitude%3E=14.740385055542&longitude%3C=15.183105468750002
            # https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/arpav_PRCPTOT_yearly.htmlTable?time%2Clatitude%2Clongitude%2CIndicator&time%3E=2021-12-25&time%3C=2022-01-01
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
            # print("DENTRO IND FALSE IS GRAPH FALSE IS ANNUAL FALSE")
            if kwargs["num_param"] > 3:
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
                    + kwargs["time_start"]
                    + "):1:("
                    + kwargs["time_finish"]
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

        elif is_indicator == "false" and is_graph and is_annual == False:
            # print("DENTRO IND FALSE IS GRAPH TRUE IS ANNUAL FALSE")
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
            # print("DENTRO IND FALSE IS GRAPH TRUE IS ANNUAL TRUE")
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
            # print("DENTRO IND FALSE IS GRAPH FALSE IS ANNUAL TRUE")
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
        print("Error", e)
        return str(e)

