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


# Should not use this as a returned object to the user. Used for the register caching.
class User(BaseModel):
    """Should not use this as a returned object to the user. Used for the register caching."""
    id: str
    user_name: str
    name: str
    password: str | None
    salt: str | None

