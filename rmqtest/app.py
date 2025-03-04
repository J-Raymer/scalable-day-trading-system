import asyncio
import aio_pika
import json
import logging
import sys


async def process_task(message):
    print("callback called")

    # Decode message
    task_data = message.body.decode()

    # Process the task (your business logic here)
    print(task_data)
    sys.stdout.flush()


async def main():
    # logging.basicConfig(level=logging.DEBUG)
    # Connect to RabbitMQ
    print("rmq test init")

    attempts = 0
    try:
        connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")
    except:
        print("connection failed, retrying")
        await asyncio.sleep(10)
        attempts += 1

        if attempts > 10:
            print("connection failed")
            return

    async with connection:
        channel = await connection.channel()

        # Declare queue
        queue = await channel.declare_queue("testQ", auto_delete=True)

        # Start consuming
        await queue.consume(process_task)

        sys.stdout.flush()

        await asyncio.sleep(10)

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
