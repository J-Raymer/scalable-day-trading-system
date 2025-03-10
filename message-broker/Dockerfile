FROM python:latest

WORKDIR /app

COPY message-broker /app/message-broker/
RUN pip install --no-cache-dir -r /app/message-broker/requirements.txt

CMD ["python3", "message-broker/app.py"]
