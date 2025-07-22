import pandas as pd
import xarray as xr
import time
import requests
import io

# URL dei dati

# dataset 
# url_csv = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/trends_b11c_cc4c_d760.csv?p[(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)][(37.00147):1:(46.97328)][(10.0168):1:(21.98158)],std_error[(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)][(37.00147):1:(46.97328)][(10.0168):1:(21.98158)],signif[(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)][(37.00147):1:(46.97328)][(10.0168):1:(21.98158)],trend[(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)][(37.00147):1:(46.97328)][(10.0168):1:(21.98158)]"
# url_nc = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/trends_b11c_cc4c_d760.nc?p[(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)][(37.00147):1:(46.97328)][(10.0168):1:(21.98158)],std_error[(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)][(37.00147):1:(46.97328)][(10.0168):1:(21.98158)],signif[(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)][(37.00147):1:(46.97328)][(10.0168):1:(21.98158)],trend[(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)][(37.00147):1:(46.97328)][(10.0168):1:(21.98158)]"

# dataset 
# url_csv = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/adriaclim_resm_nemo_historical_3h_T.csv?Latent_Downward_Heat_Flux[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],Longwave_Downward_Heat_Flux[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],Sensible_Downward_Heat_Flux[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],sohefldo[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],sosaline[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],sosfldow[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],soshfldo[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],sossheig[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],sosstsst[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],sowaflup[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],wind_speed_module[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)]"
# url_nc = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/adriaclim_resm_nemo_historical_3h_T.nc?Latent_Downward_Heat_Flux[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],Longwave_Downward_Heat_Flux[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],Sensible_Downward_Heat_Flux[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],sohefldo[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],sosaline[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],sosfldow[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],soshfldo[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],sossheig[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],sosstsst[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],sowaflup[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)],wind_speed_module[(2020-12-31T19:30:00Z):1:(2020-12-31T19:30:00Z)][(39.0):1:(45.875)][(12.0):1:(20.97917)]"

# dataset 
# url_csv = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/veneto_arpa_77db_9452_22ec.csv?TR_trend_1993_2011%5B(1991-09-01T00:00:00Z):1:(1991-09-01T00:00:00Z)%5D%5B(44.79343):1:(45.85434)%5D%5B(11.17736):1:(13.09635)%5D,TR_pvalue_1993_2011%5B(1991-09-01T00:00:00Z):1:(1991-09-01T00:00:00Z)%5D%5B(44.79343):1:(45.85434)%5D%5B(11.17736):1:(13.09635)%5D,TR_avg_1993_2011%5B(1991-09-01T00:00:00Z):1:(1991-09-01T00:00:00Z)%5D%5B(44.79343):1:(45.85434)%5D%5B(11.17736):1:(13.09635)%5D"
# url_nc = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/veneto_arpa_77db_9452_22ec.nc?TR_trend_1993_2011%5B(1991-09-01T00:00:00Z):1:(1991-09-01T00:00:00Z)%5D%5B(44.79343):1:(45.85434)%5D%5B(11.17736):1:(13.09635)%5D,TR_pvalue_1993_2011%5B(1991-09-01T00:00:00Z):1:(1991-09-01T00:00:00Z)%5D%5B(44.79343):1:(45.85434)%5D%5B(11.17736):1:(13.09635)%5D,TR_avg_1993_2011%5B(1991-09-01T00:00:00Z):1:(1991-09-01T00:00:00Z)%5D%5B(44.79343):1:(45.85434)%5D%5B(11.17736):1:(13.09635)%5D"

# dataset
url_csv = "https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/ARPAE_38a7_4089_fd20.csv?time%2Clatitude%2Clongitude%2Ca_95_BO_9_m&time%3E=2021-12-25&time%3C=2022-01-01"
url_nc = "https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/ARPAE_38a7_4089_fd20.nc?time%2Clatitude%2Clongitude%2Ca_95_BO_9_m&time%3E=2021-12-25&time%3C=2022-01-01"
# 1. Download + parsing CSV
start = time.time()
response_csv = requests.get(url_csv)
df_csv = pd.read_csv(io.StringIO(response_csv.text))
tempo_csv = time.time() - start
print(f"Lettura e parsing CSV completati in {tempo_csv:.2f} secondi")
print(f"Shape CSV: {df_csv.shape}")

# 2. Download + parsing NetCDF
start = time.time()
response_nc = requests.get(url_nc)
with open("temp_test.nc", "wb") as f:
    f.write(response_nc.content)
ds_nc = xr.open_dataset("temp_test.nc")
df_nc = ds_nc.to_dataframe().reset_index()
tempo_nc = time.time() - start
print(f"Lettura e parsing NetCDF completati in {tempo_nc:.2f} secondi")
print(f"Shape NetCDF: {df_nc.shape}")
