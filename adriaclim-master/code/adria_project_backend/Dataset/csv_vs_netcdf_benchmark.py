import requests
import pandas as pd
import xarray as xr
import time
import json
from io import StringIO
from datetime import datetime


# # === CONFIGURAZIONE ===
# CSV_URL = (
#     "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/"
#     "veneto_arpa_2984_602d_05ad.csv?"
# )

# NETCDF_URL = (
#     "https://thredds.arpa.veneto.it/thredds/dodsC/TDd/nc/"
#     "ARPAV_PRCPTOT_hist_VenetoGrid_monthly_1993_2022.nc"
# )

# SALVA_SU_FILE = True  # Cambia in False se non vuoi creare un report .json


# def test_csv():
#     print(f"\n📥 TEST CSV\n{'-'*40}")
#     start_download = time.time()
#     response = requests.get(CSV_URL)
#     download_time = time.time() - start_download
#     print(f"✔️ Scaricamento completato in: {download_time:.2f}s")

#     start_read = time.time()
#     df = pd.read_csv(StringIO(response.text), dtype="unicode")
#     read_time = time.time() - start_read
#     print(f"✔️ Lettura completata in: {read_time:.2f}s")

#     shape = df.shape
#     print(f"🔢 Dimensioni DataFrame: {shape[0]} righe x {shape[1]} colonne")

#     return {
#         "format": "CSV",
#         "url": CSV_URL,
#         "download_time": download_time,
#         "read_time": read_time,
#         "total_time": download_time + read_time,
#         "shape": {"rows": shape[0], "cols": shape[1]},
#     }


# def test_netcdf():
#     print(f"\n📦 TEST NETCDF\n{'-'*40}")
#     start = time.time()
#     ds = xr.open_dataset(NETCDF_URL)
#     ds.load()  # forza il download dei dati
#     total_time = time.time() - start
#     print(f"✔️ Download + lettura completati in: {total_time:.2f}s")

#     shape = {dim: int(ds.sizes[dim]) for dim in ds.dims}
#     print(f"🔢 Dimensioni Dataset: {shape}")

#     return {
#         "format": "NetCDF",
#         "url": NETCDF_URL,
#         "download_time": total_time,
#         "read_time": 0.0,
#         "total_time": total_time,
#         "shape": shape,
#     }


# def confronta_risultati(csv_data, netcdf_data):
#     print(f"\n📊 CONFRONTO CSV vs NETCDF\n{'='*40}")

#     for result in [csv_data, netcdf_data]:
#         print(f"\n🔹 {result['format']}")
#         print(f"URL: {result['url']}")
#         print(f"⏱ Tempo totale: {result['total_time']:.2f}s")
#         print(f"📥 Download: {result['download_time']:.2f}s")
#         if result["format"] == "CSV":
#             print(f"📄 Lettura CSV: {result['read_time']:.2f}s")
#         print(f"📐 Dimensioni: {result['shape']}")

#     winner = "CSV" if csv_data["total_time"] < netcdf_data["total_time"] else "NetCDF"
#     print(f"\n🏁 FORMATO PIÙ VELOCE: {winner}")

#     return {
#         "benchmark_time": datetime.now().isoformat(),
#         "csv": csv_data,
#         "netcdf": netcdf_data,
#         "winner": winner,
#     }


# def salva_output(report):
#     nome_file = f"benchmark_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
#     with open(nome_file, "w", encoding="utf-8") as f:
#         json.dump(report, f, indent=2)
#     print(f"\n📝 Report salvato in: {nome_file}")


# def run_benchmark():
#     print("\n🚀 AVVIO BENCHMARK COMPLETO CSV VS NETCDF...\n")
#     csv_result = test_csv()
#     netcdf_result = test_netcdf()
#     report = confronta_risultati(csv_result, netcdf_result)

#     if SALVA_SU_FILE:
#         salva_output(report)


# if __name__ == "__main__":
#     run_benchmark()
    
    
 # === CONFIGURAZIONE ===

CSV_URL = (
    "https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/adriaclim_resm_nemo_historical_day_V.csv?"
    "time,depth,latitude,longitude,v"
    "&time>=2020-01-01T00:00:00Z&time<=2020-01-11T00:00:00Z"
    "&depth=0.49402499198913574"
    "&latitude>=43.8&latitude<=44.2"
    "&longitude>=12.4&longitude<=12.8"
)

NETCDF_URL = (
    "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/adriaclim_resm_nemo_historical_day_V.nc?"
    "v[0:1:10][0:1:0][100:1:102][100:1:102]"
)

SALVA_SU_FILE = True


def test_csv():
    print(f"\n📥 TEST CSV\n{'-'*40}")
    start_download = time.time()
    response = requests.get(CSV_URL)
    download_time = time.time() - start_download
    print(f"✔️ Scaricamento completato in: {download_time:.2f}s")

    start_read = time.time()
    df = pd.read_csv(StringIO(response.text), dtype="unicode")
    read_time = time.time() - start_read
    print(f"✔️ Lettura completata in: {read_time:.2f}s")

    shape = df.shape
    print(f"🔢 Dimensioni DataFrame: {shape[0]} righe x {shape[1]} colonne")

    return {
        "format": "CSV",
        "url": CSV_URL,
        "download_time": download_time,
        "read_time": read_time,
        "total_time": download_time + read_time,
        "shape": {"rows": shape[0], "cols": shape[1]},
    }


def test_netcdf():
    print(f"\n📦 TEST NETCDF\n{'-'*40}")
    start = time.time()
    ds = xr.open_dataset(NETCDF_URL)
    ds.load()
    total_time = time.time() - start
    print(f"✔️ Download + lettura completati in: {total_time:.2f}s")

    shape = {dim: int(ds.sizes[dim]) for dim in ds.dims}
    print(f"🔢 Dimensioni Dataset: {shape}")

    return {
        "format": "NetCDF",
        "url": NETCDF_URL,
        "download_time": total_time,
        "read_time": 0.0,
        "total_time": total_time,
        "shape": shape,
    }


def confronta_risultati(csv_data, netcdf_data):
    print(f"\n📊 CONFRONTO CSV vs NETCDF\n{'='*40}")

    for result in [csv_data, netcdf_data]:
        print(f"\n🔹 {result['format']}")
        print(f"URL: {result['url']}")
        print(f"⏱ Tempo totale: {result['total_time']:.2f}s")
        print(f"📥 Download: {result['download_time']:.2f}s")
        if result["format"] == "CSV":
            print(f"📄 Lettura CSV: {result['read_time']:.2f}s")
        print(f"📐 Dimensioni: {result['shape']}")

    winner = "CSV" if csv_data["total_time"] < netcdf_data["total_time"] else "NetCDF"
    print(f"\n🏁 FORMATO PIÙ VELOCE: {winner}")

    return {
        "benchmark_time": datetime.now().isoformat(),
        "csv": csv_data,
        "netcdf": netcdf_data,
        "winner": winner,
    }


def salva_output(report):
    nome_file = f"benchmark_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(nome_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n📝 Report salvato in: {nome_file}")


def run_benchmark():
    print("\n🚀 AVVIO BENCHMARK COMPLETO CSV VS NETCDF...\n")
    csv_result = test_csv()
    netcdf_result = test_netcdf()
    report = confronta_risultati(csv_result, netcdf_result)

    if SALVA_SU_FILE:
        salva_output(report)


if __name__ == "__main__":
    run_benchmark()   
