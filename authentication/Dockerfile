FROM python:latest

WORKDIR /app

COPY authentication/requirements.txt /app/authentication/requirements.txt
RUN pip install --no-cache-dir -r /app/authentication/requirements.txt

COPY authentication /app/authentication
COPY database /app/database
COPY schemas /app/schemas


CMD ["python3", "-m", "uvicorn", "authentication.main:app", "--host", "0.0.0.0", "--port", "8000"]
