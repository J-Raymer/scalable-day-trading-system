from pydantic import BaseModel


class StockSetup(BaseModel):
    stock_id: int
    quantity: int


class Stock(BaseModel):
    stock_name: str
