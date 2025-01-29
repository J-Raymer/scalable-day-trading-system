FROM python:latest

RUN adduser --disabled-password --gecos "" docker
USER docker

WORKDIR /app

COPY . /app/database

# Ignore warning about the env path
RUN pip install --no-warn-script-location --no-cache-dir -r /app/database/requirements.txt
