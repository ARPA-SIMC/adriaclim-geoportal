import io
import urllib
import numpy as np
import xarray as xr
import pandas as pd

from django.core.cache import cache


def read_erddap_data(url):
    """
    Scarica i dati da un URL ERDDAP in formato CSV o NetCDF,
    scegliendo il formato in automatico: NetCDF per griddap, CSV per tutto il resto.
    Restituisce sempre un DataFrame pandas.
    """
    # Decidi il formato in base al tipo di URL
    if "/griddap/" in url:
        # Prova prima con NetCDF, se fallisce passa a CSV
        url_nc = url.replace('.csv?', '.nc?')
        try:
            ds = xr.open_dataset(url_nc)
            return ds.to_dataframe().reset_index()
        except Exception:
            # fallback a CSV
            return pd.read_csv(url, dtype="unicode")
    else:
        # Per tabledap e altri sempre CSV
        return pd.read_csv(url, dtype="unicode", skiprows=2)


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


