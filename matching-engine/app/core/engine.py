from app.schemas.OrderTypes import SellOrder, StockOrder

sellOrders = []

def receiveOrder (order : StockOrder):
    return order

def processSellOrder(sellOrder : SellOrder):
    sellOrders.append(sellOrder)
    sellOrders.sort()

def processBuyOrder():
    pass
