from uuid import UUID
import bcrypt
import dotenv
import jwt
import os
import sqlmodel
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from fastapi import FastAPI, Response, Depends
from fastapi.responses import RedirectResponse
from sqlmodel import SQLModel, Field
# from models import Users
from database import Wallets




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()
url = f"postgresql://admin:isolated-dean-primal-starving@localhost:5433/day_trader"
engine = sqlmodel.create_engine(url)



class AddMoneyRequest(BaseModel):
    amount: float

class ErrorResponse(BaseModel):
    message: str

class Token(BaseModel):
    username: str
    id: str



def verify_token(token: str, res: Response) -> Token | ErrorResponse:
    try:
        decoded_token = jwt.decode(token,
                   "secret123456",
                   algorithms=["HS256"],
                   options={"require": ["exp", "id", "username"]})
        return Token(username=decoded_token["username"], id=decoded_token["id"])
    except jwt.exceptions.InvalidSignatureError:
        res.status_code = 403
        return ErrorResponse(message="Unauthorized")
    except jwt.exceptions.MissingRequiredClaimError:
        res.status_code = 400
        return ErrorResponse(message="Invalid token")
    except jwt.exceptions.ExpiredSignatureError:
        res.status_code = 401
        return ErrorResponse(message="Expired Token")
    except jwt.exceptions.PyJWTError:
        res.status_code = 401
        return ErrorResponse(message="Bad request")


@app.get("/")
async def home():
    return RedirectResponse(url="/docs", status_code=302)


@app.post("/addMoneyToWallet")
async def add_money_to_waller(req: AddMoneyRequest, res: Response, token: str = Depends(oauth2_scheme)):
    result = verify_token(token, res)
    if isinstance(result, ErrorResponse):
        return result
    with sqlmodel.Session(engine) as session:
        statement = sqlmodel.select(Wallets).where(Wallets.user_id == result.id)
        wallet = session.exec(statement).one_or_none()
        if not wallet:
            res.status_code = 404
            return ErrorResponse(message="Wallet not found")
        wallet.balance += req.amount
        session.add(wallet)
        session.commit()
    return {"success": True, "data": None}

    # return jwt.decode(token, "secret123456", algorithms=["HS256"])
