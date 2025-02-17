from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import RedirectResponse
from uuid import UUID
from schemas.common import SuccessResponse, ErrorResponse
from schemas.engine import StockOrder
from .core import receiveOrder, cancelOrder, getUserFromId, getAllUsers

app = FastAPI(root_path="/engine")


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
    username, user_id = x_user_data.split('|')
    return receiveOrder(order, user_id)


# TEST CALL
@app.post("/getUserFromId")
async def getUser(x_user_data: str = Header(None)):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split('|')
    return getUserFromId(user_id)


# TEST CALL
@app.get("/getUsers")
async def getUsers():
    return getAllUsers()


@app.post(
    "/cancelStockTransaction",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def cancelStockTransaction(stockID: str):
    return cancelOrder()
