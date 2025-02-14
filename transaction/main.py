import jwt
import sqlmodel
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID
import os
import dotenv
from database import Wallets, WalletTransactions, Users, Stocks, StockPortfolios, StockTransactions
from schemas.common import SuccessResponse, ErrorResponse, User
from schemas.transaction import AddMoneyRequest, WalletTxResult, PortfolioResult
from schemas.setup import Stock, StockSetup
from fastapi.middleware.cors import CORSMiddleware

dotenv.load_dotenv()
DB_USERNAME = os.getenv("USERNAME")
DB_PASSWORD = os.getenv("PASSWORD")
DB_HOST = os.getenv("HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("DB_NAME")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

app = FastAPI(
    root_path="/transaction"
)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allows front end requests locally
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

url = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = sqlmodel.create_engine(url)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


async def verify_token(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"require": ["exp", "id", "username"]})
        return User(username=decoded_token["username"], id=decoded_token["id"])
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
    return RedirectResponse(url="/transaction/docs", status_code=302)


@app.get("/getWalletBalance", responses={
    200: {"model": SuccessResponse},
    400: {"model": ErrorResponse},
    401: {"model": ErrorResponse},
    403: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
})
async def get_wallet_balance(user: User = Depends(verify_token)):
    with sqlmodel.Session(engine) as session:
        statement = sqlmodel.select(Wallets).where(Wallets.user_id == user.id)
        wallet = session.exec(statement).one_or_none()
        if not wallet:
            new_wallet = Wallets(user_id=user.id)
            session.add(new_wallet)
            session.commit()
            return SuccessResponse(data={"balance": 0})
        return SuccessResponse(data={"balance": wallet.balance})


@app.get("/getWalletTransactions", responses={
    200: {"model": SuccessResponse},
    400: {"model": ErrorResponse},
    401: {"model": ErrorResponse},
    403: {"model": ErrorResponse},
})
async def get_wallet_transactions(user: User = Depends(verify_token)):
    with (sqlmodel.Session(engine) as session):
        # Can't pass more than 4 params into select, so have to do it this way, see here
        # https://github.com/fastapi/sqlmodel/issues/92
        columns = [WalletTransactions.wallet_tx_id,
                   WalletTransactions.is_debit,
                   WalletTransactions.amount,
                   WalletTransactions.time_stamp,
                   StockTransactions.stock_tx_id
                   ]
        statement = sqlmodel.select(
            *columns
        ).join(StockTransactions,
               WalletTransactions.wallet_tx_id == StockTransactions.wallet_tx_id
               ).where(Users.id == WalletTransactions.user_id)
        result = session.exec(statement).all()
        wallet_transactions = list(map(lambda tx: WalletTxResult(
            wallet_tx_id=tx[0],
            is_debit=tx[1],
            amount=tx[2],
            time_stamp=tx[3],
            stock_tx_id=tx[4]),
            result))
        return SuccessResponse(data=wallet_transactions)


@app.post("/addMoneyToWallet",
          responses={
              200: {"model": SuccessResponse},
              400: {"model": ErrorResponse},
              401: {"model": ErrorResponse},
              403: {"model": ErrorResponse},
              409: {"model": ErrorResponse}
          })
async def add_money_to_wallet(req: AddMoneyRequest, user: User = Depends(verify_token)):
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")
    
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
async def get_stock_prices(user: User = Depends(verify_token)):
    with sqlmodel.Session(engine) as session:
        statement = sqlmodel.select(Stocks)
        stocks = session.exec(statement).all()
        return SuccessResponse(data=stocks)


@app.get("/getStockPortfolio",
         responses={
             200: {"model": SuccessResponse},
             400: {"model": ErrorResponse},
             401: {"model": ErrorResponse},
             409: {"model": ErrorResponse}
         })
async def get_stock_portfolio(user: User = Depends(verify_token)):
    with sqlmodel.Session(engine) as session:
        statement = sqlmodel.select(
            StockPortfolios.stock_id,
            Stocks.stock_name,
            StockPortfolios.quantity_owned
        ).join(Stocks, StockPortfolios.stock_id == Stocks.stock_id
               ).where(StockPortfolios.user_id == user.id)
        result = session.exec(statement).all()
        portfolio = list(map(lambda stock: PortfolioResult(stock_id=stock[0], stock_name=stock[1], quantity_owned=stock[2]), result))
        return SuccessResponse(data=portfolio)


@app.get("/getStockTransactions",
         responses={
             200: {"model": SuccessResponse},
             400: {"model": ErrorResponse},
             401: {"model": ErrorResponse},
             409: {"model": ErrorResponse}
         })
async def get_stock_transactions(user: User = Depends(verify_token)):
    with sqlmodel.Session(engine) as session:
        statement = sqlmodel.select(StockTransactions).where(StockTransactions.user_id == user.id)
    result = session.exec(statement).all()
    return SuccessResponse(data=result)


@app.post("/createStock",
          status_code=201,
          responses={
              201: {"model": SuccessResponse},
              400: {"model": ErrorResponse},
              401: {"model": ErrorResponse},
              403: {"model": ErrorResponse},
              409: {"model": ErrorResponse}
          }
          )
async def create_stock(stock: Stock, user: User = Depends(verify_token)):
    stock_name = stock.stock_name
    if not stock_name:
        raise HTTPException(status_code=400, detail="stock_name required")
    with sqlmodel.Session(engine) as session:
        query = session.query(Stocks).where(Stocks.stock_name == stock_name)
        existing_stock = session.exec(query).one_or_none()
        if existing_stock:
            raise HTTPException(status_code=409, detail="Stock already exists")
        new_stock = Stocks(stock_name=stock_name)
        session.add(new_stock)
        session.commit()
        session.refresh(new_stock)
        return SuccessResponse(data={"stock_id": new_stock.stock_id})


@app.post("/addStockToUser",
          status_code=201,
          responses={
              201: {"model": SuccessResponse},
              400: {"model": ErrorResponse},
              401: {"model": ErrorResponse},
              403: {"model": ErrorResponse},
              404: {"model": ErrorResponse},
              409: {"model": ErrorResponse}
          }
          )
async def add_stock_to_user(new_stock: StockSetup, user: User = Depends(verify_token)):
    if not (new_stock.stock_id and new_stock.quantity):
        raise HTTPException(status_code=400, detail="Stock ID and quantity required")

    with sqlmodel.Session(engine) as session:
        query = session.query(Stocks).where(Stocks.stock_id == new_stock.stock_id)
        stock_exists = session.exec(query).one_or_none()
        if not stock_exists:
            raise HTTPException(status_code=404, detail="Stock not found")

        new_stock = StockPortfolios(user_id=user.id, stock_id=new_stock.stock_id, quantity_owned=new_stock.quantity)
        session.add(new_stock)
        session.commit()
        session.refresh(new_stock)
        return SuccessResponse(data={"stock": new_stock})
