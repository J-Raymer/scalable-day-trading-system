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
from collections import defaultdict
from statistics import mean, median
import time

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

execution_metrics = defaultdict(list)
error_counts = defaultdict(int)
processed_count = 0
reporting_interval = 100


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

    global processed_count
    metrics = {}
    stage_times = {}
    current_stage = "start"

    time = datetime.now()

    if buyPrice <= 0:
        raise ValueError(400, "Buy price must be greater than 0")

    if len(sellOrders) <= 0:
        raise ValueError(400, "Missing sell orders")

    try:

        start_time = time.time()
        stage_times["start"] = start_time

        async with async_session_maker() as session:
            stage_times["db_session_created"] = time.time()
            current_stage = "db_session_created"

            # Handling for taking money from buyer and giving them stock
            holding = await updatePortfolio(
                session, buyOrder.user_id, buyOrder.quantity, False, buyOrder.stock_id
            )
            stage_times["updated_portfolio"] = time.time()

            buyerStockTx = await addStockTx(
                session, buyOrder, True, buyPrice, OrderStatus.COMPLETED
            )
            stage_times["buyer_stock_tx_created"] = time.time()

            buyer_wallet = await updateWallet(session, buyOrder.user_id, buyPrice, True)
            stage_times["buyer_wallet_updated"] = time.time()

            buyerWalletTx = await addWalletTx(
                session, buyOrder, buyPrice, buyerStockTx.stock_tx_id, isDebit=True
            )
            stage_times["buyer_wallet_tx_created"] = time.time()

            buyerStockTx = await addWalletTxToStockTx(
                session, buyerStockTx.stock_tx_id, buyerWalletTx.wallet_tx_id, buyOrder.user_id
            )
            stage_times["buyer_complete"] = time.time()

            current_stage = "buyer_completed->process_sell_orders"
            sell_order_count = len(sellOrders)

            # Doing the same for seller(s)
            sell_order_cache_list: (str, Wallets, WalletTransactions, StockTransactions) = []
            for i, sellOrderTouple in enumerate(sellOrders):
                current_stage = f"sell_order_{i+1}_of_{sell_order_count}"

                sellOrder, sellQuantity = sellOrderTouple

                sellPrice = sellOrder.price * sellQuantity

                wallet = await updateWallet(session, sellOrder.user_id, sellPrice, False)

                sellerWalletTx = await addWalletTx(
                    session, sellOrder, sellPrice, sellOrder.stock_tx_id, False
                )

                # update the seller stock order status
                if sellOrder.is_child:
                    await updateStockOrderStatus(
                        session,
                        sellOrder.stock_tx_id,
                        OrderStatus.PARTIALLY_COMPLETE,
                        sellOrder.user_id
                    )
                    childTxId = await createChildTransaction(
                        session, sellOrder, sellQuantity
                    )

                    stock_tx = await addWalletTxToStockTx(
                        session, childTxId, sellerWalletTx.wallet_tx_id, sellOrder.user_id
                    )
                else:
                    await updateStockOrderStatus(
                        session,
                        sellOrder.stock_tx_id,
                        OrderStatus.COMPLETED,
                        sellOrder.user_id
                    )

                    stock_tx = await addWalletTxToStockTx(
                        session, sellOrder.stock_tx_id, sellerWalletTx.wallet_tx_id, sellOrder.user_id
                    )
                sell_order_cache_list.append((sellOrder.user_id, wallet, sellerWalletTx, stock_tx))


            stage_times["all_sell_orders_processed"] = time.time()

            current_stage = "final_commit"
            await session.commit()




         # TODO will have to delete if quantity is 0
        cache.set(f"WALLETS:{buyOrder.user_id}", {"balance": buyer_wallet.balance})
        for sell_order in sell_order_cache_list:
            cache.set(f"WALLETS:{sell_order[0]}", {"balance": sell_order[1].balance})







    except Exception as e:
        error_counts[current_stage] += 1
        if (
            processed_count % reporting_interval == 0
            or sum(error_counts.values()) % 10 == 0
        ):
            print(f"Error in {current_stage}: {str(e)}")
            print(f"Total errors by stage: {dict(error_counts)}")
        raise e


async def stockFromSeller(sellOrder):
    async with async_session_maker() as session:
        holding = await updatePortfolio(
            session, sellOrder.user_id, sellOrder.quantity, True, sellOrder.stock_id
        )
        holding_dict = holding.model_dump()

        stockTx = await addStockTx(
            session, sellOrder, False, sellOrder.price, OrderStatus.IN_PROGRESS
        )
        await session.commit()
        return stockTx.stock_tx_id


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
