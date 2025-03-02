FROM python:latest

WORKDIR /app

COPY rmqtest /app/rmqtest/
RUN pip install --no-cache-dir -r /app/rmqtest/requirements.txt

CMD ["python3", "rmqtest/app.py"]
