FROM python:latest

WORKDIR /app

COPY transaction/requirements.txt /app/transaction/requirements.txt
RUN pip install --no-cache-dir -r /app/transaction/requirements.txt

COPY transaction /app/transaction
COPY database /app/database
COPY schemas /app/schemas


CMD ["python3", "-m", "uvicorn", "transaction.main:app", "--host", "0.0.0.0", "--port", "8002", "--proxy-headers"]
