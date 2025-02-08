from pydantic import BaseModel
from dataclasses import dataclass


class StockOrder(BaseModel):
    stock_id : str
    is_buy : bool
    order_type : str
    quantity : int
    price : int


# TODO: child sell order

@dataclass()
class SellOrder:
    stock_id : str
    quantity : int
    price : int

    def __eq__ (self, other):
        return self.price == other.price

    def __lt__ (self, other):
        if self.price == other.price:
            return self.stock_id < other.stock_id
        return self.price < other.price


class BuyOrder(BaseModel):
    stock_id : str
    quantity : int

class UID(BaseModel):
    id : str
