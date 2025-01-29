FROM python:latest

WORKDIR /app

COPY authorization/ .

RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
