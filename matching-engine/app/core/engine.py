from fastapi import FastAPI
from uuid import UUID
from schemas.engine import StockOrder, SellOrder, BuyOrder
from schemas.common import SuccessResponse, ErrorResponse, User
from datetime import datetime 
from collections import defaultdict, deque
from heapq import heapify, heappop, heappush

sellTrees = defaultdict(list)
buyQueues = defaultdict(deque)


 
def receiveOrder(order: StockOrder, user: User):
    # grab the details only we know
    time = datetime.now()
    uid = user.id

    if order.is_buy:
        processBuyOrder(
            BuyOrder(user_id=uid,
                     stock_id=order.stock_id,
                     quantity=order.quantity,
                     timestamp=time)
        )
        return {
            "success": True,
            "data": {}
        }
    else:
        processSellOrder(
            SellOrder(
                user_id=uid,
                stock_id=order.stock_id,
                quantity=order.quantity,
                price=order.price,
                timestamp=time
            )
        )
        return {
            "success": True,
            "data": {}
        }

def checkMatch():
    global sellTrees, buyQueues

    for stock_id in sellTrees:
        if (sellTrees[stock_id]) and (buyQueues[stock_id]):
            print('match found')
            
            



def clearSellOrders():
    global sellTrees
    sellTrees.clear()
    return {"message": "sell orders cleared"}


'''
def getStockPrices():
    global sellTrees

    stockPrices = [heappop(sellTrees) for i in range(len(sellTrees))]

    sellTrees = stockPrices
    return {"success": True, "data": sellTrees}
'''

def processSellOrder(sellOrder: SellOrder):
    heappush(sellTrees[sellOrder.stock_id], sellOrder)
    print(sellTrees[sellOrder.stock_id])
    checkMatch()



def processBuyOrder(buyOrder: BuyOrder):
    buyQueues[buyOrder.stock_id].append(buyOrder)
    print(buyQueues[buyOrder.stock_id])
    checkMatch()


def cancelOrder(stockID: str):
    return {}

