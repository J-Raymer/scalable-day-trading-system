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
import json

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)
import hashlib

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


cache = RedisClient()


### Auth Functions


def generate_token(user: Users):
    expiration = datetime.now() + timedelta(days=1)
    token = jwt.encode(
        {
            "username": user.user_name,
            "name": user.name,
            "id": user.id,
            "exp": expiration,
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    return token


# TODO: If the hash slows things down again we can try using this
async def hash_password(password: str, salt: bytes) -> str:
    return await asyncio.to_thread(
        lambda: hashlib.sha256(salt + password.encode("utf-8")).hexdigest()
    )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


async def validate_token(token: str = Depends(oauth2_scheme)):
    if not token:
        raise ValueError(400, "Token is required")
    try:
        decoded_token = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["exp", "id", "username"]},
        )

        token_dict = {"username": decoded_token["username"], "id": decoded_token["id"]}

        return json.dumps(token_dict)

    except jwt.ExpiredSignatureError:
        raise ValueError(401, "Invalid Token")
    except jwt.InvalidSignatureError:
        raise ValueError(401, "Invalid Token")
    except jwt.MissingRequiredClaimError:
        raise ValueError(400, "Invalid Token")
    except jwt.PyJWTError:
        raise ValueError(400, "Invalid Payload")


async def register_user(user: RegisterRequest):
    async with AsyncSessionLocal() as session:
        if not (user.user_name and user.password and user.name):
            raise ValueError(400, "Invalid Payload")

        # check for an existing user
        query = select(Users).where(
            func.lower(Users.user_name) == func.lower(user.user_name)
        )
        db_result = await session.execute(query)
        existing_user = db_result.one_or_none()
        if existing_user:
            raise ValueError(400, "Invalid Payload")

        # Create a new User in the db
        salt = os.urandom(16)
        # hashed_password = await hash_password(user.password, salt)
        new_user = Users(
            user_name=user.user_name,
            password=hashlib.sha256(salt + user.password.encode("utf-8")).hexdigest(),
            name=user.name,
            salt=salt.hex(),  # Needs to be a string to serialize it in the cache
        )

        session.add(new_user)
        await session.flush()
        await session.refresh(new_user)

        # Create a new wallet in the db
        new_wallet = Wallets(user_id=new_user.id)
        session.add(new_wallet)
        await session.commit()
        await session.refresh(new_user)

        token = generate_token(new_user)

        # Username is unique so use that as the key since on login users don't send a user ID.
        user_dict = {
            new_user.user_name: {
                "id": new_user.id,
                "password": new_user.password,
                "salt": new_user.salt,
                "name": new_user.name,
            }
        }
        cache.set(f"{CacheName.USERS}:{new_user.user_name}", user_dict)
        cache.set(f"{CacheName.WALLETS}:{new_user.id}", {"balance": 0})
        return SuccessResponse(data={"token": token})


async def login_user(user: LoginRequest):
    async with AsyncSessionLocal() as session:
        if not (user.user_name and user.password):
            raise ValueError(400, "Username and password required")

        result = None
        cache_hit = cache.get(f"{CacheName.USERS}:{user.user_name}")
        if cache_hit:
            result = User(user_name=user.user_name, **cache_hit[user.user_name])
        else:
            query = select(Users).where(Users.user_name == user.user_name)
            db_result = await session.execute(query)
            query_result = db_result.one_or_none()
            if query_result:
                result = query_result[0]
            print("CACHE miss in login, result is and user is", result, user.user_name)

        if not result:
            raise ValueError(404, "User not found")
        hashed_password = hashlib.sha256(
            (bytes.fromhex(result.salt) + user.password.encode("utf-8"))
        ).hexdigest()

        if hashed_password != result.password:
            raise ValueError(400, "Invalid Payload")

        token = generate_token(result)
        return SuccessResponse(data={"token": token})
