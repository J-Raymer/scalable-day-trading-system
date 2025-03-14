FROM python:latest

WORKDIR /app

COPY matching-engine/requirements.txt /app/matching-engine/requirements.txt
RUN pip install --no-cache-dir -r /app/matching-engine/requirements.txt

COPY matching-engine /app/matching-engine
COPY database/__init__.py /app/database/__init__.py
COPY database/models.py /app/database/models.py
COPY schemas/__init__.py /app/schemas/__init__.py
COPY schemas/common /app/schemas/common
COPY schemas/engine /app/schemas/engine
COPY schemas/exceptions /app/schemas/exceptions
COPY schemas/redis /app/schemas/redis


CMD ["python3", "-m", "uvicorn", "matching-engine.app.main:app", "--host", "0.0.0.0", "--port", "8001", "--proxy-headers"]
