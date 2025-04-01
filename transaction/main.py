import asyncio

from pydantic import ValidationError
from .transactions import *
import os
import dotenv
from aio_pika.abc import DeliveryMode
from schemas.common import SuccessResponse, ErrorResponse, RabbitError
from schemas.engine import StockOrder, CancelOrder
from starlette.exceptions import HTTPException
from schemas.transaction import AddMoneyRequest
from schemas.setup import StockSetup, Stock

# from schemas import exception_handlers
from schemas.RedisClient import RedisClient
import aio_pika
from aio_pika import Message


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
    user_id = message.headers["user_id"]

    success = "ERROR"
    response = RabbitError(status_code=500, detail="Internal Server Error")
    try:
        if message.content_type == "GET_WALLET":
            response = await get_wallet_balance(user_id)
        elif message.content_type == "GET_WALLET_TX":
            response = await get_wallet_transactions(user_id)
        elif message.content_type == "ADD_MONEY":
            response = await add_money_to_wallet(
                AddMoneyRequest.model_validate_json(task_data), user_id
            )
        elif message.content_type == "GET_STOCK_PORTFOLIO":
            response = await get_stock_portfolio(user_id)
        elif message.content_type == "GET_STOCK_TX":
            response = await get_stock_transactions(user_id)
        elif message.content_type == "CREATE_STOCK":
            response = await create_stock(Stock.model_validate_json(task_data), user_id)
        elif message.content_type == "ADD_STOCK":
            response = await add_stock_to_user(
                StockSetup.model_validate_json(task_data), user_id
            )
        success = "SUCCESS"
    except ValueError as e:
        response = RabbitError(status_code=e.args[0], detail=e.args[1])

    except Exception as e:
        raise e
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
    print("main running", flush=True)
    global exchange, channel

    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")

    async with connection:
        channel = await connection.channel()

        # Declare queue
        queue = await channel.declare_queue("transaction", auto_delete=True)

        exchange = channel.default_exchange

        # Start consuming
        await queue.consume(process_task, no_ack=True)

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
