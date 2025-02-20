from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from schemas.common import SuccessResponse, ErrorResponse
from schemas.engine import StockOrder, CancelOrder
from schemas.setup import StockSetup
from .core import receiveOrder, cancelOrderEngine, getStockPriceEngine


app = FastAPI(root_path="/engine")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    raise HTTPException(status_code=400, detail="Invalid Payload")


@app.get("/")
async def home():
    return RedirectResponse(url="/engine/docs", status_code=302)


# engine calls
@app.post(
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
    return receiveOrder(order, user_id)


# Dont need this in the matching engine, nice for testing
@app.get("/getStockPrices")
async def getStockPrice():
    return getStockPriceEngine()


@app.post(
    "/cancelStockTransaction",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def cancelStockTransaction(cancelOrder: CancelOrder):
    return cancelOrderEngine(cancelOrder)
