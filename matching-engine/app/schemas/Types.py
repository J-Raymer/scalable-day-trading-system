from pydantic import BaseModel

class StockOrder(BaseModel):
    stock_id : str
    is_buy : bool
    order_type : str
    quantity : int
    price : int


# TODO: child sell order
class SellOrder(BaseModel):
    stock_id : str
    quantity : int
    price : int

class BuyOrder(BaseModel):
    stock_id : str
    quantity : int

class UID(BaseModel):
    id : str
