from pydantic import BaseModel
from uuid import UUID

class StockSetup(BaseModel):
    stock_id: UUID
    quantity: int

class Stock(BaseModel):
    stock_name: str
