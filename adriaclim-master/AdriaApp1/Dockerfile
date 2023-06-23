FROM python:3.9
# FROM python:3.9-buster
# FROM python:3.8

# Add unstable repo to allow us to access latest GDAL builds
# Existing binutils causes a dependency conflict, correct version will be installed when GDAL gets intalled

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN mkdir /code

WORKDIR /code

RUN echo deb http://deb.debian.org/debian testing main contrib non-free >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get remove -y binutils && \
    apt-get autoremove -y

# Install GDAL dependencies
RUN apt-get install -y libgdal-dev g++ --no-install-recommends && \
    pip install pipenv && \
    pip install whitenoise && \
    pip install gunicorn && \
    apt-get clean -y

# Install PostGIS
# RUN apt-get update && \
#     apt-get install -y postgis postgresql-13-postgis-3-scripts && \
#     apt-get clean -y
# RUN apt-get update && \
#     apt-get install -y postgis && \
#     apt-get clean -y

# Update package list
RUN apt-get update

# RUN apt-cache search postgis
# RUN apt-cache search postgresql-13-postgis-3-scripts

# Install postgis and postgresql-13-postgis-3-scripts
# RUN apt-get install -y postgis postgresql-13-postgis-3-scripts
# RUN apt-get install -y postgis
RUN apt-get install -y postgis=3.3.*
RUN apt-get install -y postgresql

# Clean up after installation
RUN apt-get clean -y


# Update C env vars so compiler can find gdal
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

ENV LC_ALL="C.UTF-8"
ENV LC_CTYPE="C.UTF-8"

COPY . /code

RUN pip install -r requirements.txt