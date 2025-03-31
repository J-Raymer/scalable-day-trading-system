from typing import List

from sqlalchemy import except_
from schemas import SuccessResponse, RabbitError
from schemas.RedisClient import RedisClient, CacheName
from schemas.engine import StockOrder, SellOrder, BuyOrder, StockPrice, CancelOrder
from datetime import datetime
from collections import defaultdict, deque
from heapq import heapify, heappop, heappush
from .engineDbConnect import *
from .db_methods import *
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
        await processSellOrder(
            SellOrder(
                user_id=sending_user_id,
                stock_id=order.stock_id,
                quantity=order.quantity,
                price=order.price,
                timestamp=time,
                order_type=order.order_type,
                is_child=False,
                amount_sold=0,
            ),
        )
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

    transactionId = await stockFromSeller(sellOrder)

    sellOrder.stock_tx_id = transactionId

    if sellOrder.stock_tx_id is None:
        raise ValueError(400, "error assigned id to sell order")

    heappush(sellTrees[sellOrder.stock_id], sellOrder)


async def processBuyOrder(buyOrder: BuyOrder):
    buyQueues[buyOrder.stock_id].append(buyOrder)

    await matchBuy(buyOrder)


# Matches buy orders to sell orders with partial buy handling
# poppedSellOrders stores touples containing (sellOrder popped from heap, quantity sold)
# return price of buy order
async def matchBuy(buyOrder: BuyOrder):
    global sellTrees

    tempTree = copy.deepcopy(sellTrees[buyOrder.stock_id])
    skipped_orders = []
    # returns a list of touples (SellOrderFilled, AmountSold)
    try:
        ordersFilled, newSellTree, skipped_orders = await matchBuyRecursive(
            buyOrder, [], tempTree, skipped_orders
        )
    except ValueError as e:
        raise e
    finally:
        for order in skipped_orders:
            heappush(tempTree, order)

    orderPrice = calculateMarketBuy(ordersFilled)
    sellTrees[buyOrder.stock_id] = newSellTree

    # takes money out of the buyers wallet
    await fundsBuyerToSeller(buyOrder, ordersFilled, orderPrice)


# This function tries to match up the buy order quantity with enough sell orders to match.
# It may return any number of sell orders from <1 to N. Where any sell order can be
# divided to match the quantity exactly (hence <1).
# Divided orders operate accordingly:
#   - Parent Order: quantity is reduced by the amount required to match the remining buy order balance. AND NOT REMOVED FROM THE HEAP
#   - Child  Order: created with that same quantity to be added to the returned list of orders. It is never added to the heap
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
async def matchBuyRecursive(
    buyOrder: BuyOrder, poppedSellOrders: List, tempTree, skipped_orders
):

    if len(tempTree) == 0:
        raise ValueError(400, "not enough sell volume to fill buy order")

    ## check to make sure we aren't buying from ourselves

    minSellOrder = heappop(tempTree)

    if buyOrder.user_id == minSellOrder.user_id:
        skipped_orders.append(minSellOrder)
        return await matchBuyRecursive(
            buyOrder, poppedSellOrders, tempTree, skipped_orders
        )
    """
    having a while loop in a recursive function like this scares me 
    changed the recursive handling to include a skipped orders list
    skipped orders get added back after recursive step is over in matchBuy()
    line 120
    """
    # while tempTree:
    #
    #     minSellOrder = heappop(tempTree)
    #
    #     if buyOrder.user_id == minSellOrder.user_id:
    #         skipped_orders.append(minSellOrder)
    #         continue
    #     else:
    #         break  # this line is hit when find a valid sell order which was not created by the buyer
    #
    # if (
    #     not tempTree
    #     and skipped_orders
    #     and all(order.user_id == buyOrder.user_id for order in skipped_orders)
    # ):
    #     for order in skipped_orders:
    #         heappush(tempTree, order)
    #     raise ValueError(
    #         400, "not enough sell orders from other users to fulfill order"
    #     )
    #
    # for order in skipped_orders:
    #     heappush(tempTree, order)
    ## end check

    buyQuantity = buyOrder.quantity
    sellQuantity = minSellOrder.quantity
    sellAmount = minSellOrder.amount_sold

    # Case 1: sellOrder quantity == buyOrder quantity
    if (sellQuantity - sellAmount) == buyQuantity:
        minSellOrder.amount_sold = buyQuantity

        poppedSellOrders.append((minSellOrder, buyQuantity))
        return poppedSellOrders, tempTree, skipped_orders

    # Case 2: sellOrder quantity > buyOrder quantity
    #  (split off a child transaction)
    if (sellQuantity - sellAmount) > buyQuantity:

        # remove buy quantity from sell order
        minSellOrder.amount_sold = sellAmount + buyQuantity

        # change the original stock transaction to Partially complete
        """
         this is already getting updated somewhere else
        """

        # await setToPartiallyComplete(minSellOrder.stock_tx_id, minSellOrder.quantity)

        # push original sell order back onto heap with reduced quantity
        heappush(tempTree, minSellOrder)

        # create a child sell order
        childSellOrder = SellOrder(
            stock_tx_id=minSellOrder.stock_tx_id,
            user_id=minSellOrder.user_id,
            stock_id=minSellOrder.stock_id,
            quantity=buyQuantity,
            price=minSellOrder.price,
            timestamp=minSellOrder.timestamp,
            order_type=minSellOrder.order_type,
            amount_sold=buyQuantity,
            is_child=True,
        )

        # pass child sell order to dbConnect, no other need for it
        poppedSellOrders.append((childSellOrder, buyQuantity))
        # create a child transaction that is IN_PROGRESS, with the parent stock tx id

        """
         The transaction also gets created somewhere else and gets created as COMPLETE
        """

        # childTxId = await createChildTransaction(
        #     childSellOrder, minSellOrder.stock_tx_id
        # )
        # childSellOrder.stock_tx_id = childTxId
        #
        # res = await getStockTransaction(childTxId)
        #
        # if not res:
        #     raise ValueError(400, "transaction not in db")
        """
        child sell orders dont need to be added to the heap
        """
        # poppedSellOrders.append((childSellOrder, buyQuantity))

        return poppedSellOrders, tempTree, skipped_orders

    # Case 3: sellOrder quantity < buyOrder quantity
    #  (we need more sell orders to make up the difference, so we recurse)
    if (sellQuantity - sellAmount) < buyQuantity:

        buyOrder.quantity = buyOrder.quantity - minSellOrder.quantity

        minSellOrder.amount_sold = sellQuantity
        poppedSellOrders.append((minSellOrder, minSellOrder.quantity))

        return await matchBuyRecursive(
            buyOrder, poppedSellOrders, tempTree, skipped_orders
        )


def calculateMarketBuy(sellOrderList):
    price = 0
    for i in sellOrderList:
        # price += sell price * quantity sold
        price += i[0].price * i[1]
    return price


async def cancelOrderEngine(cancelOrder: CancelOrder, user_id: str):
    transactionId = cancelOrder.stock_tx_id
    # Search heap for order

    transaction = await getStockTransaction(transactionId, user_id)
    if not transaction:
        raise ValueError(500, "transcation not found")
    global sellTrees

    tree = sellTrees[transaction.stock_id]

    for sellOrder in tree:
        if sellOrder.stock_tx_id == transactionId:
            if sellOrder.user_id != user_id:
                raise ValueError(500, "you cannot cancel an order that is not yours")
            else:
                tree.remove(sellOrder)
                heapify(tree)
                break

    # set transaction status to cancelled
    await cancelTransaction(transactionId)
    return SuccessResponse()
