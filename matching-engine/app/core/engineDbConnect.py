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
            await updatePortfolio(
                session, buyOrder.user_id, buyOrder.quantity, False, buyOrder.stock_id
            )
            stage_times["updated_portfolio"] = time.time()

            buyerStockTx = await addStockTx(
                session, buyOrder, True, buyPrice, OrderStatus.COMPLETED
            )
            stage_times["buyer_stock_tx_created"] = time.time()

            await updateWallet(session, buyOrder.user_id, buyPrice, True)
            stage_times["buyer_wallet_updated"] = time.time()

            buyerWalletTx = await addWalletTx(
                session, buyOrder, buyPrice, buyerStockTx.stock_tx_id, isDebit=True
            )
            stage_times["buyer_wallet_tx_created"] = time.time()

            buyerStockTx = await addWalletTxToStockTx(
                session, buyerStockTx.stock_tx_id, buyerWalletTx.wallet_tx_id
            )
            stage_times["buyer_complete"] = time.time()

            current_stage = "buyer_completed->process_sell_orders"
            sell_order_count = len(sellOrders)

            # Doing the same for seller(s)
            for i, sellOrderTouple in enumerate(sellOrders):
                current_stage = f"sell_order_{i+1}_of_{sell_order_count}"

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
                if sellQuantity < sellOrder.quantity:
                    await updateStockOrderStatus(
                        session,
                        sellOrder.stock_tx_id,
                        OrderStatus.PARTIALLY_COMPLETE,
                        sellOrder.quantity - sellQuantity,
                    )
                    # await createChildTransaction(session, sellOrder, sellQuantity)
                else:
                    await updateStockOrderStatus(
                        session,
                        sellOrder.stock_tx_id,
                        OrderStatus.COMPLETED,
                        sellQuantity,
                    )

            stage_times["all_sell_orders_processed"] = time.time()

            current_stage = "final_commit"
            await session.commit()
            stage_times["commit_completed"] = time.time()

            # prev_stage = "start"
            # for stage in stage_times:
            #    if stage != "start":
            #        duration = stage_times[stage] - stage_times[prev_stage]
            #        metrics[f"{prev_stage}_to_{stage}"] = duration
            #        execution_metrics[f"{prev_stage}_to_{stage}"].append(duration)
            #    prev_stage = stage

            # Total execution time
            # metrics["total_execution_time"] = stage_times["commit_completed"] - stage_times["start"]
            # execution_metrics["total_execution_time"].append(metrics["total_execution_time"])
            # execution_metrics["sell_order_count"].append(sell_order_count)

            processed_count += 1

            # Print periodic summary
            if processed_count % reporting_interval == -1:
                print(
                    f"\n--- Performance Summary after {processed_count} executions ---"
                )
                print(f"Total errors: {sum(error_counts.values())}")

                for stage, times in sorted(execution_metrics.items()):
                    if stage != "sell_order_count":
                        avg_time = mean(times[-reporting_interval:])
                        med_time = median(times[-reporting_interval:])
                        max_time = max(times[-reporting_interval:])
                        print(
                            f"{stage}: avg={avg_time:.4f}s, median={med_time:.4f}s, max={max_time:.4f}s"
                        )

                print(
                    f"Average sell order count: {mean(execution_metrics['sell_order_count'][-reporting_interval:]):.2f}"
                )
                print("---------------------------------------------------\n")

            # return "Transaction completed successfully"

    except Exception as e:
        error_counts[current_stage] += 1
        if (
            processed_count % reporting_interval == 0
            or sum(error_counts.values()) % 10 == 0
        ):
            print(f"Error in {current_stage}: {str(e)}")
            print(f"Total errors by stage: {dict(error_counts)}")
        raise


async def stockFromSeller(sellOrder):
    async with async_session_maker() as session:
        await updatePortfolio(
            session, sellOrder.user_id, sellOrder.quantity, True, sellOrder.stock_id
        )

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
