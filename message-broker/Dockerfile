FROM python:latest

WORKDIR /app

COPY message-broker /app/message-broker/
RUN pip install --no-cache-dir -r /app/message-broker/requirements.txt
COPY schemas /app/schemas

CMD ["python3", "-m", "uvicorn", "message-broker.main:app", "--host", "0.0.0.0", "--port", "8009", "--proxy-headers"]