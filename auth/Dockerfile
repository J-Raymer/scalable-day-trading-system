FROM python:latest

WORKDIR /app

# Copy requirements.txt from the auth directory to the container
COPY auth/requirements.txt /app/auth/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/auth/requirements.txt

# Copy the whole auth directory, database, and schemas from the root directory
COPY auth /app/auth
COPY database/__init__.py /app/database/__init__.py
COPY database/models.py /app/database/models.py
COPY schemas/__init__.py /app/schemas/__init__.py
COPY schemas/common /app/schemas/common
COPY schemas/exceptions /app/schemas/exceptions
COPY schemas/redis /app/schemas/redis


# Run the application
CMD ["python3", "-m", "uvicorn", "auth.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
