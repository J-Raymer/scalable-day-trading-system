from typing import List
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
            BuyOrder(
                user_id=uid,
                stock_id=order.stock_id,
                quantity=order.quantity,
                timestamp=time,
            )
        )
        return {"success": True, "data": {}}
    else:
        processSellOrder(
            SellOrder(
                user_id=uid,
                stock_id=order.stock_id,
                quantity=order.quantity,
                price=order.price,
                timestamp=time,
            )
        )
        return {"success": True, "data": {}}


def checkMatch():
    global sellTrees, buyQueues

    for stock_id in sellTrees:
        if (sellTrees[stock_id]) and (buyQueues[stock_id]):
            print("match found")


def clearSellOrders():
    global sellTrees
    sellTrees.clear()
    return {"message": "sell orders cleared"}


"""
def getStockPrices():
    global sellTrees

    stockPrices = [heappop(sellTrees) for i in range(len(sellTrees))]

    sellTrees = stockPrices
    return {"success": True, "data": sellTrees}
"""


def processSellOrder(sellOrder: SellOrder):
    heappush(sellTrees[sellOrder.stock_id], sellOrder)
    print(sellTrees[sellOrder.stock_id])
    checkMatch()


def processBuyOrder(buyOrder: BuyOrder):
    buyQueues[buyOrder.stock_id].append(buyOrder)
    print(buyQueues[buyOrder.stock_id])
    checkMatch()


# Matches buy orders to sell orders with partial buy handling
# poppedSellOrders stores touples containing (sellOrder popped from heap, quantity sold)
# return price of buy order


def matchBuy(buyOrder: BuyOrder):
    return matchBuyRecursive(buyOrder, [])


def matchBuyRecursive(buyOrder: BuyOrder, poppedSellOrders: List):
    global sellTrees

    minSellOrder = heappop(sellTrees[buyOrder.stock_id])

    buyQuantity = buyOrder.buyQuantity
    sellQuantity = SellOrder.sellQuantity

    # Case where sell order quantity == buy order quantity
    if sellQuantity == buyQuantity:
        poppedSellOrders.append((minSellOrder, minSellOrder.quantity))
        return poppedSellOrders

    # Case where first sell order quantity > buy order quantity
    if sellQuantity > buyQuantity:

        # remove buy quantity from sell order
        minSellOrder.quantity = minSellOrder.quantity - buyQuantity

        # push sell order back onto heap with reduced quantity

        heappush(sellTrees[buyOrder.stock_id], (minSellOrder, buyQuantity))

        return poppedSellOrders

    # Case where sell order quantity < buy order quantity
    # removes quantity of sell order from buy order and pops that sell order from heap
    # then calls matchBuy again with updated buy order and poppedSellOrders list
    if sellQuantity < buyQuantity:

        buyOrder.quantity = buyOrder.quantity - minSellOrder.quantity

        poppedSellOrders.append((minSellOrder, minSellOrder.quantity))

        return matchBuyRecursive(buyOrder, poppedSellOrders)

    # ErrorResponse
    # idk what to put here
    return []


def calculateBuyPrice(sellOrderList):
    price = 0.0
    for i in sellOrderList:
        # price += sell price * quantity sold
        price = price + (i[0].price * i[1])
    return price


def cancelOrder(stockID: str):
    return {}
