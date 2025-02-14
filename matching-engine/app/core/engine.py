from fastapi import FastAPI
from uuid import UUID
from schemas.engine import StockOrder, SellOrder, BuyOrder
from schemas.common import SuccessResponse, ErrorResponse, User
from datetime import datetime 
from collections import defaultdict, deque
from heapq import heapify, heappop, heappush
import requests

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
            buy_order  = buyQueues[stock_id][0]
            sell_order = sellTrees[stock_id][0]
            
            #get wallet of buyer
            response = requests.get("http://transaction/getWalletBalance", json={"user": 1})
           
            #happy path
            if buy_order.user_id != sell_order.user_id:
                #happy path
                if buy_order.quantity == sell_order.quantity:


                    # pop both
                    fufilled_buy  = buyQueues[stock_id].popleft()
                    fufilled_sell = heappop(sellTrees[stock_id])
                    # send a transaction to the transaction service
                    response = requests.post("http://transaction/addMoneyToWallet", json={})
                         


                if buyOrder.quantity < sellOrder.quantity:
                    pass
                if buyOrder.quantity > sellOrder.quantity:
                    pass



def clearSellOrders():
    global sellTrees
    sellTrees.clear()
    return {"message": "sell orders cleared"}


def getStockPrices():
    global sellTrees
    stockPrices = [(stock_id, sellTrees[stock_id][0]) for stock_id in sellTrees]
    return {"success": True, "data": stockPrices}

def processSellOrder(sellOrder: SellOrder):
    heappush(sellTrees[sellOrder.stock_id], sellOrder)
    print(sellTrees[sellOrder.stock_id]) #REMOVE AFTER TESTING
    checkMatch()



def processBuyOrder(buyOrder: BuyOrder):
    buyQueues[buyOrder.stock_id].append(buyOrder)
    print(buyQueues[buyOrder.stock_id]) #REMOVE AFTER TESTING
    checkMatch()


def cancelOrder(stockID: str):
    return {}

