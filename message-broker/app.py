import asyncio
import aio_pika
import sys


async def process_task(message):
    print("callback called")

    # Decode message
    task_data = message.body.decode()

    if message.content_type == "STOCK_ORDER":
        print("stock order received")

    # Process the task (your business logic here)
    print(task_data)
    sys.stdout.flush()


async def main():
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
