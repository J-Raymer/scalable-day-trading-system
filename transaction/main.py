import os
import dotenv
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

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
async def get_wallet_balance(x_user_data: str = Header(None), session: AsyncSession = Depends(get_session)):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split("|")

    cache_hit = cache.get(f'{CacheName.WALLETS}:{user_id}')
    if cache_hit:
        print("CACHE hit in get wallet balance")
        return SuccessResponse(data={"balance": cache_hit['balance']})

    async with session.begin():
        statement = select(Wallets).where(Wallets.user_id == user_id)
        result = await session.execute(statement)
        wallet = result.scalar_one_or_none()
    
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
async def get_wallet_transactions(x_user_data: str = Header(None), session: AsyncSession = Depends(get_session)):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split("|")

    cache_hit = cache.get(f'{CacheName.WALLET_TX}:{user_id}')
    if cache_hit:
        print("Cache Hit in get wallet transactions")
        return SuccessResponse(data=list(cache_hit.values()))

    async with session.begin():
        statement = select(WalletTransactions).join(
            StockTransactions,
            WalletTransactions.stock_tx_id == StockTransactions.stock_tx_id,
        ).where(WalletTransactions.user_id == user_id).order_by(WalletTransactions.time_stamp)
        result = await session.execute(statement)
        wallet_transactions = result.scalars().all()

    return SuccessResponse(data=[WalletTxResult.from_orm(tx) for tx in wallet_transactions])

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
async def add_money_to_wallet(req: AddMoneyRequest, x_user_data: str = Header(None), session: AsyncSession = Depends(get_session)):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split("|")

    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    async with session.begin():
        statement = select(Wallets).where(Wallets.user_id == user_id)
        result = await session.execute(statement)
        wallet = result.scalar_one_or_none()

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    wallet.balance += req.amount

    session.add(wallet)
    await session.commit()

    cache.set(f'{CacheName.WALLETS}:{user_id}', {"balance": wallet.balance})
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
async def get_stock_portfolio(x_user_data: str = Header(None), session: AsyncSession = Depends(get_session)):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")

    username, user_id = x_user_data.split("|")

    cache_hit = cache.get(f'{CacheName.STOCK_PORTFOLIO}:{user_id}')
    if cache_hit:
        print("CACHE hit in get stock portfolio")
        return SuccessResponse(data=sorted(list(cache_hit.values()), reverse=True, key=lambda x: x['stock_name']))

    async with session.begin():
        statement = (
            select(StockPortfolios, Stocks.stock_name)
            .join(Stocks, StockPortfolios.stock_id == Stocks.stock_id)
            .where(StockPortfolios.user_id == user_id)
            .order_by(Stocks.stock_name)
        )
        result = await session.execute(statement)
        portfolio = result.all()

    return SuccessResponse(data=[PortfolioResult(stock_id=stock[0].stock_id, stock_name=stock[1], quantity_owned=stock[0].quantity_owned) for stock in portfolio if stock[0].quantity_owned > 0])

@app.get(
    "/getStockTransactions",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def get_stock_transactions(x_user_data: str = Header(None), session: AsyncSession = Depends(get_session)):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")

    username, user_id = x_user_data.split("|")

    cache_hit = cache.get(f'{CacheName.STOCK_TX}:{user_id}')
    if cache_hit:
        print('Cache hit in get stock transactions')
        return SuccessResponse(data=list(cache_hit.values()))

    async with session.begin():
        statement = select(StockTransactions).where(StockTransactions.user_id == user_id).order_by(StockTransactions.time_stamp)
        result = await session.execute(statement)
        stock_transactions = result.scalars().all()

    return SuccessResponse(data=stock_transactions)

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
async def create_stock(stock: Stock, x_user_data: str = Header(None), session: AsyncSession = Depends(get_session)):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split("|")

    stock_name = stock.stock_name
    if not stock_name:
        raise HTTPException(status_code=400, detail="stock_name required")

    async with session.begin():
        query = select(Stocks).where(Stocks.stock_name == stock_name)
        result = await session.execute(query)
        existing_stock = result.scalar_one_or_none()

    if existing_stock:
        raise HTTPException(status_code=409, detail="Stock already exists")

    new_stock = Stocks(stock_name=stock_name)
    session.add(new_stock)
    await session.commit()

    # Cache the stock id with the stock name
    cache.update(CacheName.STOCKS, {new_stock.stock_id: new_stock.stock_name})
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
async def add_stock_to_user(new_stock: StockSetup, x_user_data: str = Header(None), session: AsyncSession = Depends(get_session)):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")

    username, user_id = x_user_data.split("|")

    if not (new_stock.stock_id and new_stock.quantity):
        raise HTTPException(status_code=400, detail="Stock ID and quantity required")

    async with session.begin():
        query = select(Stocks).where(Stocks.stock_id == new_stock.stock_id)
        result = await session.execute(query)
        stock_exists = result.scalar_one_or_none()

    if not stock_exists:
        raise HTTPException(status_code=404, detail="Stock not found")

    stock_portfolio = StockPortfolios(user_id=user_id, stock_id=new_stock.stock_id, quantity_owned=new_stock.quantity)
    session.add(stock_portfolio)
    await session.commit()

    return SuccessResponse(data={"stock": stock_portfolio})
