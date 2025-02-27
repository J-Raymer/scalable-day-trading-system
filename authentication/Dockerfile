FROM python:latest

WORKDIR /app

# Copy requirements.txt from the authentication directory to the container
COPY authentication/requirements.txt /app/authentication/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/authentication/requirements.txt

# Copy the whole authentication directory, database, and schemas from the root directory
COPY authentication /app/authentication
COPY database /app/database
COPY schemas /app/schemas

# Run the application
CMD ["python3", "-m", "uvicorn", "authentication.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
