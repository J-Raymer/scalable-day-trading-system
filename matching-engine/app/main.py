from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from .core import receiveOrder, getStockPrices, cancelOrder, clearSellOrders
from schemas.engine import StockOrder, UID

app = FastAPI(
    root_path="/engine"
)


@app.get("/")
def read_root():
    return RedirectResponse(url="/engine/docs", status_code=302)


# engine calls
@app.post("/placeStockOrder")
def placeStockOrder(order: StockOrder):
    return receiveOrder(order)


@app.post("/cancelStockTransaction")
def cancelStockTransaction(stockID: str):
    return cancelOrder()


# DB calls









