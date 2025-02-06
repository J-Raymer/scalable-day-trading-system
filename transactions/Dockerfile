FROM python:latest

WORKDIR /app

COPY transactions /app/transactions
COPY database/models.py /app/transactions

RUN pip install --no-cache-dir -r /app/transactions/requirements.txt
#ENV PYTHONPATH=/app
EXPOSE 8001

CMD ["fastapi", "run", "./transactions/main.py", "--port", "8001"]
