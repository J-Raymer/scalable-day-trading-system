import asyncio
import sys
import os
from fastapi import FastAPI, Header, HTTPException
from schemas.common import SuccessResponse, ErrorResponse
from schemas.engine import StockOrder, CancelOrder
import aio_pika
import uuid

app = FastAPI(root_path="/message-broker")

futures = {}

async def getRabbitConnection():
    return await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")

async def rpcCall(body, content, header):
    correlation_id = str(uuid.uuid4())
    future = asyncio.Future()
    futures[correlation_id] = future

    await app.rabbitmq_channel.default_exchange.publish(
        aio_pika.Message(
            body=body,
            headers=header,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type=content,
            correlation_id=correlation_id,
            reply_to=app.callback_queue.name
        ),
        routing_key="testPlaceOrder",
    )

    return await future

async def processResponse(message):
    async with message.process():
        if message.correlation_id in futures:
            future = futures.pop(message.correlation_id)
            future.set_result(message.body)



@app.on_event("startup")
async def startup():
    app.rabbitmq_connection = await getRabbitConnection()
    app.rabbitmq_channel = await app.rabbitmq_connection.channel()
    app.callback_queue = await app.rabbitmq_channel.declare_queue(exclusive=True)
    app.messageQ = asyncio.Queue()

    await app.callback_queue.consume(processResponse)

    #print("startup", flush=True)

    await app.rabbitmq_channel.declare_queue("testPlaceOrder", auto_delete=True)

@app.on_event("shutdown")
async def shutdown():
    await app.rabbitmq_connection.close()

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
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split("|")

    response = await rpcCall(order.model_dump_json().encode(), "STOCK_ORDER", {"user_id" : user_id})

    return SuccessResponse.model_validate_json(response.decode())


@app.post(
    "/cancelStockTransaction",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def cancelStockOrder(order: CancelOrder, x_user_data: str = Header(None)):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split("|")

    response = await rpcCall(order.model_dump_json().encode(), "CANCEL_ORDER", {"user_id" : user_id})

    return SuccessResponse.model_validate_json(response.decode())

@app.get("/getStockPrices")
async def getStockPrice():

    response = await rpcCall("".encode(), "GET_PRICES", None)

    return SuccessResponse.model_validate_json(response.decode())
    