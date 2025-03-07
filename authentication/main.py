import bcrypt
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
from .db import get_session

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

app = FastAPI(root_path="/authentication")

cache = RedisClient()

app.add_exception_handler(StarletteHTTPException, exception_handlers.http_exception_handler)
app.add_exception_handler(RequestValidationError, exception_handlers.validation_exception_handler)



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


async def hash_password(password: str, salt: bytes):
    return (await asyncio.to_thread(bcrypt.hashpw, password.encode("utf-8"), salt)).decode("utf-8")



## Auth Routes

@app.get("/")
async def home():
    return RedirectResponse(url="/authentication/docs", status_code=302)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

@app.get(
    "/validate_token",
    responses={
        200: {"model": SuccessResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
    },
)
async def validate_token(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")
    try:
        decoded_token = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["exp", "id", "username"]},
        )
        return {"username": decoded_token["username"], "id": decoded_token["id"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Invalid Token")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Invalid Token")
    except jwt.MissingRequiredClaimError:
        raise HTTPException(status_code=400, detail="Invalid Token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid Payload")

@app.post(
    "/register",
    status_code=201,
    responses={
        201: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def register(user: RegisterRequest, session: AsyncSession = Depends(get_session)):
    if not (user.user_name and user.password and user.name):
        raise HTTPException(
            status_code=400, detail="Invalid Payload"
        )

    # check for an existing user
    query = select(Users).where(
        func.lower(Users.user_name) == func.lower(user.user_name)
    )
    db_result = await session.execute(query)
    existing_user = db_result.one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Invalid Payload")


    # Create a new User in the db
    salt = bcrypt.gensalt()
    hashed_password = await hash_password(user.password, salt)
    new_user = Users(
        user_name=user.user_name,
        password=hashed_password,
        name=user.name,
        salt=salt.decode("utf-8"),
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
            "name": new_user.name
        }}
    cache.set(f'{CacheName.USERS}:{new_user.user_name}',user_dict)
    cache.set(f'{CacheName.WALLETS}:{new_user.id}',{"balance": 0})
    return SuccessResponse(data={"token": token})


@app.post(
    "/login",
    responses={
        200: {"model": LoginResponse},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def login(user: LoginRequest, session: AsyncSession = Depends(get_session)):
    if not (user.user_name and user.password):
        raise HTTPException(status_code=400, detail="Username and password required")

    result = None
    cache_hit = cache.get(f'{CacheName.USERS}:{user.user_name}')
    if cache_hit:
        print("CACHE hit in login")
        result = User(user_name=user.user_name, **cache_hit[user.user_name])
    else:
        query = select(Users).where(Users.user_name == user.user_name)
        db_result = await session.execute(query)
        result = db_result.one_or_none()

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = await hash_password(user.password, result.salt.encode("utf-8"))

    if hashed_password != result.password:
        raise HTTPException(status_code=400, detail="Invalid Payload")

    token = generate_token(result)
    return SuccessResponse(data={"token": token})
