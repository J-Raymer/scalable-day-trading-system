from pydantic import BaseModel

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    token: str

class SuccessResponse(BaseModel):
    success: bool
    data: dict | None

class LoginResponse(SuccessResponse):
    data: Token

class ErrorResponse(BaseModel):
    message: str
