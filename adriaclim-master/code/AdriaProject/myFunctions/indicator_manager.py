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


def getIndicatorQueryUrl(ind: Node, onlyFirstVariable: bool, skipDimensions: bool, **kwargs) -> str:
    """Construct the query URL for the indicator."""
    if isinstance(ind, str):
        ind = getIndicator(ind)

    base_url = getIndicatorBaseUrl(ind)
    if not base_url:
        return ""

    data_format = getIndicatorDataFormat(ind)
    griddap = data_format == "griddap"

    variables = getIndicatorVariables(ind) or []
    dimensions = [] if skipDimensions else (getIndicatorDimensions(ind) or [])

    if griddap and onlyFirstVariable and len(variables) > 1:
        variables = [variables[0]]

    if griddap and "variable" in kwargs:
        variables = [kwargs["variable"]]

    query = buildQueryString(variables, dimensions, griddap, **kwargs)
    result = f"{base_url}.{kwargs.get('format', 'csv')}{query}"

    return result.replace("None", "0")


def getIndicatorQueryUrlPoint(
    ind: Node, onlyFirstVariable: bool, skipDimensions: bool, lat: str, lon: str, time: str, range: str, **kwargs
) -> str:
    """Construct the query URL for a specific point."""
    return getIndicatorQueryUrl(
        ind,
        onlyFirstVariable,
        skipDimensions,
        latitude=lat,
        longitude=lon,
        time=time,
        range=range,
        **kwargs,
    )


def url_is_indicator(is_indicator: bool, is_graph: bool, is_annual: bool, **kwargs) -> str:
    """Construct the URL for an indicator or graph."""
    params = {key: kwargs[key] for key in ["dataset_id", "time_start", "time_finish", "latitude", "longitude", "num_parameters", "range_value"] if key in kwargs}
    base_url = ERDDAP_URL

    if is_indicator:
        time_range = "[2020-01-01T00:00:00Z):1:(2020-12-31T00:00:00Z]" if is_annual else "[2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z]"
        url = f"{base_url}/griddap/{params['dataset_id']}.csv?{params['range_value']}{time_range}[({params['latitude']}):1:({params['latitude']})][({params['longitude']}):1:({params['longitude']})]"
    else:
        query_string = urlencode(params)
        url = f"{base_url}/griddap/{params['dataset_id']}.csv?{query_string}" if is_graph else f"{base_url}/griddap/{params['dataset_id']}.csv"

    return url


