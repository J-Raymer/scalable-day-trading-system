import asyncio
import sys
import os
from fastapi import FastAPI, Header, HTTPException
from schemas.common import SuccessResponse, ErrorResponse
from schemas.engine import StockOrder, CancelOrder
import aio_pika
import uuid

app = FastAPI(root_path="/message-broker")

async def getRabbitConnection():
    return await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")



@app.on_event("startup")
async def startup():
    app.rabbitmq_connection = await getRabbitConnection()
    app.rabbitmq_channel = await app.rabbitmq_connection.channel()

    #print("startup", flush=True)

    await app.rabbitmq_channel.declare_queue("testPlaceOrder", auto_delete=True)

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

    callback_queue = await app.rabbitmq_channel.declare_queue(exclusive=True)
    #loop = asyncio.get_running_loop()
    #future = loop.create_future()
    correlation_id = str(uuid.uuid4())

    await app.rabbitmq_channel.default_exchange.publish(
        aio_pika.Message(
            body=order.model_dump_json().encode(),
            headers={"user_id" : user_id},
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="STOCK_ORDER",
            correlation_id=correlation_id,
            reply_to=callback_queue.name
        ),
        routing_key="testPlaceOrder",
    )

    messageQ = asyncio.Queue()

    async def printResponse(message):
        print(message.body, flush=True)

        await messageQ.put(message.body)

    
    await callback_queue.consume(printResponse)

    data = await asyncio.wait_for(messageQ.get(), timeout=5.0)


    return SuccessResponse.model_validate_json(data)
    #return receiveOrder(order, user_id)
