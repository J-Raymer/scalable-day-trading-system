import jwt
import os
import asyncio
from sqlalchemy import func
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordBearer
from starlette.exceptions import HTTPException as StarletteHTTPException
from database import Users, Wallets
from schemas.common import *
from schemas import exception_handlers
from schemas.RedisClient import RedisClient, CacheName
from .db import get_session, AsyncSessionLocal
import logging
from contextlib import asynccontextmanager
import aio_pika
from .auth import *

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)
import hashlib

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


async def process_task(message):
    global exchange

    if not exchange or not channel:
        print("no exchange exchange")
        return

    task_data = message.body.decode()
    if message.headers:
        user_id = message.headers["user_id"]

    success = "ERROR"
    response = RabbitError(status_code=500, detail="Internal Server Error")
    try:
        if message.content_type == "REGISTER":
            response = await register_user(
                RegisterRequest.model_validate_json(task_data)
            )
        elif message.content_type == "LOGIN":
            response = await login_user(LoginRequest.model_validate_json(task_data))
        elif message.content_type == "VALIDATE":
            await validate_token(task_data)
            response = SuccessResponse()
        success = "SUCCESS"
    except ValueError as e:
        response = RabbitError(status_code=e.args[0], detail=e.args[1])
    except Exception as e:
        raise e
    finally:
        await exchange.publish(
            aio_pika.Message(
                body=response.model_dump_json().encode(),
                correlation_id=message.correlation_id,
                content_type=success,
            ),
            routing_key=message.reply_to,
        )


async def main():
    global exchange, channel, connection

    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")

    async with connection:
        channel = await connection.channel()

        # Declare queue
        queue = await channel.declare_queue("auth", auto_delete=True)

        exchange = channel.default_exchange

        # Start consuming
        await queue.consume(process_task, no_ack=True)

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
