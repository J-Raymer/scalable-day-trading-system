from uuid import UUID
import jwt
import sqlmodel
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from fastapi import FastAPI, Response, Depends, HTTPException
from fastapi.responses import RedirectResponse
from database import Wallets, WalletTransactions, Users, Stocks
from schemas import SuccessResponse


app = FastAPI()
url = f"postgresql://admin:isolated-dean-primal-starving@localhost:5433/day_trader"
engine = sqlmodel.create_engine(url)



class AddMoneyRequest(BaseModel):
    amount: float

class ErrorResponse(BaseModel):
    detail: str

class Token(BaseModel):
    username: str
    id: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

SECRET_KEY = "secret123456"
ALGORITHM = "HS256"

async def verify_token(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"require": ["exp", "id", "username"]})
        return Token(username=decoded_token["username"], id=decoded_token["id"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired Token")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=403, detail="Unauthorized")
    except jwt.MissingRequiredClaimError:
        raise HTTPException(status_code=400, detail="Missing required claim")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/")
async def home():
    return RedirectResponse(url="/docs", status_code=302)

@app.get("/getWalletBalance", responses={
    200: {"model": SuccessResponse},
    400: {"model": ErrorResponse},
    401: {"model": ErrorResponse},
    403: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
})
async def get_wallet_balance(user: Token = Depends(verify_token)):
    with sqlmodel.Session(engine) as session:
        statement = sqlmodel.select(Wallets.balance).where(Wallets.user_id == user.id)
        balance = session.exec(statement).one_or_none()
        if not balance:
            raise HTTPException(status_code=404, detail="Not Found")
        return SuccessResponse(data={"balance": balance})


@app.get("/getWalletTransactions", responses={
    200: {"model": SuccessResponse},
    400: {"model": ErrorResponse},
    401: {"model": ErrorResponse},
    403: {"model": ErrorResponse},
})
async def get_wallet_transactions(user: Token = Depends(verify_token)):
    with sqlmodel.Session(engine) as session:
        # Overload issue need to pass params this way see here https://github.com/fastapi/sqlmodel/issues/92
        columns = [WalletTransactions.wallet_tx_id,
                   WalletTransactions.stock_tx_id,
                   WalletTransactions.is_debit,
                   WalletTransactions.amount,
                   WalletTransactions.time_stamp]
        statement = sqlmodel.select(
            *columns).where(Users.id == WalletTransactions.user_id)
        result = session.exec(statement).all()
        return result


@app.post("/addMoneyToWallet",
          responses={
              201: {"model": SuccessResponse},
              400: {"model": ErrorResponse},
              401: {"model": ErrorResponse},
              403: {"model": ErrorResponse},
              409: {"model": ErrorResponse}
          })
async def add_money_to_wallet(req: AddMoneyRequest, user: Token = Depends(verify_token)):
    with sqlmodel.Session(engine) as session:
        statement = sqlmodel.select(Wallets).where(Wallets.user_id == user.id)
        wallet = session.exec(statement).one_or_none()
        if not wallet:
            new_wallet = Wallets(user_id=UUID(user.id), balance=req.amount)
            session.add(new_wallet)
            session.commit()
            return SuccessResponse()
        wallet.balance += req.amount
        session.add(wallet)
        session.commit()
    return SuccessResponse()


@app.get("/getStockPrices",
         responses={
             200: {"model": SuccessResponse},
             400: {"model": ErrorResponse},
             401: {"model": ErrorResponse},
             409: {"model": ErrorResponse}
         })
async def get_stock_prices(user: Token = Depends(verify_token)):
    with sqlmodel.Session(engine) as session:
        statement = sqlmodel.select(Stocks)
        stocks = session.exec(statement).all()
        return SuccessResponse(data=stocks)
