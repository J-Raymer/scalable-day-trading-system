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
            tx_item = {
                buyerStockTx.stock_tx_id: buyerStockTx.model_dump()
            }
            cache.update(f'STOCK_TX:{buyOrder.user_id}', tx_item)


            holding_dict = holding.model_dump()
            stock_id = holding_dict.get('stock_id')
            stocks = cache.get("STOCKS")
            if not stocks:
                print("cache miss getting stocks in updatePortfolio")
            stock_name = stocks[str(stock_id)]
            portfolio_item = { str(stock_id): {
                "stock_name": stock_name,
                **holding_dict
            } }

            buyer_wallet_tx_item = {
                buyerWalletTx.wallet_tx_id: buyerWalletTx.model_dump()   }

             # TODO will have to delete if quantity is 0
            cache.update(f'STOCK_PORTFOLIO:{buyOrder.user_id}', portfolio_item)
            cache.set(f"WALLETS:{buyOrder.user_id}", {"balance": buyer_wallet.balance})
            cache.update(f'WALLET_TX:{buyOrder.user_id}', buyer_wallet_tx_item)
            for sell_order in sell_order_cache_list:
                cache.set(f"WALLETS:{sell_order[0]}", {"balance": sell_order[1].balance})
                wallet_tx_item = { sell_order[2].wallet_tx_id: sell_order[2].model_dump()    }
                wallet_update_result = cache.update(f'WALLET_TX:{sell_order[0]}', wallet_tx_item)
                print(f'WALLET UPDATE RESULT {wallet_update_result}  {sell_order[0]}  {wallet_tx_item}', )

                stockTxDict = sell_order[3].model_dump()
                tx_item = {
                    sell_order[3].stock_tx_id: stockTxDict

                }
                cache.update(f'STOCK_TX:{sell_order[0]}', tx_item)

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
        stock_id = holding_dict.get('stock_id')
        stocks = cache.get("STOCKS")
        if not stocks:
            print("cache miss getting stocks in updatePortfolio")
        stock_name = stocks[str(stock_id)]
        portfolio_item = { str(stock_id): {
            "stock_name": stock_name,
            **holding_dict
        } }
         # TODO will have to delete if quantity is 0
        cache.update(f'STOCK_PORTFOLIO:{sellOrder.user_id}', portfolio_item)
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
        stock_id = transactionToBeCancelled.stock_id
        stocks = cache.get("STOCKS")
        if not stocks:
            print("Cache miss getting stocks in cancelTransaction")
        stock_name = stocks[str(stock_id)]
        portfolio_item = { str(stock_id): {
            "stock_name": stock_name,
            **sellerPortfolio.model_dump()
        } }
        # TODO will have to delete if quantity is 0

        transactions_item = {
            stockTxId: transactionToBeCancelled.model_dump()
        }
        cache.update(f'STOCK_TX:{transactionToBeCancelled.user_id}', transactions_item)
        cache.update(f'STOCK_PORTFOLIO:{transactionToBeCancelled.user_id}', portfolio_item)