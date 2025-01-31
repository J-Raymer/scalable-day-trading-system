FROM python:latest

WORKDIR /app

COPY authorization /app/authorization
COPY database /app/database

RUN pip install --no-cache-dir -r /app/authorization/requirements.txt
ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["fastapi", "run", "./authorization/main.py"]
