from pydantic import BaseModel

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    token: str

class SuccessResponse(BaseModel):
    success: bool = True
    data: list | dict | None = None

class LoginResponse(SuccessResponse):
    data: Token

class ErrorResponse(BaseModel):
    message: str
