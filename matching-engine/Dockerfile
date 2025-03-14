FROM python:latest

WORKDIR /app

COPY matching-engine /app/matching-engine
COPY schemas /app/schemas
COPY database /app/database

RUN pip install --no-cache-dir -r /app/matching-engine/requirements.txt


CMD ["python3", "-m", "matching-engine.app.main"]
