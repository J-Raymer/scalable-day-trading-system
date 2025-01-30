FROM python:latest

WORKDIR /app

# Copy everything in the current build context (parent folder) into /app/authorization
COPY authorization /app/authorization
COPY database /app/database

RUN pip install --no-cache-dir -r /app/authorization/requirements.txt
ENV PYTHONPATH=/app
EXPOSE 8000

# Command to run the application
CMD ["fastapi", "run", "./authorization/main.py"]
