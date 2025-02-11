FROM python:latest

WORKDIR /app

COPY matching-engine /app/matching-engine
COPY database /app/database
COPY schemas /app/schemas

RUN pip install --no-cache-dir -r /app/matching-engine/requirements.txt

CMD ["python3", "-m", "uvicorn", "matching-engine.app.main:app", "--host", "0.0.0.0", "--port", "8001"]
