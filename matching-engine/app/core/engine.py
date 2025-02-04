from app.schemas.OrderTypes import StockOrder, SellOrder, BuyOrder
from collections import defaultdict

#TODO: change these to better data structures
sellTrees = defaultdict(list)
buyQueues = defaultdict(list)

def receiveOrder(order : StockOrder):
    if order.is_buy:
        processBuyOrder(BuyOrder(stock_id = order.stock_id, quantity = order.quantity))
    else
        processSellOrder(SellOrder(stock_id = order.stock_id, quantity = order.quantity, price = order.price))
    return {"success": true, "data": null}


def getStockPrices():
    priceList = []
    for key in sellTrees:
        priceList.append(sellTrees[key][0])
    return {"success": true, "data": priceList}

def processSellOrder(sellOrder : SellOrder):
    sellTrees[sellOrder.stock_id].append(sellOrder)
    sellTrees[sellOrder.stock_id].sort(key=lambda x: x.price)

def processBuyOrder(buyOrder : BuyOrder):
    buyOrders[buyOrder.stock_id].append(buyOrder)


def cancelOrder(stockID : str):
    return {}
