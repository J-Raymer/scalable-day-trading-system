import asyncio
import sys
import os
from fastapi import FastAPI, Header, HTTPException
from schemas.common import SuccessResponse, ErrorResponse
from schemas.engine import StockOrder, CancelOrder
import aio_pika

app = FastAPI(root_path="/message-broker")

async def getRabbitConnection():
    return await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")



@app.on_event("startup")
async def startup():
    app.rabbitmq_connection = await getRabbitConnection()
    app.rabbitmq_channel = await app.rabbitmq_connection.channel()

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

    await app.rabbitmq_channel.default_exchange.publish(
        aio_pika.Message(
            body=order.model_dump_json().encode(),
            headers={"user_id" : user_id},
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="STOCK_ORDER",
        ),
        routing_key="testPlaceOrder",
    )
    #return receiveOrder(order, user_id)
