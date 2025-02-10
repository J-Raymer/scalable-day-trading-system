from pydantic import BaseModel


class LoginRequest(BaseModel):
    user_name: str
    password: str


class RegisterRequest(LoginRequest):
    name: str


class Token(BaseModel):
    token: str


class SuccessResponse(BaseModel):
    success: bool = True
    data: list | dict | None = None


class LoginResponse(SuccessResponse):
    data: Token


class ErrorResponse(BaseModel):
    detail: str


class User(BaseModel):
    username: str
    id: str

