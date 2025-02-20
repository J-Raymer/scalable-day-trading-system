import bcrypt
import dotenv
import jwt
import os
import sqlmodel
from sqlmodel import func
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from database import Users
from schemas.common import *

dotenv.load_dotenv(override=True)
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("DB_NAME")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
url = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

engine = sqlmodel.create_engine(url)
app = FastAPI(root_path="/authentication")


def generate_token(user: Users):
    expiration = datetime.now() + timedelta(days=1)
    token = jwt.encode(
        {
            "username": user.user_name,
            "name": user.name,
            "id": str(user.id),
            "exp": expiration,
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    return token

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    raise HTTPException(status_code=400, detail="Invalid Payload")

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
        raise HTTPException(status_code=401, detail="Expired Token")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=403, detail="Unauthorized")
    except jwt.MissingRequiredClaimError:
        raise HTTPException(status_code=400, detail="Missing required claim")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post(
    "/register",
    status_code=201,
    responses={
        201: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def register(user: RegisterRequest):
    if not (user.user_name and user.password and user.name):
        raise HTTPException(
            status_code=400, detail="Username, name and password required"
        )

    with sqlmodel.Session(engine) as session:
        query = sqlmodel.select(Users).where(
            func.lower(Users.user_name) == func.lower(user.user_name)
        )
        existing_user = session.exec(query).one_or_none()

        if existing_user:
            raise HTTPException(status_code=409, detail="Username already exists")

        salt = bcrypt.gensalt()
        new_user = Users(
            user_name=user.user_name,
            password=bcrypt.hashpw(user.password.encode("utf-8"), salt).decode("utf-8"),
            name=user.name,
            salt=salt.decode("utf-8"),
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        token = generate_token(new_user)
        return SuccessResponse(data={"token": token})


@app.post(
    "/login",
    responses={
        200: {"model": LoginResponse},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def login(user: LoginRequest):
    if not (user.user_name and user.password):
        raise HTTPException(status_code=400, detail="Username and password required")

    with sqlmodel.Session(engine) as session:
        query = sqlmodel.select(Users).where(Users.user_name == user.user_name)
        result = session.exec(query).one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="User not found")

        hashed_password = bcrypt.hashpw(
            user.password.encode("utf-8"), result.salt.encode("utf-8")
        ).decode("utf-8")
        if hashed_password != result.password:
            raise HTTPException(status_code=401, detail="Unauthorized")
    token = generate_token(result)
    return SuccessResponse(data={"token": token})
