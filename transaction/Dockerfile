FROM python:latest

WORKDIR /app

COPY transaction /app/transaction
COPY database /app/database
COPY schemas /app/schemas

RUN pip install --no-cache-dir -r /app/transaction/requirements.txt

CMD ["python3", "-m", "uvicorn", "transaction.main:app", "--host", "0.0.0.0", "--port", "8002"]
