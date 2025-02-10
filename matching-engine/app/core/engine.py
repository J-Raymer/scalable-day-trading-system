from schemas.engine import StockOrder, SellOrder, BuyOrder
from collections import defaultdict
from heapq import heapify, heappop, heappush

# TODO: change these to better data structures
sellTrees = []
buyQueues = defaultdict(list)


def receiveOrder(order: StockOrder):
    if order.is_buy:
        return {
            "success": True,
            "data": processBuyOrder(
                BuyOrder(stock_id=order.stock_id, quantity=order.quantity)
            ),
        }
    return {
        "success": True,
        "data": processSellOrder(
            SellOrder(
                stock_id=order.stock_id, quantity=order.quantity, price=order.price
            )
        ),
    }


def clearSellOrders():
    global sellTrees
    sellTrees = []
    return {"message": "sell orders cleared"}


def getStockPrices():
    global sellTrees

    stockPrices = [heappop(sellTrees) for i in range(len(sellTrees))]

    sellTrees = stockPrices
    return {"success": True, "data": sellTrees}


def processSellOrder(sellOrder: SellOrder):
    heappush(sellTrees, sellOrder)
    return sellOrder


def processBuyOrder(buyOrder: BuyOrder):
    buyQueues[buyOrder.stock_id].append(buyOrder)
    return buyOrder


def cancelOrder(stockID: str):
    return {}
