from schemas.common import *
from schemas.setup import Stock, StockSetup
from schemas.transaction import AddMoneyRequest
from ..core.broker import *
from fastapi import APIRouter, Header, Depends
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
queue_name = "auth"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


@router.get(
    "/validate_token",
    responses={
        200: {"model": SuccessResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
    },
)
async def validate_token(token: str = Depends(oauth2_scheme)):
    return await sendRequest(
        x_user_data="NO_AUTH",
        body=token,
        content="VALIDATE",
        q_name=queue_name,
    )


@router.post(
    "/register",
    status_code=201,
    responses={
        201: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def register_user(user: RegisterRequest):
    return await sendRequest(
        x_user_data="NO_AUTH",
        body=user.model_dump_json(),
        content="REGISTER",
        q_name=queue_name,
    )


@router.post(
    "/login",
    responses={
        200: {"model": LoginResponse},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def login_user(user: LoginRequest):
    return await sendRequest(
        x_user_data="NO_AUTH",
        body=user.model_dump_json(),
        content="LOGIN",
        q_name=queue_name,
    )
