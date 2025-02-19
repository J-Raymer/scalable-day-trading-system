from typing import List
from fastapi import FastAPI, HTTPException
from uuid import UUID
from schemas.engine import StockOrder, SellOrder, BuyOrder
from schemas.common import SuccessResponse, ErrorResponse, User
from datetime import datetime
from collections import defaultdict, deque
from heapq import heapify, heappop, heappush
from .engineDbConnect import fundsBuyerToSeller, checkStockPortfolio

sellTrees = defaultdict(list)
buyQueues = defaultdict(deque)


# UUID might need to be a string
def receiveOrder(order: StockOrder, sending_user_id: UUID):
    # grab the details only we know
    time = datetime.now()

    if order.is_buy:
        processBuyOrder(
            BuyOrder(
                user_id=sending_user_id,
                stock_id=order.stock_id,
                quantity=order.quantity,
                timestamp=time,
                order_type=order.order_type,
            )
        )
        return {"success": True, "data": {}}

    elif checkStockPortfolio(sending_user_id, order.stock_id, order.quantity):
        processSellOrder(
            SellOrder(
                user_id=sending_user_id,
                stock_id=order.stock_id,
                quantity=order.quantity,
                price=order.price,
                timestamp=time,
                order_type=order.order_type,
            )
        )
        return {"success": True, "data": {}}
    else:
        return {"success": False, "data": {"message": "you can only sell stock you own"}}


def getStockPriceEngine(stockID):
    global sellTrees

    if not sellTrees[stockID] or len(sellTrees[stockID]) == 0:
        raise HTTPException(status_code=400, detail="No sell orders for stock")

    return {"success": True, "data": sellTrees[stockID]}


def processSellOrder(sellOrder: SellOrder):
    global sellTrees
    heappush(sellTrees[sellOrder.stock_id], sellOrder)


def processBuyOrder(buyOrder: BuyOrder):
    buyQueues[buyOrder.stock_id].append(buyOrder)

    matchBuy((buyOrder))


# Matches buy orders to sell orders with partial buy handling
# poppedSellOrders stores touples containing (sellOrder popped from heap, quantity sold)
# return price of buy order
def matchBuy(buyOrder: BuyOrder):
    global sellTrees

    try:
        tempTree = sellTrees[buyOrder.stock_id].copy()
        # returns a list of touples (SellOrderFilled, AmountSold)
        ordersFilled, newSellTree = matchBuyRecursive(buyOrder, [], tempTree)

        orderPrice = calculateMarketBuy(ordersFilled)

        # takes money out of the buyers wallet

        orderWalletTransactionList = fundsBuyerToSeller(buyOrder, ordersFilled, orderPrice)
        transferStocks(buyOrder, ordersFilled, orderWalletTransactionList) 
    except Exception as e: 
        raise e
    else:
        sellTrees[buyOrder.stock_id] = newSellTree


def matchBuyRecursive(buyOrder: BuyOrder, poppedSellOrders: List, tempTree):

    if len(tempTree) == 0:
        raise HTTPException(
            status_code=400, detail="not enough sell volume to fill buy order"
        )

    minSellOrder = heappop(tempTree)

    buyQuantity = buyOrder.quantity
    sellQuantity = minSellOrder.quantity

    # Case where sell order quantity == buy order quantity
    if sellQuantity == buyQuantity:
        poppedSellOrders.append((minSellOrder, minSellOrder.quantity))
        return poppedSellOrders, tempTree

    # Case where first sell order quantity > buy order quantity
    if sellQuantity > buyQuantity:

        # remove buy quantity from sell order
        minSellOrder.quantity = minSellOrder.quantity - buyQuantity

        # push sell order back onto heap with reduced quantity

        heappush(tempTree, minSellOrder)

        poppedSellOrders.append((minSellOrder, buyQuantity))

        return poppedSellOrders, tempTree

    # Case where sell order quantity < buy order quantity
    # removes quantity of sell order from buy order and pops that sell order from heap
    # then calls matchBuy again with updated buy order and poppedSellOrders list
    if sellQuantity < buyQuantity:

        buyOrder.quantity = buyOrder.quantity - minSellOrder.quantity

        poppedSellOrders.append((minSellOrder, minSellOrder.quantity))

        return matchBuyRecursive(buyOrder, poppedSellOrders, tempTree)


def calculateMarketBuy(sellOrderList):
    price = 0
    for i in sellOrderList:
        # price += sell price * quantity sold
        price += i[0].price * i[1]
    return price


def cancelOrder(stockID: str):
    return {}
