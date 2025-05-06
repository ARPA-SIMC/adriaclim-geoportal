FROM python:3.9

# Imposta variabili d'ambiente per evitare problemi di buffer e bytecode
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV LC_ALL="C.UTF-8"
ENV LC_CTYPE="C.UTF-8"

# Crea cartella di lavoro
WORKDIR /code

# Aggiunge i repository e installa GDAL/PostGIS e dipendenze
RUN echo "deb http://deb.debian.org/debian trixie main contrib non-free" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get remove -y binutils && \
    apt-get autoremove -y && \
    apt-get install -y libgdal-dev g++ postgis=3.3.* postgresql --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copia codice sorgente
COPY . /code

# Rende eseguibile lo script entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Installa dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Avvia lo script entrypoint
ENTRYPOINT ["/entrypoint.sh"]