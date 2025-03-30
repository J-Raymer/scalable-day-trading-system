from typing import Tuple
from schemas.common import SuccessResponse
from schemas.engine import BuyOrder
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
from .db_methods import *

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


async def getStockData():
    async with async_session_maker() as session:
        query = sqlmodel.select(Stocks).order_by(desc(Stocks.stock_name))
        result = await session.execute(query)

        if result:
            return result.scalars().all()


# takes buy order and list of sell orders
# connects to database and checks if buyer has funds
# takes funds from buyer and distributes to seller(s)
#
# Main purpose of writing it like this is to execute taking money from the buyer and giving
#   it to sellers as one transaction
async def fundsBuyerToSeller(buyOrder: BuyOrder, sellOrders, buyPrice):
    time = datetime.now()

    if buyPrice <= 0:
        raise ValueError(400, "Buy price must be greater than 0")

    if len(sellOrders) <= 0:
        raise ValueError(400, "Missing sell orders")

    async with async_session_maker() as session:

        # Handling for taking money from buyer and giving them stock
        await updatePortfolio(
            session, buyOrder.user_id, buyOrder.quantity, False, buyOrder.stock_id
        )

        buyerStockTx = await addStockTx(
            session, buyOrder, True, buyPrice, OrderStatus.COMPLETED
        )

        await updateWallet(session, buyOrder.user_id, buyPrice, True)

        buyerWalletTx = await addWalletTx(
            session, buyOrder, buyPrice, buyerStockTx.stock_tx_id, isDebit=True
        )

        buyerStockTx = await addWalletTxToStockTx(
            session, buyerStockTx.stock_tx_id, buyerWalletTx.wallet_tx_id
        )

        # Doing the same for seller(s)
        for sellOrderTouple in sellOrders:
            sellOrder, sellQuantity = sellOrderTouple

            sellPrice = sellOrder.price * sellQuantity

            await updateWallet(session, sellOrder.user_id, sellPrice, False)

            sellerWalletTx = await addWalletTx(
                session, buyOrder, buyPrice, sellOrder.stock_tx_id, False
            )

            await addWalletTxToStockTx(
                session, sellOrder.stock_tx_id, sellerWalletTx.wallet_tx_id
            )

            # update the seller stock order status
            await updateStockOrderStatus(
                session, sellOrder.stock_tx_id, OrderStatus.COMPLETED
            )

        await session.commit()


async def gatherStocks(order, user_id, stock_id, stock_amount):
    async with async_session_maker() as session:
        statement = sqlmodel.select(StockPortfolios).where(
            (StockPortfolios.user_id == user_id)
            & (StockPortfolios.stock_id == stock_id)
        )
        holding = await session.execute(statement)
        holding = holding.scalar_one_or_none()

        if not holding or holding.quantity_owned < stock_amount:
            raise ValueError(500, "you cannot sell stocks you dont own")

        holding.quantity_owned -= stock_amount
        stockTx = await addStockTx(
            session,
            order,
            isBuy=False,
            price=order.price,
            state=OrderStatus.IN_PROGRESS,
        )
        session.add(holding)
        await session.commit()

        return stockTx.stock_tx_id


async def payOutStocks(
    session, buyOrder: BuyOrder, buyPrice
) -> Tuple[StockTransactions, dict]:

    if not buyOrder:
        raise ValueError(400, "Missing buy order")

    statement = sqlmodel.select(StockPortfolios).where(
        (StockPortfolios.user_id == buyOrder.user_id)
        & (StockPortfolios.stock_id == buyOrder.stock_id)
    )
    buyerStockHolding = await session.execute(statement)
    buyerStockHolding = buyerStockHolding.scalar_one_or_none()

    buyerStockHolding.quantity_owned += buyOrder.quantity
    session.add(buyerStockHolding)

    stockTx = await addStockTx(
        session, buyOrder, isBuy=True, price=buyPrice, state=OrderStatus.COMPLETED
    )

    return stockTx


async def cancelTransaction(stockTxId):
    async with async_session_maker() as session:
        statement = sqlmodel.select(StockTransactions).where(
            StockTransactions.stock_tx_id == stockTxId
        )
        transactionToBeCancelled = await session.execute(statement)
        transactionToBeCancelled = transactionToBeCancelled.scalar_one_or_none()

        transactionToBeCancelled.order_status = OrderStatus.CANCELLED
        session.add(transactionToBeCancelled)

        statement = sqlmodel.select(StockPortfolios).where(
            (StockPortfolios.user_id == transactionToBeCancelled.user_id)
            & (StockPortfolios.stock_id == transactionToBeCancelled.stock_id)
        )
        sellerPortfolio = await session.execute(statement)
        sellerPortfolio = sellerPortfolio.scalar_one_or_none()

        sellerPortfolio.quantity_owned += transactionToBeCancelled.quantity
        session.add(sellerPortfolio)

        await session.commit()


async def createChildTransaction(order, parentStockTxId):
    async with async_session_maker() as session:
        time = datetime.now()

        childTx = StockTransactions(
            stock_id=order.stock_id,
            order_status=OrderStatus.IN_PROGRESS,
            is_buy=False,
            order_type=order.order_type,
            stock_price=order.price,
            quantity=order.quantity,
            parent_stock_tx_id=parentStockTxId,
            user_id=order.user_id,
        )

        session.add(childTx)
        await session.flush()
        await session.refresh(childTx)
        await session.commit()
        return childTx.stock_tx_id
