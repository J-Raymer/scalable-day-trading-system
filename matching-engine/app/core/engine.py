from typing import List
from fastapi import FastAPI
from uuid import UUID
from schemas.engine import StockOrder, SellOrder, BuyOrder
from schemas.common import SuccessResponse, ErrorResponse, User
from schemas.transaction import AddMoneyRequest
from datetime import datetime
from collections import defaultdict, deque
from heapq import heapify, heappop, heappush
import requests


sellTrees = defaultdict(list)
buyQueues = defaultdict(deque)


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
            )
        )
        return {"success": True, "data": {}}
    else:
        processSellOrder(
            SellOrder(
                user_id=sending_user_id,
                stock_id=order.stock_id,
                quantity=order.quantity,
                price=order.price,
                timestamp=time,
            )
        )
        return {"success": True, "data": {uid}}


def checkMatch():
    global sellTrees, buyQueues

    for stock_id in sellTrees:
        if (sellTrees[stock_id]) and (buyQueues[stock_id]):
            print("match found")
            buy_order = buyQueues[stock_id][0]
            sell_order = sellTrees[stock_id][0]

            # get wallet of buyer
            response = requests.get(
                "http://transaction/getWalletBalance", json={"user": 1}
            )

            # happy path
            if buy_order.user_id != sell_order.user_id:
                # happy path
                if buy_order.quantity == sell_order.quantity:

                    # pop both
                    fufilled_buy = buyQueues[stock_id].popleft()
                    fufilled_sell = heappop(sellTrees[stock_id])
                    # send a transaction to the transaction service
                    response = requests.post(
                        "http://transaction/addMoneyToWallet", json={}
                    )

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
    print(sellTrees[sellOrder.stock_id])  # REMOVE AFTER TESTING
    checkMatch()


def processBuyOrder(buyOrder: BuyOrder):
    buyQueues[buyOrder.stock_id].append(buyOrder)
    print(buyQueues[buyOrder.stock_id])  # REMOVE AFTER TESTING
    checkMatch()


# Matches buy orders to sell orders with partial buy handling
# poppedSellOrders stores touples containing (sellOrder popped from heap, quantity sold)
# return price of buy order
def matchBuy(buyOrder: BuyOrder):
    ordersFilled = matchBuyRecursive(buyOrder, [])

    orderPrice = calculateMarketBuy(ordersFilled)

    user = engineGetUser.getUserFromId(buyOrder.user_id)


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


def calculateMarketBuy(sellOrderList):
    price = 0.0
    for i in sellOrderList:
        # price += sell price * quantity sold
        price = price + (i[0].price * i[1])
    return price


# Pays sellers after buy order has been filled
def paySellers(sellOrderList):
    for sellOrder in sellOrderList:
        userId = sellOrder[0].user_id

        user = engineGetUser.getUserFromId(userId)

        addMoneyRequest = AddMoneyRequest(sellOrder[0].price * sellOrder[1])
        # send post request to transaction service??
        # TODO
        # add a call to engineDb to add money to wallet directly
        requests.post(
            "http://transaction/addMoneyToWallet", json={addMoneyRequest, user}
        )


def cancelOrder(stockID: str):
    return {}
