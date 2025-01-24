import uuid

from sqlmodel import SQLModel, Field
from uuid import UUID


class Users(SQLModel, table=True):
    id: UUID = Field(default=uuid.uuid4(), primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str


class Stocks(SQLModel, table=True):
    id: UUID = Field(default=uuid.uuid4(), primary_key=True)
    name: str = Field(unique=True)
    price: int


class BuyOrders(SQLModel, table=True):
    id: UUID = Field(default=uuid.uuid4(), primary_key=True)
    stockId: UUID = Field(foreign_key="stocks.id")
    bid: int


class SellOrders(SQLModel, table=True):
    id: UUID = Field(default=uuid.uuid4(), primary_key=True)
    stockId: UUID = Field(foreign_key="stocks.id")
    price: int

