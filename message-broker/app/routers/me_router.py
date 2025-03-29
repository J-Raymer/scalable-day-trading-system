from fastapi import APIRouter, Header, HTTPException
from schemas.common import ErrorResponse, SuccessResponse, RabbitError
from schemas.engine import StockOrder, CancelOrder
from ..core.broker import *

router = APIRouter()
queue_name = "matching-engine"


@router.post(
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
    return await sendRequest(
        x_user_data=x_user_data,
        body=order.model_dump_json(),
        content="STOCK_ORDER",
        q_name=queue_name,
    )


@router.post(
    "/cancelStockTransaction",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def cancelStockOrder(order: CancelOrder, x_user_data: str = Header(None)):
    return await sendRequest(
        x_user_data=x_user_data,
        body=order.model_dump_json(),
        content="CANCEL_ORDER",
        q_name=queue_name,
    )


@router.get("/getStockPrices")
async def getStockPrice():
    return await sendRequest(
        x_user_data="NO_AUTH",
        body="",
        content="GET_PRICES",
        q_name=queue_name,
    )
