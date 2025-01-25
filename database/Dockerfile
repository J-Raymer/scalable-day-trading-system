FROM python:latest

RUN adduser --disabled-password --gecos "" docker
USER docker

WORKDIR /app

COPY . /app/database

RUN pip install --no-cache-dir -r /app/database/requirements.txt

# Command to run the application
CMD ["python3", "-m", "database.app"]