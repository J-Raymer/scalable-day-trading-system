import asyncio
import sys
import os
from fastapi import FastAPI, Header, HTTPException
import aio_pika

app = FastAPI(root_path="/message-broker")

async def process_task(message):
    print("callback called")

    # Decode message
    task_data = message.body.decode()
    user_id = message.headers["user_id"]

    if message.content_type == "STOCK_ORDER":
        print("stock order received")

    # Process the task (your business logic here)
    print("message received", flush=True)
    print(task_data, flush=True)
    # sys.stdout.flush()

@app.on_event("startup")
async def startup():
    # Connect to RabbitMQ
    print("rmq test init")

    attempts = 0
    while attempts < 10:
        try:
            connection = await aio_pika.connect_robust(
                "amqp://guest:guest@rabbitmq:5672/"
            )
        except:
            print("connection failed, retrying")
            await asyncio.sleep(10)
            attempts += 1

        else:
            async with connection:
                channel = await connection.channel()

                # Declare queue
                queue = await channel.declare_queue("testPlaceOrder", auto_delete=True)

                # Start consuming
                await queue.consume(process_task, no_ack=True)

                sys.stdout.flush()

                await asyncio.sleep(10)

                await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
