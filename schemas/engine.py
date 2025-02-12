from pydantic import BaseModel
from datetime import datetime
from dataclasses import dataclass


class StockOrder(BaseModel):
    stock_id: str
    is_buy: bool
    order_type: str
    quantity: int
    price: int


# TODO: child sell order


@dataclass()
class SellOrder:
    stock_id: str
    quantity: int
    price: int
    timestamp: datetime

    def __eq__(self, other):
        return self.price == other.price

    def __lt__(self, other):
        if self.price == other.price:
            return self.timestamp < other.timestamp
        return self.price < other.price


class BuyOrder(BaseModel):
    stock_id: str
    quantity: int
    timestamp: datetime


class UID(BaseModel):
    id: str
