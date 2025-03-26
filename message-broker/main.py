import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, HTTPException
from schemas.common import SuccessResponse, ErrorResponse, RabbitError
from schemas.engine import StockOrder, CancelOrder
import aio_pika
import uuid

futures = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global callback_queue, rabbitmq_channel, rabbitmq_connection

    rabbitmq_connection = await getRabbitConnection()
    rabbitmq_channel = await rabbitmq_connection.channel()
    callback_queue = await rabbitmq_channel.declare_queue(exclusive=True)

    await callback_queue.consume(processResponse)

    await rabbitmq_channel.declare_queue("matching-engine", auto_delete=True)

    # waits here until app shutdown
    yield

    if rabbitmq_connection:
        await rabbitmq_connection.close()


app = FastAPI(root_path="/message-broker", lifespan=lifespan)


async def getRabbitConnection():
    return await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")


async def rpcCall(body, content, header, q_name):
    correlation_id = str(uuid.uuid4())
    future = asyncio.Future()
    futures[correlation_id] = future

    await rabbitmq_channel.default_exchange.publish(
        aio_pika.Message(
            body=body,
            headers=header,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type=content,
            correlation_id=correlation_id,
            reply_to=callback_queue.name,
        ),
        routing_key=q_name,
    )

    return await future


async def processResponse(message):
    async with message.process():
        if message.correlation_id in futures:
            future = futures.pop(message.correlation_id)
            future.set_result(message)


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

    response = await rpcCall(
        order.model_dump_json().encode(),
        "STOCK_ORDER",
        {"user_id": user_id},
        "matching-engine",
    )

    if response.content_type == "SUCCESS":

        return SuccessResponse.model_validate_json(response.body.decode())

    error = RabbitError.model_validate_json(response.body.decode())
    raise HTTPException(status_code=error.status_code, detail=error.detail)


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

    response = await rpcCall(
        order.model_dump_json().encode(),
        "CANCEL_ORDER",
        {"user_id": user_id},
        "matching-engine",
    )

    if response.content_type == "SUCCESS":
        return SuccessResponse.model_validate_json(response.body.decode())

    error = RabbitError.model_validate_json(response.body.decode())
    raise HTTPException(status_code=error.status_code, detail=error.detail)


@app.get("/getStockPrices")
async def getStockPrice():

    response = await rpcCall("".encode(), "GET_PRICES", None, "matching-engine")

    if response.content_type == "SUCCESS":

        return SuccessResponse.model_validate_json(response.body.decode())

    error = RabbitError.model_validate_json(response.body.decode())
    raise HTTPException(status_code=error.status_code, detail=error.detail)
