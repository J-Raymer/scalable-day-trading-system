from typing import List
from fastapi import HTTPException
from schemas import SuccessResponse
from schemas.RedisClient import RedisClient, CacheName
from schemas.engine import StockOrder, SellOrder, BuyOrder, StockPrice, CancelOrder
from datetime import datetime
from collections import defaultdict, deque
from heapq import heapify, heappop, heappush
from .engineDbConnect import (
    fundsBuyerToSeller,
    gatherStocks,
    getStockData,
    cancelTransaction,
    getTransaction,
    createChildTransaction,
    setToPartiallyComplete
)

sellTrees = defaultdict(list)
buyQueues = defaultdict(deque)

cache = RedisClient()


def receiveOrder(order: StockOrder, sending_user_id: str):
    # grab the details only we know
    time = str(datetime.now())

    if order.is_buy:
        processBuyOrder(
            BuyOrder(
                user_id=sending_user_id,
                stock_id=order.stock_id,
                quantity=order.quantity,
                timestamp=time,
                order_type=order.order_type,
                price=0,
            )
        )
        return SuccessResponse()

    else:
        incomingSellOrder = SellOrder(
            user_id=sending_user_id,
            stock_id=order.stock_id,
            quantity=order.quantity,
            price=order.price,
            timestamp=time,
            order_type=order.order_type,
        )
        transactionId = gatherStocks(
            incomingSellOrder, sending_user_id, order.stock_id, order.quantity
        )

        incomingSellOrder.stock_tx_id = transactionId

        if incomingSellOrder.stock_tx_id == None:
            raise HTTPException(
                status_code=400, detail="error assigning id to sell order"
            )

        processSellOrder(incomingSellOrder)
        return SuccessResponse()


def getStockPriceEngine():
    global sellTrees

    cache_hit = cache.get(CacheName.STOCKS)
    data = []

    if cache_hit:
        print('CACHE hit in get stock price')
        for stock_id, stock_name in cache_hit.items():
            # Need to cast id to int because it's stored as a string
            id = int(stock_id)
            if sellTrees[id]:
                data.append(
                    StockPrice(stock_id=id, stock_name=stock_name, current_price=sellTrees[id][0].price)
                )
    else:
        stockList = getStockData()
        for stock in stockList:
            id = stock.stock_id
            if sellTrees[id]:
                data.append(
                    StockPrice(stock_id=id, stock_name=stock.stock_name, current_price=sellTrees[id][0].price)
                )
    return SuccessResponse(data=data)


def processSellOrder(sellOrder: SellOrder):
    global sellTrees
    heappush(sellTrees[sellOrder.stock_id], sellOrder)
    # TODO: We should rename "price" to "current_price" across the app for consistency and to avoid this sort of thing
    sell_dict = dict(sellOrder)
    sell_dict['current_price'] = sellOrder.price
    del sell_dict['price']


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
        fundsBuyerToSeller(buyOrder, ordersFilled, orderPrice)
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

        # change the original stock transaction to Partially complete
        setToPartiallyComplete(minSellOrder.stock_tx_id, minSellOrder.quantity)

        # push original sell order back onto heap with reduced quantity
        heappush(tempTree, minSellOrder)

        # create a child sell order
        childSellOrder = SellOrder(
            user_id = minSellOrder.user_id,
            stock_id = minSellOrder.stock_id,
            quantity = buyQuantity,
            price = minSellOrder.price,
            timestamp = minSellOrder.timestamp,
            order_type = minSellOrder.order_type
        )

        # create a child transaction that is IN_PROGRESS, with the parent stock tx id
        childTxId = createChildTransaction(childSellOrder, minSellOrder.stock_tx_id)
        childSellOrder.stock_tx_id = childTxId
        
        res = getTransaction(childTxId)

        if not res:
            raise HTTPException(status_code=400, detail="transaction not in db")

        poppedSellOrders.append((childSellOrder, buyQuantity))

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


def cancelOrderEngine(cancelOrder: CancelOrder):
    transactionId = cancelOrder.stock_tx_id
    # Search heap for order

    transaction = getTransaction(transactionId)
    global sellTrees

    tree = sellTrees[transaction.stock_id]

    for sellOrder in tree:

        if sellOrder.stock_tx_id == transactionId:
            tree.remove(sellOrder)
            heapify(tree)
            break

    # set transaction status to cancelled
    cancelTransaction(transactionId)
    return SuccessResponse()
