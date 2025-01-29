import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field
from uuid import UUID

class Users(SQLModel, table=True):
    id: UUID = Field(default=uuid.uuid4(), primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str


class Wallets(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    balance: int = Field(default=0)


class WalletTransactions(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    stock_tx_id: int = Field(foreign_key="stocktransactions.id")
    is_debit: bool
    amount: int
    time_stamp: datetime = Field(default=datetime.now())


class Stocks(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    price: int


class StockPortfolios(SQLModel, table=True):
    user_id: UUID = Field(primary_key=True, foreign_key="users.id")
    stock_id: int = Field(primary_key=True, foreign_key="stocks.id")
    quantity_owned: int


class StockTransactions(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    stock_id: int = Field(foreign_key="stocks.id")
