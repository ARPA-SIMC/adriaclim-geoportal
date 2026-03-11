import io
import urllib
import numpy as np
import xarray as xr
import pandas as pd
from AdriaProject.logger_config import setup_logger

from django.core.cache import cache

logger = setup_logger(__name__) 


# def read_erddap_data(url):
#     """
#     Scarica i dati da un URL ERDDAP in formato CSV o NetCDF.
#     NetCDF viene provato prima per griddap, poi fallback a CSV.
#     Per tabledap viene usato solo CSV.
#     Ritorna sempre un DataFrame pandas.
#     """
#     import pandas as pd
#     import xarray as xr
#     import io
#     import urllib.request

#     if "/griddap/" in url:
#         url_nc = url.replace(".csv?", ".nc?")
#         try:
#             ds = xr.open_dataset(url_nc)
#             df = ds.to_dataframe().reset_index()
#             if df.empty:
#                 raise ValueError("NetCDF vuoto")
#             return df
#         except Exception:
#             pass  # Attempt fallback

#     # CSV fallback (for both griddap and tabledap)
#     try:
#         with urllib.request.urlopen(url, timeout=60) as response:
#             text = response.read().decode("utf-8", errors="ignore")
#     except Exception as e:
#         raise e  # Actual error
#     if "nRows = 0" in text or "no matching results" in text:
#         print(f"[ERDDAP] Nessun dato restituito da ERDDAP: {url}")
#         return pd.DataFrame()

#     return pd.read_csv(io.StringIO(text), dtype="unicode")
def read_erddap_data(url):
    """
    Download data from an ERDDAP URL in CSV or NetCDF format.

    For griddap URLs, NetCDF is attempted first, then CSV fallback.
    For tabledap URLs, only CSV is used.

    Returns:
        pandas.DataFrame: Data returned by ERDDAP. An empty DataFrame means
        the request completed successfully but no matching rows were found.

    Raises:
        TimeoutError: ERDDAP request timed out.
        RuntimeError: ERDDAP returned a server-side or temporary error.
        Exception: Any other unexpected error.
    """
    import io
    import pandas as pd
    import xarray as xr
    import urllib.request
    import urllib.error
    import socket

    def _classify_erddap_error(exc, source_url):
        """
        Convert low-level HTTP/network errors into explicit exceptions
        that callers can classify correctly.
        """
        if isinstance(exc, urllib.error.HTTPError):
            status_code = exc.code

            if status_code in (500, 502, 503, 504):
                raise RuntimeError(
                    f"ERDDAP server error ({status_code}) while requesting"
                ) from exc

            if status_code == 429:
                raise RuntimeError(
                    f"ERDDAP rate limit error (429) while requesting"
                ) from exc

            raise RuntimeError(
                f"ERDDAP HTTP error ({status_code}) while requesting"
            ) from exc

        if isinstance(exc, socket.timeout):
            raise TimeoutError(
                f"ERDDAP request timeout while requesting "
            ) from exc

        if isinstance(exc, TimeoutError):
            raise TimeoutError(
                f"ERDDAP request timeout while requesting "
            ) from exc

        raise exc

    if "/griddap/" in url:
        url_nc = url.replace(".csv?", ".nc?")
        try:
            ds = xr.open_dataset(url_nc)
            df = ds.to_dataframe().reset_index()

            if df.empty:
                raise ValueError("NetCDF empty")

            return df

        except Exception as exc:
            # If NetCDF fails because of timeout/server/network issues,
            # we should not silently hide it and pretend it is coverage-related.
            # We only allow fallback for generic format/opening problems.
            if isinstance(exc, (urllib.error.HTTPError, socket.timeout, TimeoutError)):
                _classify_erddap_error(exc, url_nc)

            # NetCDF failed for a non-network reason: try CSV fallback.
            pass

    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            text = response.read().decode("utf-8", errors="ignore")

    except Exception as exc:
        _classify_erddap_error(exc, url)

    if "nRows = 0" in text or "no matching results" in text:
        logger.warning("ERDDAP returned no matching data for URL: %s", url)
        return pd.DataFrame()

    return pd.read_csv(io.StringIO(text), dtype="unicode")



def percentile_new(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = "percentile_%s" % n
    return percentile_

def download_with_cache(u):
    cache_key = u  # needs to be unique
    cache_time = 43200  # time in seconds for cache to be valid (now it is 12 hours)
    output_value = cache.get(key=cache_key)  # returns None if no key-value pair
    if output_value == None:
        # if is none we save it in the cache and returns it
        try:
            output_value = urllib.request.urlopen(cache_key).read()
        except Exception as e:
            return "fuoriWms"
        if output_value:
            output_value = output_value.decode("utf-8")
            cache.set(key=cache_key, value=output_value,timeout=cache_time)
            return output_value
    else:
        return output_value
    
def remove_from_cache(u):
    cache_key = u  # needs to be unique
    output_value = cache.get(key=cache_key)  # returns None if no key-value pair
    if output_value:
        output_value = output_value.decode("utf-8")
        cache.delete(key=cache_key)
        return output_value
    else:
        return None
    
def download_with_cache_as_csv(u):
    try:
        q = download_with_cache(u)
        if q:
            return io.StringIO(q)
        else:
            return None
    except Exception as e:
        return "fuoriWms"


