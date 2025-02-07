from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str


class AddMoneyRequest(BaseModel):
    amount: float


class Token(BaseModel):
    token: str


class SuccessResponse(BaseModel):
    success: bool = True
    data: list | dict | None = None


class LoginResponse(SuccessResponse):
    data: Token


class ErrorResponse(BaseModel):
    detail: str


class Stock(BaseModel):
    stock_name: str


class User(BaseModel):
    username: str
    id: str
