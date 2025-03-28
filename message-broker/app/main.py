from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, HTTPException
from schemas.common import SuccessResponse, ErrorResponse, RabbitError
from schemas.engine import CancelOrder
from schemas.engine import StockOrder
from .core.broker import *
from .routers.matching_engine import router as me_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker_setup()

    yield

    await broker_shutdown()


app = FastAPI(root_path="/message-broker", lifespan=lifespan)
app.include_router(me_router)

# engine calls
# @app.post(
#     "/placeStockOrder",
#     responses={
#         200: {"model": SuccessResponse},
#         400: {"model": ErrorResponse},
#         401: {"model": ErrorResponse},
#         403: {"model": ErrorResponse},
#         404: {"model": ErrorResponse},
#     },
# )
# async def placeStockOrder(order: StockOrder, x_user_data: str = Header(None)):
#     if not x_user_data:
#         raise HTTPException(status_code=400, detail="User data is missing in headers")
#     username, user_id = x_user_data.split("|")
#
#     response = await rpcCall(
#         order.model_dump_json().encode(),
#         "STOCK_ORDER",
#         {"user_id": user_id},
#         "matching-engine",
#     )
#
#     if response.content_type == "SUCCESS":
#
#         return SuccessResponse.model_validate_json(response.body.decode())
#
#     error = RabbitError.model_validate_json(response.body.decode())
#     raise HTTPException(status_code=error.status_code, detail=error.detail)


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
