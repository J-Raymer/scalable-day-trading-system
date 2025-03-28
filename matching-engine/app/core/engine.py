from typing import List
from schemas import SuccessResponse, RabbitError
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
    setToPartiallyComplete,
)
import copy

sellTrees = defaultdict(list)
buyQueues = defaultdict(deque)

cache = RedisClient()


async def receiveOrder(order: StockOrder, sending_user_id: str):
    time = str(datetime.now())

    if order.is_buy:
        await processBuyOrder(
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
        transactionId = await gatherStocks(
            incomingSellOrder, sending_user_id, order.stock_id, order.quantity
        )

        incomingSellOrder.stock_tx_id = transactionId

        if incomingSellOrder.stock_tx_id is None:
            print("no incomingSellOrder.stock_tx_id")
            raise ValueError(400, "error assigned id to sell order")

        await processSellOrder(incomingSellOrder)
        return SuccessResponse()


async def getStockPriceEngine():
    global sellTrees

    cache_hit = cache.get(CacheName.STOCKS)
    data = []

    if cache_hit:
        for stock_id, stock_name in cache_hit.items():
            # Need to cast id to int because it's stored as a string
            id = int(stock_id)
            if sellTrees[id]:
                data.append(
                    StockPrice(
                        stock_id=id,
                        stock_name=stock_name,
                        current_price=sellTrees[id][0].price,
                    )
                )
    else:
        print("CACHE MISS in get stock price")
        stockList = await getStockData()
        for stock in stockList:
            id = stock.stock_id
            if sellTrees[id]:
                data.append(
                    StockPrice(
                        stock_id=id,
                        stock_name=stock.stock_name,
                        current_price=sellTrees[id][0].price,
                    )
                )
    return SuccessResponse(data=data)


async def processSellOrder(sellOrder: SellOrder):
    global sellTrees
    heappush(sellTrees[sellOrder.stock_id], sellOrder)
    # TODO: We should rename "price" to "current_price" across the app for consistency and to avoid this sort of thing
    sell_dict = dict(sellOrder)
    sell_dict["current_price"] = sellOrder.price
    del sell_dict["price"]


async def processBuyOrder(buyOrder: BuyOrder):
    buyQueues[buyOrder.stock_id].append(buyOrder)

    await matchBuy(buyOrder)


# Matches buy orders to sell orders with partial buy handling
# poppedSellOrders stores touples containing (sellOrder popped from heap, quantity sold)
# return price of buy order
async def matchBuy(buyOrder: BuyOrder):
    global sellTrees

    tempTree = copy.deepcopy(sellTrees[buyOrder.stock_id])
    # returns a list of touples (SellOrderFilled, AmountSold)

    #TODO REMOVE AFTER TESTING
    count = 0
    check = False
    for sellOrder in tempTree:
        if sellOrder.user_id != buyOrder.user_id:
            print(f"found a seller after {count} orders in the heap")
            check = True
        else:
            count = count + 1
    if not check:
        print(f"only found {buyOrder.user_id} in the heap")


    ordersFilled, newSellTree = await matchBuyRecursive(buyOrder, [], tempTree)

    sellTrees[buyOrder.stock_id] = newSellTree

    orderPrice = calculateMarketBuy(ordersFilled)

    # takes money out of the buyers wallet
    await fundsBuyerToSeller(buyOrder, ordersFilled, orderPrice)



# This function tries to match up the buy order quantity with enough sell orders to match.
# It may take any number of sell orders from <1 to N. Where any sell order can be
# divided to match the quantity exactly (hence <1).
# Divided orders operate accordingly:
#   - Parent Order: quantity is reduced by the amount required to match the remining buy order balance. 
#   - Child  Order: created with that same quantity to be added to the returned list of orders.
# 
# Inputs:   
#           - @buyOrder : the buy order
#           - @[]       : an empty list (for recursion) to populate with the returning sell orders
#           - @tempTree : the heap for <stock_id> we are buying from
# Outputs:
#           - (SellOrderFilled, AmountSold) tuples
#           - newSellTree 
# Errors:
#           - 400
#             -> ValueError(400, "transaction not in db")
#             -> ValueError(400, "not enough sell volume to fill buy order")
#
async def matchBuyRecursive(buyOrder: BuyOrder, poppedSellOrders: List, tempTree):

    if len(tempTree) == 0:
        print("no more sell orders in the heap")
        raise ValueError(400, "not enough sell volume to fill buy order")

    ## Check to make sure the buying user isn't buying from themselves
    skipped_orders = []

    while tempTree:
        minSellOrder = heappop(tempTree)

        if buyOrder.user_id == minSellOrder.user_id:
            skipped_orders.append(minSellOrder)
            continue
        else:
            break # this line happens when we find an order from a different user

    if not tempTree and skipped_orders and all(order.user_id == buyOrder.user_id for order in skipped_orders):
        for order in skipped_orders:
            heappush(tempTree, order)
        print("not enough sell orders from other users for this order: " + str(buyOrder.user_id))
        raise ValueError(400, "not enough sell volume from other users to fufill order")

    for order in skipped_orders:
        heappush(tempTree, order)
    ## End check

    buyQuantity = buyOrder.quantity
    sellQuantity = minSellOrder.quantity

    # Case 1: sell order quantity == buy order quantity
    if sellQuantity == buyQuantity:
        poppedSellOrders.append((minSellOrder, minSellOrder.quantity))
        return poppedSellOrders, tempTree

    # Case 2: sell order quantity > buy order quantity
    # (create a child transaction)
    if sellQuantity > buyQuantity:

        # remove buy quantity from sell order
        minSellOrder.quantity = minSellOrder.quantity - buyQuantity

        # change the original stock transaction to Partially complete
        await setToPartiallyComplete(minSellOrder.stock_tx_id, minSellOrder.quantity)

        # push original sell order back onto heap with reduced quantity
        heappush(tempTree, minSellOrder)

        # create a child sell order
        childSellOrder = SellOrder(
            user_id=minSellOrder.user_id,
            stock_id=minSellOrder.stock_id,
            quantity=buyQuantity,
            price=minSellOrder.price,
            timestamp=minSellOrder.timestamp,
            order_type=minSellOrder.order_type,
        )

        # create a child transaction that is IN_PROGRESS, with the parent stock tx id
        childTxId = await createChildTransaction(
            childSellOrder, minSellOrder.stock_tx_id
        )
        childSellOrder.stock_tx_id = childTxId

        res = await getTransaction(childTxId)

        if not res:
            print("selltransaction from initial gather not in db")
            raise ValueError(400, "transaction not in db")

        poppedSellOrders.append((childSellOrder, buyQuantity))

        return poppedSellOrders, tempTree

    # Case 3: sell order quantity < buy order quantity
    # (we need more sell orders so we recurse)
    if sellQuantity < buyQuantity:

        buyOrder.quantity = buyOrder.quantity - minSellOrder.quantity

        poppedSellOrders.append((minSellOrder, minSellOrder.quantity))

        return await matchBuyRecursive(buyOrder, poppedSellOrders, tempTree)


def calculateMarketBuy(sellOrderList):
    price = 0
    for i in sellOrderList:
        # price += sell price * quantity sold
        price += i[0].price * i[1]
    return price


async def cancelOrderEngine(cancelOrder: CancelOrder, user_id: str):

    print("Cancelling an Order")
    transactionId = cancelOrder.stock_tx_id
    # Search heap for order

    transaction = await getTransaction(transactionId)
    if not transaction:
        print("No Transaction Found")
        raise ValueError(500, "transcation not found")
    global sellTrees

    tree = sellTrees[transaction.stock_id]

    for sellOrder in tree:
        if sellOrder.stock_tx_id == transactionId:
            if sellOrder.user_id != user_id:
                print("You cannot cancel an order that is not yours")
                raise ValueError(500, "You cannot cancel an order that is not yours")
            else:
                tree.remove(sellOrder)
                heapify(tree)
                break

    # set transaction status to cancelled
    await cancelTransaction(transactionId)
    return SuccessResponse()
