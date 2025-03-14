FROM python:latest

WORKDIR /app

COPY transaction/requirements.txt /app/transaction/requirements.txt
RUN pip install --no-cache-dir -r /app/transaction/requirements.txt

COPY transaction /app/transaction
COPY database/__init__.py /app/database/__init__.py
COPY database/models.py /app/database/models.py
COPY schemas/__init__.py /app/schemas/__init__.py
COPY schemas/common /app/schemas/common
COPY schemas/transaction /app/schemas/transaction
COPY schemas/setup /app/schemas/setup
COPY schemas/exceptions /app/schemas/exceptions
COPY schemas/redis /app/schemas/redis



CMD ["python3", "-m", "uvicorn", "transaction.main:app", "--host", "0.0.0.0", "--port", "8002", "--proxy-headers"]
