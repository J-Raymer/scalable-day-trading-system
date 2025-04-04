from pydantic import BaseModel
from typing import Literal, Optional


class StockOrder(BaseModel):
    stock_id: int
    is_buy: bool
    order_type: Literal["MARKET", "LIMIT"]
    quantity: int
    price: Optional[int] = None


# TODO: child sell order


class SellOrder(BaseModel):
    user_id: str
    stock_id: int
    quantity: int
    price: int
    timestamp: str
    order_type: Literal["MARKET", "LIMIT"]
    stock_tx_id: Optional[int] = None
    is_child: bool
    amount_sold: int

    def __eq__(self, other):
        return self.price == other.price

    def __lt__(self, other):
        if self.price == other.price:
            return self.timestamp < other.timestamp
        return self.price < other.price


class BuyOrder(BaseModel):
    user_id: str
    stock_id: int
    quantity: int
    timestamp: str
    price: Literal[0]
    order_type: Literal["MARKET", "LIMIT"]


class StockPrice(BaseModel):
    stock_id: int
    stock_name: str
    current_price: int


class CancelOrder(BaseModel):
    stock_tx_id: int
