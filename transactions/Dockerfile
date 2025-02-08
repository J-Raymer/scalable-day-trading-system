FROM python:latest

WORKDIR /app

COPY transactions /app/transactions
COPY database /app/database
COPY schemas /app/schemas

RUN pip install --no-cache-dir -r /app/transactions/requirements.txt

EXPOSE 8001

CMD ["python3", "-m", "uvicorn", "transactions.main:app", "--host", "0.0.0.0", "--port", "8001"]
