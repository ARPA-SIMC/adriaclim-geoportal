import os
import io
import pandas as pd
import urllib
import numpy as np
import requests
from django.core.cache import cache


def percentile_new(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = "percentile_%s" % n
    return percentile_

def download_with_cache(u):
    cache_key = u  # needs to be unique
    cache_time = 43200  # time in seconds for cache to be valid (now it is 12 hours)
    output_value = cache.get(key=cache_key)  # returns None if no key-value pair
    # print("output_value: ",output_value)
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
    # print("output_value: ",output_value)
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


