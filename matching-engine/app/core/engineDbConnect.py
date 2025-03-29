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

    try:

        start_time = time.time()
        stage_times["start"] = start_time


        # Input validation
        if buyPrice <= 0:
            print("negative buy price")
            raise ValueError(400, "Buy price must be greater than 0")

        if len(sellOrders) <= 0:
            print("no sellers")
            raise ValueError(400, "Missing sell orders")

        if not buyOrder:
            print("no buy order")
            raise ValueError(400, "Missing buy order")

        
        async with async_session_maker() as session:
            
            stage_times["db_session_created"] = time.time()

            statement = sqlmodel.select(Wallets).where(Wallets.user_id == buyOrder.user_id)
            buyerWallet = await session.execute(statement)
            buyerWallet = buyerWallet.scalar_one_or_none()
            stage_times["buyer_wallet_fetched"] = time.time()

            if buyerWallet.balance < buyPrice:
                print("buy lacks funds")
                raise ValueError(400, "buyer lacks funds")

            # pay out the stocks
            current_stage = "pay_out_stocks"
            buyerStockTx, holding = await payOutStocks(session, buyOrder, buyPrice)
            stage_times["stocks_paid_out"] = time.time()

            # subtracts from buyer's wallet balance
            current_stage = "update_buyer_wallet"
            buyerWallet.balance -= buyPrice
            session.add(buyerWallet)

            # creates wallet transaction for taking money from the buyer
            buyerWalletTx = await addWalletTx(
                session, buyOrder, buyPrice, buyerStockTx.stock_tx_id, isDebit=True
            )
            stage_times["buyer_wallet_tx_created"] = time.time()

            # adds wallet tx id to stock stock_tx_id
            buyerStockTx = await addWalletTxToStockTx(
                session, buyerStockTx.stock_tx_id, buyerWalletTx.wallet_tx_id
            )
            stage_times["buyer_stock_tx_updated"] = time.time()

            # TODO stock added to portfolio
            current_stage = "process_sell_orders"
            amountSoldTotal = 0
            sell_order_count = len(sellOrders)

            for i, sellOrderTouple in enumerate(sellOrders):
                current_stage = f"sell_order_{i+i}_of_{sell_order_count}"

                sellOrder, sellQuantity = sellOrderTouple

                # calculates price using the price per stock and the *actual* amount sold
                sellPrice = sellOrder.price * sellQuantity

                statement = sqlmodel.select(Wallets).where(
                    Wallets.user_id == sellOrder.user_id
                )
                sellerWallet = await session.execute(statement)
                sellerWallet = sellerWallet.scalar_one_or_none()

                # adds money to sellers wallet
                sellerWallet.balance += sellPrice
                session.add(sellerWallet)

                # updates the sell order transaction to completed
                sellerStockTxId = sellOrder.stock_tx_id

                statement = sqlmodel.select(StockTransactions).where(
                    StockTransactions.stock_tx_id == sellerStockTxId
                )
                incompleteTx = await session.execute(statement)
                incompleteTx = incompleteTx.scalar_one_or_none()

                if not incompleteTx:
                    print("missing sell transaction")
                    raise ValueError(500, "Missing sell transaction to update")

                incompleteTx.order_status = OrderStatus.COMPLETED

                session.add(incompleteTx)

                # creates wallet transaction for paying the seller
                sellerWalletTx = await addWalletTx(
                    session, sellOrder, sellPrice, sellerStockTxId, isDebit=False
                )

                sellerStockTx = await addWalletTxToStockTx(
                    session, sellerStockTxId, sellerWalletTx.wallet_tx_id
                )

                amountSoldTotal += sellPrice

            stage_times["all_sell_orders_processed"] = time.time()

            if not amountSoldTotal == buyPrice:
                print("somehow we didnt do math right")
                raise ValueError(400, "Buyer seller mismatch")

            current_stage = "final_commit"
            await session.commit()
            stage_times["commit_completed"] = time.time()

            prev_stage = "start"
            for stage in stage_times:
                if stage != "start":
                    duration = stage_times[stage] - stage_times[prev_stage]
                    metrics[f"{prev_stage}_to_{stage}"] = duration
                    execution_metrics[f"{prev_stage}_to_{stage}"].append(duration)
                prev_stage = stage
            
            # Total execution time
            metrics["total_execution_time"] = stage_times["commit_completed"] - stage_times["start"]
            execution_metrics["total_execution_time"].append(metrics["total_execution_time"])
            execution_metrics["sell_order_count"].append(sell_order_count)
            
            processed_count += 1
            
            # Print periodic summary
            if processed_count % reporting_interval == 0:
                print(f"\n--- Performance Summary after {processed_count} executions ---")
                print(f"Total errors: {sum(error_counts.values())}")
                
                for stage, times in sorted(execution_metrics.items()):
                    if stage != "sell_order_count":
                        avg_time = mean(times[-reporting_interval:])
                        med_time = median(times[-reporting_interval:])
                        max_time = max(times[-reporting_interval:])
                        print(f"{stage}: avg={avg_time:.4f}s, median={med_time:.4f}s, max={max_time:.4f}s")
                
                print(f"Average sell order count: {mean(execution_metrics['sell_order_count'][-reporting_interval:]):.2f}")
                print("---------------------------------------------------\n")
            
            return "Transaction completed successfully"
            
    except Exception as e:
        error_counts[current_stage] += 1
        if processed_count % reporting_interval == 0 or sum(error_counts.values()) % 10 == 0:
            print(f"Error in {current_stage}: {str(e)}")
            print(f"Total errors by stage: {dict(error_counts)}")
        raise
