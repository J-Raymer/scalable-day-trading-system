import uuid

from sqlmodel import SQLModel, Field
from uuid import UUID


class Users(SQLModel, table=True):
    id: UUID = Field(default=uuid.uuid4(), primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str


class Stocks(SQLModel, table=True):
    name: str = Field(primary_key=True)
    price: int


class BuyOrders(SQLModel, table=True):
    id: UUID = Field(default=uuid.uuid4(), primary_key=True)
    stockName: str = Field(foreign_key="stocks.name")
    bid: int


class SellOrders(SQLModel, table=True):
    id: UUID = Field(default=uuid.uuid4(), primary_key=True)
    stockName: str = Field(foreign_key="stocks.name")
    price: int

