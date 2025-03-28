import aio_pika
import asyncio
import uuid
from fastapi import HTTPException
from schemas.common import SuccessResponse, RabbitError
from pydantic import ValidationError

futures = {}


async def sendRequest(x_user_data, body, content, q_name):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")

    if x_user_data == "NO_AUTH":
        user_id = ""
        header_data = {}
    else:
        username, user_id = x_user_data.split("|")
        header_data = {"user_id": user_id}

    response = await rpcCall(
        body=body.encode(),
        content=content,
        header=header_data,
        q_name=q_name,
    )

    if response.content_type == "SUCCESS":
        return SuccessResponse.model_validate_json(response.body.decode())

    error = RabbitError.model_validate_json(response.body.decode())
    raise HTTPException(status_code=error.status_code, detail=error.detail)


async def getRabbitConnection():
    return await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")


async def broker_setup():
    global callback_queue, rabbitmq_channel, rabbitmq_connection

    rabbitmq_connection = await getRabbitConnection()
    rabbitmq_channel = await rabbitmq_connection.channel()
    callback_queue = await rabbitmq_channel.declare_queue(exclusive=True)

    await callback_queue.consume(processResponse)

    await rabbitmq_channel.declare_queue("matching-engine", auto_delete=True)
    await rabbitmq_channel.declare_queue("transaction", auto_delete=True)


async def broker_shutdown():
    await rabbitmq_connection.close()


async def processResponse(message):
    async with message.process():
        if message.correlation_id in futures:
            future = futures.pop(message.correlation_id)
            future.set_result(message)
        else:
            raise ValidationError("error recieving response")


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
