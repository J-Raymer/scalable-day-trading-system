import asyncio
import aio_pika
import json


async def process_task(message):
    print("callback called")

    # Decode message
    task_data = message.body.decode()

    # Process the task (your business logic here)
    print(task_data)


async def main():
    # Connect to RabbitMQ
    print("rmq test init")
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")
    async with connection:
        channel = await connection.channel()

        # Declare queue
        queue = await channel.declare_queue("testQ", auto_delete=True)

        # Start consuming
        await queue.consume(process_task)

        await asyncio.sleep(10)

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
