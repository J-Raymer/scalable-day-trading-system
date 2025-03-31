import os
import dotenv
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
import asyncio
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
from .db import get_session, async_session_maker

dotenv.load_dotenv(override=True)
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))

cache = RedisClient()

app = FastAPI(root_path="/transaction")

app.add_exception_handler(
    StarletteHTTPException, exception_handlers.http_exception_handler
)
app.add_exception_handler(
    RequestValidationError, exception_handlers.validation_exception_handler
)

# @app.get("/")
# async def home():
#     return RedirectResponse(url="/transaction/docs", status_code=302)


async def get_wallet_balance(user_id: str):

    async with async_session_maker() as session:
        cache_hit = cache.get(f"{CacheName.WALLETS}:{user_id}")
        if cache_hit:
            return SuccessResponse(data={"balance": cache_hit["balance"]})

        async with session.begin():
            print("CACHE MISS in get wallet balance")
            statement = select(Wallets).where(Wallets.user_id == user_id)
            result = await session.execute(statement)
            wallet = result.scalar_one_or_none()

        if not wallet:
            raise ValueError(404, "Wallet not found")

        return SuccessResponse(data={"balance": wallet.balance})


async def get_wallet_transactions(user_id: str):
    async with async_session_maker() as session:
        cache_hit = cache.get(f"{CacheName.WALLET_TX}:{user_id}")
        if cache_hit:
            return SuccessResponse(data=list(cache_hit.values()))

        async with session.begin():
            print("Cache MISS in get wallet transactions")
            statement = (
                select(WalletTransactions)
                .join(
                    StockTransactions,
                    WalletTransactions.stock_tx_id == StockTransactions.stock_tx_id,
                )
                .where(WalletTransactions.user_id == user_id)
                .order_by(WalletTransactions.time_stamp)
            )
            result = await session.execute(statement)
            wallet_transactions = result.scalars().all()

        return SuccessResponse(
            data=[WalletTxResult.from_orm(tx) for tx in wallet_transactions]
        )


async def add_money_to_wallet(
    req: AddMoneyRequest,
    user_id: str,
):
    async with async_session_maker() as session:
        if req.amount <= 0:
            raise ValueError(400, "Amount must be greater than 0")

        async with session.begin():
            statement = select(Wallets).where(Wallets.user_id == user_id)
            result = await session.execute(statement)
            wallet = result.scalar_one_or_none()

        if not wallet:
            raise ValueError(404, "Wallet not found")

        wallet.balance += req.amount

        session.add(wallet)
        await session.commit()

        cache.set(f"{CacheName.WALLETS}:{user_id}", {"balance": wallet.balance})
        return SuccessResponse()


async def get_stock_portfolio(user_id: str):
    async with async_session_maker() as session:
        cache_hit = cache.get(f"{CacheName.STOCK_PORTFOLIO}:{user_id}")
        if cache_hit:
            return SuccessResponse(
                data=sorted(
                    filter(lambda stock: stock['quantity_owned'] > 0, list(cache_hit.values())),
                    reverse=True,
                    key=lambda x: x["stock_name"],
                )
            )

        async with session.begin():
            print("CACHE MISS in get stock portfolio")
            statement = (
                select(StockPortfolios, Stocks.stock_name)
                .join(Stocks, StockPortfolios.stock_id == Stocks.stock_id)
                .where(StockPortfolios.user_id == user_id)
                .order_by(Stocks.stock_name)
            )
            result = await session.execute(statement)
            portfolio = result.all()

        data = [
            PortfolioResult(
                stock_id=stock[0].stock_id,
                stock_name=stock[1],
                quantity_owned=stock[0].quantity_owned,
            )
            for stock in portfolio
            if stock[0].quantity_owned > 0
        ]
        data.sort(reverse=True, key=lambda stock: stock.stock_name)
        return SuccessResponse(data=data)


async def get_stock_transactions(user_id: str):
    async with async_session_maker() as session:
        cache_hit = cache.get(f"{CacheName.STOCK_TX}:{user_id}")
        if cache_hit:
            return SuccessResponse(data=list(cache_hit.values()))

        async with session.begin():
            print("Cache MISS in get stock transactions")
            statement = (
                select(StockTransactions)
                .where(StockTransactions.user_id == user_id)
                .order_by(StockTransactions.time_stamp)
            )
            result = await session.execute(statement)
            stock_transactions = result.scalars().all()

        return SuccessResponse(data=stock_transactions)


async def create_stock(
    stock: Stock,
    user_id: str,
):
    async with async_session_maker() as session:
        stock_name = stock.stock_name
        if not stock_name:
            raise ValueError(400, "stock_name required")

        async with session.begin():
            query = select(Stocks).where(Stocks.stock_name == stock_name)
            result = await session.execute(query)
            existing_stock = result.scalar_one_or_none()

        if existing_stock:
            raise ValueError(409, "Stock already exists")

        new_stock = Stocks(stock_name=stock_name)
        session.add(new_stock)
        await session.commit()

        # Cache the stock id with the stock name
        cache.update(CacheName.STOCKS, {new_stock.stock_id: new_stock.stock_name})
        return SuccessResponse(data={"stock_id": new_stock.stock_id})


async def add_stock_to_user(
    new_stock: StockSetup,
    user_id: str,
):
    async with async_session_maker() as session:
        if not (new_stock.stock_id and new_stock.quantity):
            raise ValueError(400, "Stock ID and quantity required")

        async with session.begin():
            query = select(Stocks).where(Stocks.stock_id == new_stock.stock_id)
            result = await session.execute(query)
            stock_exists = result.scalar_one_or_none()

        if not stock_exists:
            raise ValueError(404, "Stock not found")

        stock_portfolio = StockPortfolios(
            user_id=user_id,
            stock_id=new_stock.stock_id,
            quantity_owned=new_stock.quantity,
        )
        session.add(stock_portfolio)
        await session.commit()
        stock_id = new_stock.stock_id
        stocks = cache.get(CacheName.STOCKS)
        if not stocks:
            print("cache miss getting stocks in add_stock_to_user")
        stock_name = stocks[str(stock_id)]
        portfolio_item = { str(stock_id): {
            "stock_name": stock_name,
            **stock_portfolio.model_dump()
        } }

        # TODO will have to delete if quantity is 0
        cache.update(f'{CacheName.STOCK_PORTFOLIO}:{user_id}', portfolio_item)
        return SuccessResponse(data={"stock": stock_portfolio})
