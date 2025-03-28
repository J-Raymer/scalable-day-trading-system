from fastapi import APIRouter, Header, HTTPException
from schemas.common import ErrorResponse, SuccessResponse, RabbitError
from schemas.engine import StockOrder, CancelOrder
from ..core.broker import *

router = APIRouter()


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


@router.post(
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


@router.get("/getStockPrices")
async def getStockPrice():

    response = await rpcCall("".encode(), "GET_PRICES", None, "matching-engine")

    if response.content_type == "SUCCESS":

        return SuccessResponse.model_validate_json(response.body.decode())

    error = RabbitError.model_validate_json(response.body.decode())
    raise HTTPException(status_code=error.status_code, detail=error.detail)
