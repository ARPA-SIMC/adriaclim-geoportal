# FROM python:3.9

# # Imposta variabili d'ambiente per evitare problemi di buffer e bytecode
# ENV PYTHONUNBUFFERED=1
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
# ENV C_INCLUDE_PATH=/usr/include/gdal
# ENV LC_ALL="C.UTF-8"
# ENV LC_CTYPE="C.UTF-8"

# # Crea cartella di lavoro
# WORKDIR /code

# # Aggiunge i repository e installa GDAL/PostGIS e dipendenze
# RUN echo "deb http://deb.debian.org/debian trixie main contrib non-free" >> /etc/apt/sources.list && \
#     apt-get update && \
#     apt-get remove -y binutils && \
#     apt-get autoremove -y && \
#     apt-get install -y libgdal-dev g++ postgis=3.3.* postgresql --no-install-recommends && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# # Copia codice sorgente
# COPY . /code

# # Rende eseguibile lo script entrypoint
# COPY entrypoint.sh /entrypoint.sh
# RUN chmod +x /entrypoint.sh


# # Installa dipendenze Python
# RUN pip install --no-cache-dir -r requirements.txt

# # Avvia lo script entrypoint
# ENTRYPOINT ["/entrypoint.sh"]

FROM python:3.9-bookworm

# Env utili e niente .pyc
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal \
    LC_ALL="C.UTF-8" \
    LC_CTYPE="C.UTF-8"

WORKDIR /code

# Sorgenti APT pulite + pacchetti coerenti con bookworm (PG15 + PostGIS 3.x)
RUN set -eux; \
    rm -f /etc/apt/sources.list.d/*; \
    printf '%s\n' \
      'deb http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware' \
      'deb http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware' \
      'deb http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware' \
      > /etc/apt/sources.list; \
    apt-get update; \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      g++ \
      libgdal-dev gdal-bin \
      postgresql-15 postgresql-15-postgis-3 postgresql-contrib \
      libpq-dev postgresql-client \
    ; \
    apt-get clean; rm -rf /var/lib/apt/lists/*

# Prima requirements (cache-friendly)
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Poi il resto del codice
COPY . /code

# Entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
