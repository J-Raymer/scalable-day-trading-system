FROM python:latest

WORKDIR /app

COPY matching-engine /app/matching-engine
COPY database /app/database

RUN pip install --no-cache-dir -r /app/matching-engine/requirements.txt
ENV PYTHONPATH=/app
EXPOSE ${ME_PORT}

CMD ["fastapi", "run", "./matching-engine/app/main.py"]
