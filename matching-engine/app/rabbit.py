import asyncio
import aio_pika
import json


async def process_task(message):
    # Decode message
    task_data = json.loads(message.body.decode())

    # Process the task (your business logic here)
    print(task_data)


async def main():
    # Connect to RabbitMQ
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    channel = await connection.channel()

    # Declare queue
    queue = await channel.declare_queue("testQ", durable=True)

    # Start consuming
    await queue.consume(process_task)

    try:
        # Keep the worker running
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
