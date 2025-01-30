FROM python:latest

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r /app/requirements.txt


EXPOSE 8000

# Command to run the application
CMD ["fastapi", "run", "main.py"]
