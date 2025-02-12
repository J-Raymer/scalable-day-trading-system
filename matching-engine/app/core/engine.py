from schemas.engine import StockOrder, SellOrder, BuyOrder
from schemas.common import User
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime 
from collections import defaultdict
from heapq import heapify, heappop, heappush

# TODO: change these to better data structures
sellTrees = defaultdict(list)
buyQueues = defaultdict(list)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

async def verify_token(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"require": ["exp", "id", "username"]})
        return User(username=decoded_token["username"], id=decoded_token["id"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired Token")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=403, detail="Unauthorized")
    except jwt.MissingRequiredClaimError:
        raise HTTPException(status_code=400, detail="Missing required claim")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Unauthorized")

 
def receiveOrder(order: StockOrder):
    time = datetime.now()
    if order.is_buy:
        processBuyOrder(
            BuyOrder(stock_id=order.stock_id, quantity=order.quantity, timestamp=time)
        )
        return {
            "success": True,
            "data": {}
        }
    else:
        processSellOrder(
            SellOrder(
                stock_id=order.stock_id, quantity=order.quantity, price=order.price, timestamp=time
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
            pass
            



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


def processBuyOrder(buyOrder: BuyOrder):
    buyQueues[buyOrder.stock_id].append(buyOrder)


def cancelOrder(stockID: str):
    return {}