'''
        # Update cache after committing the transaction
        incomplete_tx_dict = {incompleteTx.stock_tx_id: incompleteTx.model_dump()}
        cache.update(f"{CacheName.STOCK_TX}:{incompleteTx.user_id}", incomplete_tx_dict)
        cache.update(f"{CacheName.STOCK_PORTFOLIO}:{buyOrder.user_id}", holding)
        cache.set(
            f"{CacheName.WALLETS}:{buyOrder.user_id}",
            {"balance": buyerWallet.balance},
        )
        cache.set(
            f"{CacheName.WALLETS}:{sellOrder.user_id}",
            {"balance": sellerWallet.balance},
        )
        buyer_stock_tx_dict = {buyerStockTx.stock_tx_id: buyerStockTx.model_dump()}
        cache.update(
            f"{CacheName.STOCK_TX}:{buyerStockTx.user_id}", buyer_stock_tx_dict
        )
        seller_stock_tx_dict = {sellerStockTx.stock_tx_id: sellerStockTx.model_dump()}
        cache.update(
            f"{CacheName.STOCK_TX}:{sellerStockTx.user_id}", seller_stock_tx_dict
        )
        buyer_wallet_tx_dict = {buyerWalletTx.wallet_tx_id: buyerWalletTx.model_dump()}
        cache.update(
            f"{CacheName.WALLET_TX}:{buyerWalletTx.user_id}", buyer_wallet_tx_dict
        )
        seller_wallet_tx_dict = {
            sellerWalletTx.wallet_tx_id: sellerWalletTx.model_dump()
        }
        cache.update(
            f"{CacheName.WALLET_TX}:{sellerWalletTx.user_id}", seller_wallet_tx_dict
        )
'''

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

        # Update cache after committing the transaction
        buy_order_dict = {stockTx.stock_tx_id: stockTx.model_dump()}

        # Try Querying the stock cache, query db if cache fails
        stock = cache.get(f"{CacheName.STOCKS}:{stock_id}")
        if not stock:
            print("gatherStocks stock_name cache failed")
            query = sqlmodel.select(Stocks).where(Stocks.stock_id == stock_id)
            stock = await session.execute(query)
            stock = stock.scalar_one()
        portfolio_dict = {
            holding.stock_id: {
                "stock_name": stock.stock_name,
                **holding.model_dump(),
            }
        }
        cache.update(f"{CacheName.STOCK_TX}:{user_id}", buy_order_dict)
        # Don't cache anything if they don't own any
        if holding.quantity_owned > 0:
            cache.update(f"{CacheName.STOCK_PORTFOLIO}:{user_id}", portfolio_dict)
        return stockTx.stock_tx_id


async def payOutStocks(
    session, buyOrder: BuyOrder, buyPrice
) -> Tuple[StockTransactions, dict]:

    if not buyOrder:
        print("no buyer in payOutStocks")
        raise ValueError(400, "Missing buy order")

    statement = sqlmodel.select(StockPortfolios).where(
        (StockPortfolios.user_id == buyOrder.user_id)
        & (StockPortfolios.stock_id == buyOrder.stock_id)
    )
    buyerStockHolding = await session.execute(statement)
    buyerStockHolding = buyerStockHolding.scalar_one_or_none()

    # Try to get from cache first, query database as a fallback safety
    stock_name = cache.get(f"{CacheName.STOCKS}:{buyOrder.stock_id}")
    if not stock_name:
        print("Pay out stocks cache failed")
        stock_name_query = sqlmodel.select(Stocks.stock_name).where(
            Stocks.stock_id == buyOrder.stock_id
        )
        stock_name = await session.execute(stock_name_query)
        stock_name = stock_name.scalar_one()

    # The holding is for caching things later.
    holding = None
    if not buyerStockHolding:
        newStockHolding = StockPortfolios(
            user_id=buyOrder.user_id,
            stock_id=buyOrder.stock_id,
            quantity_owned=buyOrder.quantity,
        )
        session.add(newStockHolding)
        holding = {
            newStockHolding.stock_id: {
                "stock_name": stock_name,
                **newStockHolding.model_dump(),
            }
        }

    else:
        buyerStockHolding.quantity_owned += buyOrder.quantity
        session.add(buyerStockHolding)
        holding = {
            buyerStockHolding.user_id: {
                "stock_name": stock_name,
                **buyerStockHolding.model_dump(),
            }
        }

    stockTx = await addStockTx(
        session, buyOrder, isBuy=True, price=buyPrice, state=OrderStatus.COMPLETED
    )

    return stockTx, holding


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

        # Update cache after committing the transaction
        cancelled_dict = {
            transactionToBeCancelled.stock_tx_id: transactionToBeCancelled.model_dump()
        }
        cache.update(
            f"{CacheName.STOCK_TX}:{transactionToBeCancelled.user_id}", cancelled_dict
        )
        # TODO: Do we need to update the stock portfolio here?


async def getTransaction(stockTxId):
    async with async_session_maker() as session:
        statement = sqlmodel.select(StockTransactions).where(
            StockTransactions.stock_tx_id == stockTxId
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()


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


async def addWalletTxToStockTx(session, stockTxId, walletTxId) -> StockTransactions:

    statement = sqlmodel.select(StockTransactions).where(
        StockTransactions.stock_tx_id == stockTxId
    )
    stockTx = await session.execute(statement)
    stockTx = stockTx.scalar_one_or_none()

    stockTx.wallet_tx_id = walletTxId

    session.add(stockTx)
    return stockTx
