FROM python:latest

WORKDIR /app

COPY authentication /app/authentication
COPY database /app/database
#COPY database/__init__.py /app/database
#COPY database/models.py /app/database
COPY schemas /app/schemas

RUN pip install --no-cache-dir -r /app/authentication/requirements.txt
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["python3", "-m", "uvicorn", "authentication.main:app", "--host", "0.0.0.0", "--port", "8000"]
