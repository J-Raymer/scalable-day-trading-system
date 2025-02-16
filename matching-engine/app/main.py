from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID
from schemas.common import SuccessResponse, ErrorResponse, User
from schemas.engine import StockOrder
from .core import receiveOrder, cancelOrder, clearSellOrders

app = FastAPI(
    root_path="/engine"
)


@app.get("/")
async def home():
    return RedirectResponse(url="/engine/docs", status_code=302)


# engine calls
@app.post("/placeStockOrder", responses={
    200: {"model": SuccessResponse},
    400: {"model": ErrorResponse},
    401: {"model": ErrorResponse},
    403: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
})
async def placeStockOrder(order: StockOrder, user: User): # REMOVE AFTER TESTING= Depends(verify_token)):
    return receiveOrder(order, user)


@app.post("/cancelStockTransaction", responses={
    200: {"model": SuccessResponse},
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
})
async def cancelStockTransaction(stockID: str):
    return cancelOrder()

