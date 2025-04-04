from schemas.common import SuccessResponse
import dotenv
import os
import sqlmodel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool  # Disable connection pooling
from sqlmodel import desc
from database import (
    Stocks,
    Wallets,
    WalletTransactions,
    StockTransactions,
    StockPortfolios,
    OrderStatus,
)
from datetime import datetime

dotenv.load_dotenv(override=True)
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("DB_NAME")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
url = f"postgresql+asyncpg://{USERNAME}:{PASSWORD}@pgbouncer:6432/{DB_NAME}"
from schemas.RedisClient import RedisClient, CacheName

# Disable connection pooling (use PgBouncer instead)
engine = create_async_engine(url, echo=False, poolclass=NullPool)
async_session_maker = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

cache = RedisClient()


async def getWallet(user_id) -> Wallets:
    async with async_session_maker() as session:
        statement = sqlmodel.select(Wallets).where(Wallets.user_id == user_id)
        result = await session.execute(statement)
        wallet = result.scalar_one_or_none()

        return wallet.balance


async def getStockTransaction(stockTxId):
    async with async_session_maker() as session:
        statement = sqlmodel.select(StockTransactions).where(
            StockTransactions.stock_tx_id == stockTxId
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()


async def getWalletTransaction(walletTxId):
    async with async_session_maker() as session:
        statement = sqlmodel.select(WalletTransactions).where(
            WalletTransactions.stock_tx_id == walletTxId
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()


async def getPortfolio(user_id, stock_id):
    async with async_session_maker() as session:
        statement = sqlmodel.select(StockPortfolios).where(
            (StockPortfolios.user_id == user_id)
            & (StockPortfolios.stock_id == stock_id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()


async def updateWallet(session, user_id, amount, isDebit):
    statement = sqlmodel.select(Wallets).where(Wallets.user_id == user_id)
    result = await session.execute(statement)
    wallet = result.scalar_one_or_none()

    if wallet is None:
        raise ValueError(400, "No wallet found")

    if amount == 0:
        raise ValueError(400, "Amount is 0")

    if isDebit:
        if wallet.balance < amount:
            raise ValueError(400, "Buyer lacks funds")
        wallet.balance -= amount
    else:
        wallet.balance += amount

    session.add(wallet)


async def updatePortfolio(session, user_id, amount, isDebit, stock_id):
    statement = sqlmodel.select(StockPortfolios).where(
        (StockPortfolios.user_id == user_id) & (StockPortfolios.stock_id == stock_id)
    )
    result = await session.execute(statement)
    holding = result.scalar_one_or_none()

    if holding is None:  # this means the user doesn't own the stock yet
        newStockHolding = StockPortfolios(
            user_id=user_id,
            stock_id=stock_id,
            quantity_owned=amount,
        )
        session.add(newStockHolding)
    else:
        if isDebit:
            if holding.quantity_owned < amount:
                raise ValueError(400, "Seller lacks the stocks for this order")
            holding.quantity_owned -= amount
        else:
            holding.quantity_owned += amount
        session.add(holding)


async def updateStockOrderStatus(session, stock_tx_id, status, newQuantity):
    statement = sqlmodel.select(StockTransactions).where(
        StockTransactions.stock_tx_id == stock_tx_id
    )
    result = await session.execute(statement)
    stockTx = result.scalar_one_or_none()

    stockTx.order_status = status
    # stockTx.quantity = newQuantity
    session.add(stockTx)


async def addWalletTx(
    session, order, orderValue, stockTxId, isDebit: bool
) -> WalletTransactions:
    time = str(datetime.now())
    walletTx = WalletTransactions(
        user_id=order.user_id,
        stock_tx_id=stockTxId,
        is_debit=isDebit,
        amount=orderValue,
    )

    session.add(walletTx)
    await session.flush()
    await session.refresh(walletTx)
    return walletTx


async def addStockTx(
    session, order, isBuy: bool, price: int, state: OrderStatus
) -> StockTransactions:

    stockTx = StockTransactions(
        stock_id=order.stock_id,
        order_status=state,
        is_buy=isBuy,
        order_type=order.order_type,
        quantity=order.quantity,
        parent_stock_tx_id=None,
        user_id=order.user_id,
        stock_price=price,
    )

    # we should just put this ^^^ but for clarity im just gonna leave it like this for now
    if isBuy:
        stockTx.stock_price = (
            price / order.quantity
        )  # buy orders will pass in the total buy price from the combined orders
    else:
        stockTx.stock_price = (
            price  # sell order will pass in their individual sell price
        )

    session.add(stockTx)
    await session.flush()
    await session.refresh(stockTx)
    return stockTx


async def addWalletTxToStockTx(session, stockTxId, walletTxId) -> StockTransactions:

    statement = sqlmodel.select(StockTransactions).where(
        StockTransactions.stock_tx_id == stockTxId
    )
    stockTx = await session.execute(statement)
    stockTx = stockTx.scalar_one_or_none()

    stockTx.wallet_tx_id = walletTxId

    session.add(stockTx)
    return stockTx


async def setToPartiallyComplete(stockTxId, quantity):
    async with async_session_maker() as session:
        statement = sqlmodel.select(StockTransactions).where(
            StockTransactions.stock_tx_id == stockTxId
        )
        transactionToChange = await session.execute(statement)
        transactionToChange = transactionToChange.scalar_one_or_none()

        transactionToChange.order_status = OrderStatus.PARTIALLY_COMPLETE
        transactionToChange.quantity = quantity

        session.add(transactionToChange)
        await session.commit()
        return SuccessResponse()


async def createChildTransaction(session, order, newQuantity):
    try:
        if order is None:
            print("no order into child")
        # if parentTxId is None:
        #     print("no parentTxId into child")

        childTx = StockTransactions(
            stock_id=order.stock_id,
            order_status=OrderStatus.COMPLETED,
            is_buy=False,
            order_type=order.order_type,
            stock_price=order.price,
            quantity=newQuantity,
            parent_stock_tx_id=order.stock_tx_id,
            user_id=order.user_id,
        )

        if childTx is None:
            print("childTx is None after creation")
            raise ValueError(400, "FUCK YOU")
        else:
            session.add(childTx)
            await session.flush()
            await session.refresh(childTx)
            await session.commit()
            return childTx.stock_tx_id
    except Exception as e:
        print(f"error creating child transaction {e}")
        raise
