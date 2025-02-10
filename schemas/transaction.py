from pydantic import BaseModel


class AddMoneyRequest(BaseModel):
    amount: float
