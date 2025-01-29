from fastapi import FastAPI
from app.core.engine import receiveOrder
from app.schemas.OrderTypes import StockOrder

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.post("/engine/placeStockOrder")
def placeStockOrder(order : StockOrder):
    return receiveOrder(order)
