from fastapi import FastAPI
from app.core.engine import receiveOrder, getStockPrices, cancelOrder, clearSellOrders
from app.schemas.Types import StockOrder,  UID

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


#engine calls
@app.post("/engine/placeStockOrder")
def placeStockOrder(order : StockOrder):
    return receiveOrder(order)

@app.get("/transaction/getStockPrices")
def getPrices():
    return getStockPrices()

@app.post("/engine/cancelStockTransaction")
def cancelStockTransaction(stockID : str):
    return cancelOrder()

@app.get("/engine/clearSellOrders")
def clearOrders():
    return clearSellOrders()

#DB calls
@app.post("/transaction/addMoneyToWallet")
def addMoneyToWallet(amount : int):
    return addMoney(amount)

@app.post("/transaction/getWalletBalance")
def getWalletBalance(id : UID):
    return getBalance(id)

@app.post("/transaction/getStockPortfolio")
def getStockPortfolio(id : UID):
    return getPortfolio(id)

@app.post("/transaction/getWalletTransactions")
def getWalletTransactions(id : UID):
    return getWalletLog(id)

@app.post("/transaction/getStockTransactions")
def getStockTransactions(id : UID):
    return getTransactionsLog(id)


