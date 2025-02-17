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


# UUID might need to be a string
def receiveOrder(order: StockOrder, sending_user_id: UUID):
    # grab the details only we know
    time = datetime.now()

    print("ORDER RECEIVED: ", order)

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

    processSellOrder(
        SellOrder(
            user_id=sending_user_id,
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


def getStockPriceEngine(stockID):
    global sellTrees
    print("SELL TREE: ", sellTrees)
    return {"success": True, "data": sellTrees[stockID]}


# TEST METHOD
def getSellOrdersEngine(stockID):
    return {"success": True, "data": sellTrees[stockID]}


def processSellOrder(sellOrder: SellOrder):
    global sellTrees
    heappush(sellTrees[sellOrder.stock_id], sellOrder)
    print("SELL ORDER RECEIVED: ", sellOrder)
    print("SELL TREE: ", sellTrees)


def processBuyOrder(buyOrder: BuyOrder):
    buyQueues[buyOrder.stock_id].append(buyOrder)

    matchBuy((buyOrder))


# Matches buy orders to sell orders with partial buy handling
# poppedSellOrders stores touples containing (sellOrder popped from heap, quantity sold)
# return price of buy order
def matchBuy(buyOrder: BuyOrder):
    global sellTrees
    # returns a list of touples (SellOrderFilled, AmountSold)
    ordersFilled = matchBuyRecursive(buyOrder, [])

    orderPrice = calculateMarketBuy(ordersFilled)

    # takes money out of the buyers wallet
    # try:
    #    fundsBuyerToSeller(buyOrder, ordersFilled, orderPrice)
    # except:
    #
    #    for sellOrderTouple in ordersFilled:
    #        sellOrder, sellPrice = sellOrderTouple
    #        heappush(sellTrees[sellOrder.stock_id], sellOrder)


def matchBuyRecursive(buyOrder: BuyOrder, poppedSellOrders: List):
    global sellTrees

    minSellOrder = heappop(sellTrees[buyOrder.stock_id])

    buyQuantity = buyOrder.quantity
    sellQuantity = minSellOrder.quantity

    # Case where sell order quantity == buy order quantity
    if sellQuantity == buyQuantity:
        poppedSellOrders.append((minSellOrder, minSellOrder.quantity))
        return poppedSellOrders

    # Case where first sell order quantity > buy order quantity
    if sellQuantity > buyQuantity:

        # remove buy quantity from sell order
        minSellOrder.quantity = minSellOrder.quantity - buyQuantity

        # push sell order back onto heap with reduced quantity

        heappush(sellTrees[buyOrder.stock_id], minSellOrder)

        poppedSellOrders.append((minSellOrder, buyQuantity))

        return poppedSellOrders

    # Case where sell order quantity < buy order quantity
    # removes quantity of sell order from buy order and pops that sell order from heap
    # then calls matchBuy again with updated buy order and poppedSellOrders list
    if sellQuantity < buyQuantity:

        buyOrder.quantity = buyOrder.quantity - minSellOrder.quantity

        poppedSellOrders.append((minSellOrder, minSellOrder.quantity))

        return matchBuyRecursive(buyOrder, poppedSellOrders)


def calculateMarketBuy(sellOrderList):
    price = 0
    for i in sellOrderList:
        # price += sell price * quantity sold
        price = price + (i[0].price * i[1])
    return price


def cancelOrder(stockID: str):
    return {}
