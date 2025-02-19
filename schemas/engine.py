from pydantic import BaseModel
from datetime import datetime
from dataclasses import dataclass
from uuid import UUID
from typing import Literal, Optional


class StockOrder(BaseModel):
    stock_id: int
    is_buy: bool
    order_type: Literal["MARKET", "LIMIT"]
    quantity: int
    price: int


# TODO: child sell order


@dataclass()
class SellOrder:
    user_id: UUID
    stock_id: int
    quantity: int
    price: int
    timestamp: datetime
    order_type: Literal["MARKET", "LIMIT"]

    def __eq__(self, other):
        return self.price == other.price

    def __lt__(self, other):
        if self.price == other.price:
            return self.timestamp < other.timestamp
        return self.price < other.price


class BuyOrder(BaseModel):
    user_id: UUID
    stock_id: int
    price: int
    quantity: int
    timestamp: datetime
    order_type: Literal["MARKET", "LIMIT"]
