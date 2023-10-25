import pandas as pd
from myFunctions.allFunctions import getIndicatorQueryUrl, download_with_cache_as_csv, packageGraphData, processOperation


# x = 500000
x = 400000

def getDataGraphicGeneric(
    dataset_id,
    adriaclim_timeperiod,
    layer_name,
    time_start,
    time_finish,
    latitude,
    longitude,
    num_parameters,
    range_value,
    is_indicator,
    lat_start,
    long_start,
    lat_end,
    long_end,
    **kwargs
):
    
    try:

        # print("DATASET ID", dataset_id)
        # print("ADRIACLIM TIMEPERIOD", adriaclim_timeperiod)
        # print("LAYER NAME", layer_name)
        # print("TIME START", time_start)
        # print("TIME FINISH", time_finish)
        # print("LATITUDE", latitude)
        # print("LONGITUDE", longitude)
        # # print("NUM PARAMETERS", num_parameters)
        # print("RANGE VALUE", range_value)
        # # print("IS INDICATOR", is_indicator)
        # print("LAT START", lat_start)
        # print("LONG START", long_start)
        # print("LAT END", lat_end)
        # print("LONG END", long_end)
        # print("KWARGS", kwargs)

        # print()
        # print()
        # print()
        # print()


        onlyone = 0
        cache = 0
        if "context" in kwargs and kwargs["context"] == "one":
            onlyone = 1
        if "cache" in kwargs and kwargs["cache"] == "yes":
            cache = 1
        onlylat = None
        onlylong = None
        operation = None

        if "operation" in kwargs and kwargs["operation"] != "":
            operation = kwargs["operation"]

        if lat_start == "no":
            lat_start = latitude
        if lat_end == "no":
            lat_end = latitude
        if long_start == "no":
            long_start = longitude
        if long_end == "no":
            long_end = longitude

        url = getIndicatorQueryUrl(
            dataset_id,
            False,
            False,
            latitude=latitude,
            longitude=longitude,
            latitudeMin=lat_start,
            latitudeMax=lat_end,
            longitudeMin=long_start,
            longitudeMax=long_end,
            range=range_value,
            variable=layer_name,
            format="csv",
            timeMin=time_start,
            timeMax=time_finish,
        )

        # url = "https://erddap.cmcc-opa.eu/erddap/tabledap/RMN_c122_036f_888c.csv?time%2Clatitude%2Clongitude%2Cwd%2Cwv&time%3E=2022-06-14&time%3C=2022-06-14&latitude%3E=41.1402056&latitude%3C=41.1402056&longitude%3E=16.864644444444444&longitude%3C=16.864644444444444"
        # print("ARRIVO QUI")
        # print("PRIMA URL=====")
        if cache == 1:
            url = download_with_cache_as_csv(url)
        if url == "fuoriWms":
            return url
        try:
            df = pd.read_csv(url, dtype="unicode")
            # df = df.dropna(axis=1, how="all")
            # df = df.dropna(how="any", axis=0)
            # if len(df) > x:
            #     # do something
            #     df = df.dropna(how="any", axis=0)

            # print("URL READ CSV =", url)
            # print("DF READ CSV =", df)
        except Exception as e:
            return "fuoriWms"
        if df[layer_name] is not None:
            unit = df[layer_name][0]
        else:
            unit = layer_name
        unit = ""
        df = df.iloc[1:, :]
        # print("DF Test",df.head())
        n_values = len(df)
        allData = []
        values = []
        dates = []
        layerName = []
        lats = []
        longs = []
        i = 0
        # print("ARRIVO QUO")
        # if n_values > x:
        #     # df = df.dropna(axis=1, how="all")
        #     df = df.dropna(how="any", axis=0)

        if n_values <= x:  # all the data
            for index, row in df.iterrows():
                # print("ROW LAYER NAME =", row[layer_name])
                if onlyone == 1 and onlylat is None:
                    onlylat = row["latitude"]
                    onlylong = row["longitude"]

                # assuming df is your dataframe
                # if pd.isna(df.loc[index, layer_name]):
                #     print("IF ISNA NUOVO")
                #     # do something if it's NaN
                # else:
                #     print("IF NOT NAN NUOVO")
                #     # do something else if it's not NaN

                
                if (
                    row[layer_name] == row[layer_name]
                    and row[layer_name] != "NaN"
                    and (
                        onlyone == 0
                        or (onlylat == row["latitude"] and onlylong == row["longitude"])
                    )
                ):
                    # print("IF NOT NAN VECCHIO")
                    lats.insert(i, row["latitude"])
                    longs.insert(i, row["longitude"])
                    layerName.insert(i, layer_name)
                    try:
                        # print("SONO NEL TRY DI VALUES")

                        values.insert(i,float(row[layer_name]))
                    except Exception as e:
                        # print("SONO NEL EXCEPT DI VALUES =",e)

                        values.insert(i,row[layer_name])
                
                    dates.insert(i, row["time"])
                    i += 1
        else:  # one every nvalues/x data
            every_nth_rows = int(n_values / (x - 350000)) # x = 400000 quindi il risultato è 400000 - 350000 = 50000
            df = df[::every_nth_rows]
            for index, row in df.iterrows():
                # print("ROW LAYER NAME =", row[layer_name])
                # if row[layer_name] == row[layer_name] and not pd.isna(df.loc[index, layer_name]) and (onlyone == 0 or (onlylat == row["latitude"] and onlylong == row["longitude"])):
                #     print("NOT NAN")
                #     # do something if it's NaN
                # else:
                #     print("IF NAN NUOVO ELSE")
                #     print("TYPE ROW LAYER NAN =", type(row[layer_name]))
                #     # do something else if it's not NaN

                if onlyone == 1 and onlylat is None:
                    # print("ENTRO NEL ONLYONE IF === 1")
                    onlylat = row["latitude"]
                    onlylong = row["longitude"]
                if (
                    row[layer_name] == row[layer_name]
                    and row[layer_name] != "NaN"
                    and (
                        onlyone == 0
                        or (onlylat == row["latitude"] and onlylong == row["longitude"])
                    )
                ):
                    # print("IF NOT NAN VECCHIO ELSE")
                    lats.insert(i, row["latitude"])
                    longs.insert(i, row["longitude"])
                    layerName.insert(i, layer_name)
                    try:
                        # print("SONO NEL TRY DI VALUES ELSE")
                        values.insert(i,float(row[layer_name]))
                    except Exception as e:
                        # print("SONO NEL EXCEPT DI VALUES ELSE =",e)
                        values.insert(i,row[layer_name])
                    dates.insert(i, row["time"])
                    i += 1
        # print("ARRIVO QUA")
        
        # print("VALUES =", values)
        # print("DATES =", dates)
        # print("UNIT =", unit)
        # print("LAYER NAME =", layerName)
        # print("LATS =", lats)
        # print("LONGS =", longs)

        allData = [values, dates, unit, layerName, lats, longs]
        # print("All data======",allData)
        # print("OPERATION======",operation)
        if operation is None:
            return allData
        else:
            output = None
            if "output" in kwargs:
                output = kwargs["output"]

            return packageGraphData(
                processOperation(operation, values, dates, unit, layerName, lats, longs),
                output=output,
                operation=operation,
                adriaclim_timeperiod=adriaclim_timeperiod,
            )
    except Exception as e:
        print("ECCEZIONE NO WMS ==", e)
        return str(e)
