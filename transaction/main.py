import sqlmodel
import os
import dotenv
from sqlmodel import Session, desc
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from database import (
    Wallets,
    WalletTransactions,
    Stocks,
    StockPortfolios,
    StockTransactions,
)
from schemas.common import SuccessResponse, ErrorResponse
from schemas.transaction import AddMoneyRequest, WalletTxResult, PortfolioResult
from schemas.setup import Stock, StockSetup
from schemas import exception_handlers
from schemas.RedisClient import RedisClient, CacheName
from .db import get_session

dotenv.load_dotenv(override=True)
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))

cache = RedisClient()


app = FastAPI(root_path="/transaction")

app.add_exception_handler(StarletteHTTPException, exception_handlers.http_exception_handler)
app.add_exception_handler(RequestValidationError, exception_handlers.validation_exception_handler)

@app.get("/")
async def home():
    return RedirectResponse(url="/transaction/docs", status_code=302)

@app.get(
    "/getWalletBalance",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def get_wallet_balance(x_user_data: str = Header(None), session: Session = Depends(get_session)):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split("|")

    cache_hit = cache.get(CacheName.WALLETS, user_id)
    if cache_hit:
        return SuccessResponse(data={"balance": cache_hit['balance']})

    statement = sqlmodel.select(Wallets).where(Wallets.user_id == user_id)
    wallet = session.exec(statement).one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return SuccessResponse(data={"balance": wallet.balance})

@app.get(
    "/getWalletTransactions",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
    },
)
async def get_wallet_transactions(x_user_data: str = Header(None), session: Session = Depends(get_session)):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split("|")

    cache_hit = cache.get_list(CacheName.WALLET_TX, user_id, sort_key='time_stamp', desc=False)

    if cache_hit:
        return SuccessResponse(data=cache_hit)

    # Can't pass more than 4 params into select, so have to do it this way, see here
    # https://github.com/fastapi/sqlmodel/issues/92
    columns = [
        WalletTransactions.wallet_tx_id,
        WalletTransactions.is_debit,
        WalletTransactions.amount,
        WalletTransactions.time_stamp,
        StockTransactions.stock_tx_id,
    ]
    statement = (
        sqlmodel.select(*columns)
        .join(
            StockTransactions,
            WalletTransactions.stock_tx_id == StockTransactions.stock_tx_id,
        )
        .where(WalletTransactions.user_id == user_id)
        .order_by(WalletTransactions.time_stamp)
    )
    result = session.exec(statement).all()
    wallet_transactions = list(
        map(
            lambda tx: WalletTxResult(
                wallet_tx_id=tx[0],
                is_debit=tx[1],
                amount=tx[2],
                time_stamp=tx[3],
                stock_tx_id=tx[4],
            ),
            result,
        )
    )
    return SuccessResponse(data=wallet_transactions)

@app.post(
    "/addMoneyToWallet",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def add_money_to_wallet(req: AddMoneyRequest, x_user_data: str = Header(None), session: Session = Depends(get_session)):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split("|")

    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    statement = sqlmodel.select(Wallets).where(Wallets.user_id == user_id)
    wallet = session.exec(statement).one()
    balance = wallet.balance + req.amount
    wallet.balance = balance

    session.add(wallet)
    session.commit()

    cache.set(CacheName.WALLETS, user_id, {"balance": balance})
    return SuccessResponse()


@app.get(
    "/getStockPortfolio",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def get_stock_portfolio(x_user_data: str = Header(None), session: Session = Depends(get_session)):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")

    username, user_id = x_user_data.split("|")

    cache_hit = cache.get_list(CacheName.STOCK_PORTFOLIO, user_id, sort_key='stock_name')

    if cache_hit:
        return SuccessResponse(data=cache_hit)

    statement = (
        sqlmodel.select(
            StockPortfolios.stock_id,
            Stocks.stock_name,
            StockPortfolios.quantity_owned,
        )
        .join(Stocks, StockPortfolios.stock_id == Stocks.stock_id)
        .where(StockPortfolios.user_id == user_id)
        .order_by(desc(Stocks.stock_name))
    )
    result = session.exec(statement).all()
    portfolio = list(
        map(
            lambda stock: PortfolioResult(
                stock_id=stock[0], stock_name=stock[1], quantity_owned=stock[2]
            ),
            filter(lambda stock: stock[2] > 0, result)
        )
    )
    return SuccessResponse(data=portfolio)

@app.get(
    "/getStockTransactions",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def get_stock_transactions(x_user_data: str = Header(None), session: Session = Depends(get_session)):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")

    username, user_id = x_user_data.split("|")

    cache_hit = cache.get_list(CacheName.STOCK_TX, user_id, sort_key='time_stamp', desc=False)

    if cache_hit:
        return SuccessResponse(data=cache_hit)


    statement = sqlmodel.select(StockTransactions).where(
        StockTransactions.user_id == user_id
    ).order_by(StockTransactions.time_stamp)
    result = session.exec(statement).all()
    return SuccessResponse(data=result)

@app.post(
    "/createStock",
    status_code=201,
    responses={
        201: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def create_stock(stock: Stock, x_user_data: str = Header(None), session: Session = Depends(get_session)):

    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split("|")

    stock_name = stock.stock_name

    if not stock_name:
        raise HTTPException(status_code=400, detail="stock_name required")

    query = sqlmodel.select(Stocks).where(Stocks.stock_name == stock_name)
    existing_stock = session.exec(query).one_or_none()
    if existing_stock:
        raise HTTPException(status_code=409, detail="Stock already exists")
    new_stock = Stocks(stock_name=stock_name)
    session.add(new_stock)
    session.commit()
    session.refresh(new_stock)
    cache.set(CacheName.STOCKS, new_stock.stock_id, new_stock.dict())
    return SuccessResponse(data={"stock_id": new_stock.stock_id})

@app.post(
    "/addStockToUser",
    status_code=201,
    responses={
        201: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def add_stock_to_user(new_stock: StockSetup, x_user_data: str = Header(None), session: Session = Depends(get_session)):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")

    username, user_id = x_user_data.split("|")

    if not (new_stock.stock_id and new_stock.quantity):
        raise HTTPException(status_code=400, detail="Stock ID and quantity required")

    query = sqlmodel.select(Stocks).where(Stocks.stock_id == new_stock.stock_id)
    stock_exists = session.exec(query).one_or_none()
    if not stock_exists:
        raise HTTPException(status_code=404, detail="Stock not found")

    new_stock = StockPortfolios(
        user_id=user_id,
        stock_id=new_stock.stock_id,
        quantity_owned=new_stock.quantity,
    )
    session.add(new_stock)
    session.commit()
    session.refresh(new_stock)
    stock_dict = {
        new_stock.stock_id: {
            'stock_id': new_stock.stock_id,
            'quantity_owned': new_stock.quantity_owned,
            'stock_name': stock_exists.stock_name
        }
    }
    cache.update(CacheName.STOCK_PORTFOLIO, user_id, stock_dict)
    return SuccessResponse(data={"stock": new_stock})
