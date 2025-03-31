from schemas.common import *
from schemas.setup import Stock, StockSetup
from schemas.transaction import AddMoneyRequest
from ..core.broker import *
from fastapi import APIRouter, Header

router = APIRouter()
queue_name = "auth"


@router.get(
    "/validate_token",
    responses={
        200: {"model": SuccessResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
    },
)
async def validate_token(token: str):
    return await sendRequest(
        x_user_data="NO_AUTH",
        body=token,
        content="VALIDATE_TOKEN",
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
async def register(user: RegisterRequest):
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
async def login(user: LoginRequest):
    return await sendRequest(
        x_user_data="NO_AUTH",
        body=user.model_dump_json(),
        content="LOGIN",
        q_name=queue_name,
    )
