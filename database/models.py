import uuid
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field
from uuid import UUID


class OrderStatus(str, Enum):
    IN_PROGRESS = 'IN_PROGRESS',
    PARTIALLY_COMPLETE = 'PARTIALLY_COMPLETE',
    COMPLETED = 'COMPLETED'


class Users(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str
    salt: str


class Wallets(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    balance: int = Field(default=0)


class WalletTransactions(SQLModel, table=True):
    wallet_tx_id: int = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    stock_tx_id: int = Field(foreign_key="stocktransactions.stock_tx_id")
    is_debit: bool
    amount: int
    time_stamp: datetime = Field(default_factory=datetime.now)


class Stocks(SQLModel, table=True):
    stock_id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    stock_name: str = Field(unique=True, index=True)
    price: int


class StockPortfolios(SQLModel, table=True):
    user_id: UUID = Field(primary_key=True, foreign_key="users.id")
    stock_id: UUID = Field(primary_key=True, foreign_key="stocks.stock_id")
    quantity_owned: int


class StockTransactions(SQLModel, table=True):
    stock_tx_id: int = Field(default=None, primary_key=True)
    stock_id: UUID = Field(foreign_key="stocks.stock_id")
    wallet_tx_id: int = Field(foreign_key="wallettransactions.wallet_tx_id")
    order_status: OrderStatus = Field(default=OrderStatus.IN_PROGRESS)
    is_buy: bool
    order_type: str
    stock_price: int
    quantity: int
    parent_tx_id: int | None = Field(foreign_key="stocktransactions.stock_tx_id")
    time_stamp: datetime = Field(default_factory=datetime.now)
    user_id: UUID = Field(foreign_key="users.id", index=True)
