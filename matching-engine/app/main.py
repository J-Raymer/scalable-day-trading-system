import redis
import os
import dotenv
from aio_pika.abc import DeliveryMode
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from schemas.common import SuccessResponse, ErrorResponse
from schemas.engine import StockOrder, CancelOrder
from .core import receiveOrder, cancelOrderEngine, getStockPriceEngine
from schemas import exception_handlers
from schemas.RedisClient import RedisClient
import aio_pika
from aio_pika import Message
import asyncio
import sys


app = FastAPI(root_path="/engine")

dotenv.load_dotenv(override=True)
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))

# cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

dotenv.load_dotenv(override=True)
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))

# cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


async def getRabbitConnection():
    return await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")


app.add_exception_handler(
    StarletteHTTPException, exception_handlers.http_exception_handler
)
app.add_exception_handler(
    RequestValidationError, exception_handlers.validation_exception_handler
)

async def process_task(message):
    print("callback called")

    # Decode message
    task_data = message.body.decode()
    user_id = message.headers["user_id"]

    

    if message.content_type == "STOCK_ORDER":
        print("stock order received")
        print(user_id)
        response = receiveOrder(StockOrder.model_validate_json(task_data), user_id) 

        await app.exchange.publish(
            Message(
                body=response.model_dump_json().encode(),
                correlation_id=message.correlation_id,
            ),
            routing_key=message.reply_to
        )

    elif message.content_type == "CANCEL_ORDER":
        print("cancel order received")
        print(user_id)
        response = cancelOrderEngine(CancelOrder.model_validate_json(task_data)) 

        await app.exchange.publish(
            Message(
                body=response.model_dump_json().encode(),
                correlation_id=message.correlation_id,
            ),
            routing_key=message.reply_to
        )


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
                app.channel = await connection.channel()

                # Declare queue
                queue = await app.channel.declare_queue("testPlaceOrder", auto_delete=True)

                app.exchange = app.channel.default_exchange

                

                # Start consuming
                await queue.consume(process_task, no_ack=True)

                

                sys.stdout.flush()

                await asyncio.sleep(10)

                await asyncio.Future()


@app.on_event("shutdown")
async def shutdown():
    await app.rabbitmq_connection.close()


@app.get("/")
async def home():
    return RedirectResponse(url="/engine/docs", status_code=302)


# Rabbitmq test call
@app.get("/rabbit")
async def rabbitTest():
    await app.rabbitmq_channel.default_exchange.publish(
        aio_pika.Message(
            body="Hello World".encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        ),
        routing_key="testQ",
    )


# TODO: Is the below comment still the case? Maybe move to transaction service and cache the prices?
# Don't need this in the matching engine, nice for testing
@app.get("/getStockPrices")
async def getStockPrice():
    return getStockPriceEngine()


@app.post(
    "/cancelStockTransaction",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def cancelStockTransaction(cancelOrder: CancelOrder):
    return cancelOrderEngine(cancelOrder)
