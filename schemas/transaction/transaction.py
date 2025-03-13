from pydantic import BaseModel
from datetime import datetime


class AddMoneyRequest(BaseModel):
    amount: int

    class Config:
        orm_mode = True
        from_attributes = True


class WalletTxResult(BaseModel):
    wallet_tx_id: int
    is_debit: bool
    amount: int
    time_stamp: datetime
    stock_tx_id: int

    class Config:
        orm_mode = True
        from_attributes = True


class PortfolioResult(BaseModel):
    stock_id: int
    stock_name: str
    quantity_owned: int

    class Config:
        orm_mode = True
        from_attributes = True
