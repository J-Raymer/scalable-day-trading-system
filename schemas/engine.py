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
    price: Optional[int] = None


# TODO: child sell order


@dataclass()
class SellOrder:
    user_id: UUID
    stock_id: int
    quantity: int
    price: int
    timestamp: datetime
    order_type: Literal["MARKET", "LIMIT"]
    stock_tx_id: Optional[int] = None

    def __eq__(self, other):
        return self.price == other.price

    def __lt__(self, other):
        if self.price == other.price:
            return self.timestamp < other.timestamp
        return self.price < other.price


class BuyOrder(BaseModel):
    user_id: UUID
    stock_id: int
    quantity: int
    timestamp: datetime
    price: Literal[0]
    order_type: Literal["MARKET", "LIMIT"]


class StockPrice(BaseModel):
    stock_id: int
    stock_name: str
    current_price: int


class CancelOrder(BaseModel):
    stock_tx_id: int
