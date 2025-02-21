FROM python:latest

RUN adduser --disabled-password --gecos "" docker
USER docker

WORKDIR /app

COPY database/requirements.txt /app/database/requirements.txt
RUN pip install --no-warn-script-location --no-cache-dir -r /app/database/requirements.txt

COPY . /app/database

CMD ["python3", "-m", "database.app"]
