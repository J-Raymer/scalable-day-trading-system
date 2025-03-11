import redis
import os
import dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from schemas.common import SuccessResponse, ErrorResponse
from schemas.engine import StockOrder, CancelOrder
from .core import receiveOrder, cancelOrderEngine, getStockPriceEngine
from schemas import exception_handlers
from schemas.RedisClient import RedisClient

app = FastAPI(root_path="/engine")

dotenv.load_dotenv(override=True)
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))

# cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

app.add_exception_handler(StarletteHTTPException, exception_handlers.http_exception_handler)
app.add_exception_handler(RequestValidationError, exception_handlers.validation_exception_handler)

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
    try:
        username, user_id = x_user_data.split("|")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user data format in headers")
    return await receiveOrder(order, user_id)

# TODO: Is the below comment still the case? Maybe move to transaction service and cache the prices?
# Don't need this in the matching engine, nice for testing
@app.get("/getStockPrices")
async def getStockPrice():
    return await getStockPriceEngine()

@app.post(
    "/cancelStockTransaction",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def cancelStockTransaction(cancelOrder: CancelOrder):
    return await cancelOrderEngine(cancelOrder)
