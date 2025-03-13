import redis
import os
import dotenv
from aio_pika.abc import DeliveryMode
from schemas.common import SuccessResponse, ErrorResponse, RabbitError
from schemas.engine import StockOrder, CancelOrder
from .core import receiveOrder, cancelOrderEngine, getStockPriceEngine
from starlette.exceptions import HTTPException

# from schemas import exception_handlers
from schemas.RedisClient import RedisClient
import aio_pika
from aio_pika import Message
import asyncio


dotenv.load_dotenv(override=True)
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))

exchange = None
channel = None
connection = None


async def process_task(message):
    global exchange

    if not exchange or not channel:
        print("no exchange exchange")
        return

    task_data = message.body.decode()
    if message.headers:
        user_id = message.headers["user_id"]

    if message.content_type == "STOCK_ORDER":
        try:
            response = await receiveOrder(
                StockOrder.model_validate_json(task_data), user_id
            )
            success = "SUCCESS"
        except ValueError as e:
            response = RabbitError(status_code=e.args[0], detail=e.args[1])
            success - "ERROR"
        finally:
            await exchange.publish(
                Message(
                    body=response.model_dump_json().encode(),
                    correlation_id=message.correlation_id,
                    content_type=success,
                ),
                routing_key=message.reply_to,
            )

    elif message.content_type == "CANCEL_ORDER":
        try:
            response = await cancelOrderEngine(
                CancelOrder.model_validate_json(task_data)
            )
            success = "SUCCESS"
        except ValueError as e:
            print("error caught", flush=True)
            response = RabbitError(status_code=e.args[0], detail=e.args[1])
            success = "ERROR"
        finally:
            await exchange.publish(
                Message(
                    body=response.model_dump_json().encode(),
                    correlation_id=message.correlation_id,
                    content_type=success,
                ),
                routing_key=message.reply_to,
            )

    elif message.content_type == "GET_PRICES":
        try:
            response = await getStockPriceEngine()
            success = "SUCCESS"
        except ValueError as e:
            response = RabbitError(status_code=e.args[0], detail=e.args[1])
            success = "ERROR"
        finally:
            await exchange.publish(
                Message(
                    body=response.model_dump_json().encode(),
                    correlation_id=message.correlation_id,
                    content_type=success,
                ),
                routing_key=message.reply_to,
            )


async def main():
    # Connect to RabbitMQ
    global exchange, channel

    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")

    async with connection:
        channel = await connection.channel()

        # Declare queue
        queue = await channel.declare_queue("testPlaceOrder", auto_delete=True)

        exchange = channel.default_exchange

        # Start consuming
        await queue.consume(process_task, no_ack=True)

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
