from pydantic import BaseModel

class StockOrder (BaseModel):
    stock_id : str
    is_buy : bool
    order_type : str
    quantity : int
    price : int

class SellOrder (BaseModel):
    stock_id : str
    quantity : int
    price : int
