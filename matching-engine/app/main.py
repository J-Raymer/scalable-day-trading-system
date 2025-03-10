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


@app.on_event("startup")
async def startup():
    app.rabbitmq_connection = await getRabbitConnection()
    app.rabbitmq_channel = await app.rabbitmq_connection.channel()

    await app.rabbitmq_channel.declare_queue("testQ", auto_delete=True)
    await app.rabbitmq_channel.declare_queue("testPlaceOrder", auto_delete=True)


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


# engine calls
@app.post(
    "/placeStockOrder",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def placeStockOrder(order: StockOrder, x_user_data: str = Header(None)):

    await app.rabbitmq_channel.default_exchange.publish(
        aio_pika.Message(
            body=order.model_dump_json().encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="STOCK_ORDER",
        ),
        routing_key="testPlaceOrder",
    )

    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split("|")
    return receiveOrder(order, user_id)


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
