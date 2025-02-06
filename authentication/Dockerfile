FROM python:latest

WORKDIR /app

COPY authentication /app/authentication
COPY database /app/database

RUN pip install --no-cache-dir -r /app/authentication/requirements.txt
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["fastapi", "run", "./authentication/main.py"]
