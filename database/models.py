import uuid
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, BigInteger, Column


class OrderStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    PARTIALLY_COMPLETE = "PARTIALLY_COMPLETE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

def generate_user_id():
    return str(uuid.uuid4())

def generate_timestamp():
    return str(datetime.now())

class Users(SQLModel, table=True):
    id: str = Field(default_factory=generate_user_id, primary_key=True)
    user_name: str = Field(index=True, unique=True)
    name: str
    password: str
    salt: str


class Wallets(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", unique=True, index=True)
    balance: int = Field(default=0)


class WalletTransactions(SQLModel, table=True):
    wallet_tx_id: int = Field(default=None, primary_key=True)
    stock_tx_id: int = Field(foreign_key="stocktransactions.stock_tx_id")
    user_id: str = Field(foreign_key="users.id", index=True)
    is_debit: bool
    amount: int
    time_stamp: str = Field(default_factory=generate_timestamp)


class Stocks(SQLModel, table=True):
    stock_id: int = Field(primary_key=True)
    stock_name: str = Field(unique=True, index=True)
    current_price: int = Field(default=0)


class StockPortfolios(SQLModel, table=True):
    user_id: str = Field(primary_key=True, foreign_key="users.id", index=True)
    stock_id: int = Field(primary_key=True, foreign_key="stocks.stock_id")
    quantity_owned: int = Field(sa_column=Column(BigInteger()))


class StockTransactions(SQLModel, table=True):
    stock_tx_id: int = Field(default=None, primary_key=True)
    wallet_tx_id: int | None = Field(foreign_key="wallettransactions.wallet_tx_id")
    stock_id: int = Field(foreign_key="stocks.stock_id")
    order_status: OrderStatus = Field(default=OrderStatus.IN_PROGRESS)
    is_buy: bool
    order_type: OrderType
    stock_price: int
    quantity: int = Field(sa_column=Column(BigInteger()))
    parent_stock_tx_id: int | None = Field(foreign_key="stocktransactions.stock_tx_id")
    time_stamp: str = Field(default_factory=generate_timestamp)
    user_id: str = Field(foreign_key="users.id", index=True)
