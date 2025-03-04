from schemas.common import SuccessResponse
from schemas.engine import BuyOrder
import dotenv
import os
import sqlmodel
from fastapi import HTTPException
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
url = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
from schemas.RedisClient import RedisClient, CacheName

engine = sqlmodel.create_engine(url)

cache = RedisClient()

def getStockData():
    with sqlmodel.Session(engine) as session:
        query = sqlmodel.select(Stocks).order_by(desc(Stocks.stock_name))
        result = session.exec(query)

        if result:
            return result.all()


# takes buy order and list of sell orders
# connects to database and checks if buyer has funds
# takes funds from buyer and distributes to seller(s)
#
# Main purpose of writing it like this is to execute taking money from the buyer and giving
#   it to sellers as one transaction
def fundsBuyerToSeller(buyOrder: BuyOrder, sellOrders, buyPrice):
    time = datetime.now()
    if buyPrice <= 0:
        raise HTTPException(status_code=400, detail="Buy price must be greater than 0")

    if len(sellOrders) <= 0:
        raise HTTPException(status_code=400, detail="Missing sell orders")

    if not buyOrder:
        raise HTTPException(status_code=400, detail="Missing buy order")

    with sqlmodel.Session(engine) as session:

        statement = sqlmodel.select(Wallets).where(Wallets.user_id == buyOrder.user_id)
        buyerWallet = session.exec(statement).one_or_none()

        if buyerWallet.balance < buyPrice:
            raise HTTPException(status_code=400, detail="buyer lacks funds")

        # pay out the stocks
        buyerStockTx = payOutStocks(session, buyOrder, buyPrice)

        # subtracts from buyer's wallet balance
        buyerWallet.balance -= buyPrice
        session.add(buyerWallet)

        # creates wallet transaction for taking money from the buyer
        buyerWalletTx = addWalletTx(
            session, buyOrder, buyPrice, buyerStockTx.stock_tx_id, isDebit=True
        )

        # adds wallet tx id to stock stock_tx_id
        buyerStockTx = addWalletTxToStockTx(session, buyerStockTx.stock_tx_id, buyerWalletTx.wallet_tx_id)

        # TODO stock added to portfolio
        amountSoldTotal = 0

        for sellOrderTouple in sellOrders:
            sellOrder, sellQuantity = sellOrderTouple

            # calculates price using the price per stock and the *actual* amount sold
            sellPrice = sellOrder.price * sellQuantity

            statement = sqlmodel.select(Wallets).where(
                Wallets.user_id == sellOrder.user_id
            )
            sellerWallet = session.exec(statement).one_or_none()

            # adds money to sellers wallet
            sellerWallet.balance += sellPrice
            session.add(sellerWallet)

            # updates the sell order transaction to completed
            sellerStockTxId = sellOrder.stock_tx_id

            statement = sqlmodel.select(StockTransactions).where(
                StockTransactions.stock_tx_id == sellerStockTxId
            )
            incompleteTx = session.exec(statement).one_or_none()

            if not incompleteTx:
                raise HTTPException(
                    status_code=500, detail="Missing Sell Transaction to update"
                )

            incompleteTx.order_status = OrderStatus.COMPLETED

            session.add(incompleteTx)

            # creates wallet transaction for paying the seller
            sellerWalletTx = addWalletTx(
                session, sellOrder, sellPrice, sellerStockTxId, isDebit=False
            )

            sellerStockTx = addWalletTxToStockTx(session, sellerStockTxId, sellerWalletTx.wallet_tx_id)

            amountSoldTotal += sellPrice

        if not amountSoldTotal == buyPrice:
            raise HTTPException(status_code=400, detail="Buyer/Seller mismatch")

        session.commit()
        cache.set(f'{CacheName.WALLETS}:{buyOrder.user_id}',{"balance": buyerWallet.balance})
        cache.set(f'{CacheName.WALLETS}:{sellOrder.user_id}',{"balance": sellerWallet.balance})
        buyer_stock_tx_dict = {
            buyerStockTx.stock_tx_id: buyerStockTx.model_dump()
        }
        cache.update(f'{CacheName.STOCK_TX}:{buyerStockTx.user_id}', buyer_stock_tx_dict)
        seller_stock_tx_dict = {
            sellerStockTx.stock_tx_id: sellerStockTx.model_dump()
        }
        cache.update(f'{CacheName.STOCK_TX}:{sellerStockTx.user_id}', seller_stock_tx_dict)
        buyer_wallet_tx_dict = {
            buyerWalletTx.wallet_tx_id: buyerWalletTx.model_dump()
        }
        cache.update(f'{CacheName.WALLET_TX}:{buyerWalletTx.user_id}', buyer_wallet_tx_dict)
        seller_wallet_tx_dict = {
            sellerWalletTx.wallet_tx_id: sellerWalletTx.model_dump()
        }
        cache.update(f'{CacheName.WALLET_TX}:{sellerWalletTx.user_id}', seller_wallet_tx_dict)



def addWalletTx(session, order, orderValue, stockTxId, isDebit: bool) -> WalletTransactions:
    time = str(datetime.now())
    walletTx = WalletTransactions(
        user_id=order.user_id,
        stock_tx_id=stockTxId,
        is_debit=isDebit,
        amount=orderValue,
    )

    session.add(walletTx)
    session.flush()
    session.refresh(walletTx)
    return walletTx


def addStockTx(session, order, isBuy: bool, price: int, state: OrderStatus)-> StockTransactions:

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
    session.flush()
    session.refresh(stockTx)
    return stockTx


def gatherStocks(order, user_id, stock_id, stock_amount):
    with sqlmodel.Session(engine) as session:
        statement = sqlmodel.select(StockPortfolios).where(
            (StockPortfolios.user_id == user_id)
            & (StockPortfolios.stock_id == stock_id)
        )
        holding = session.exec(statement).one_or_none()

        if not holding or holding.quantity_owned < stock_amount:
            raise HTTPException(
                status_code=500, detail="You cannot sell stocks you don't own"
            )

        holding.quantity_owned -= stock_amount
        stockTx = addStockTx(
            session,
            order,
            isBuy=False,
            price=order.price,
            state=OrderStatus.IN_PROGRESS,
        )
        session.add(holding)

        session.commit()
        buy_order_dict = {
            stockTx.stock_tx_id: stockTx.model_dump()
        }
        cache.update(f'{CacheName.STOCK_TX}:{user_id}', buy_order_dict)
        return stockTx.stock_tx_id


def payOutStocks(session, buyOrder: BuyOrder, buyPrice)-> StockTransactions:

    if not buyOrder:
        raise HTTPException(status_code=400, detail="Missing buy order")

    statement = sqlmodel.select(StockPortfolios).where(
        (StockPortfolios.user_id == buyOrder.user_id)
        & (StockPortfolios.stock_id == buyOrder.stock_id)
    )
    buyerStockHolding = session.exec(statement).one_or_none()
    stock_name_query = sqlmodel.select(Stocks.stock_name).where(Stocks.stock_id == buyOrder.stock_id)
    stock_name = session.exec(stock_name_query).one()

    if not buyerStockHolding:
        newStockHolding = StockPortfolios(
            user_id=buyOrder.user_id,
            stock_id=buyOrder.stock_id,
            quantity_owned=buyOrder.quantity,
        )
        session.add(newStockHolding)
        # TODO: Is there some other thing we can do here to get the stock name? (needs to be sorted by stock_name)
        portfolio_dict = {
            newStockHolding.stock_id: {
                "stock_name": stock_name,
                **newStockHolding.model_dump()
            }
        }
        cache.update(f'{CacheName.STOCK_PORTFOLIO}:{buyOrder.user_id}', portfolio_dict)
    else:
        buyerStockHolding.quantity_owned += buyOrder.quantity
        session.add(buyerStockHolding)
        portfolio_dict = {
            buyerStockHolding.id: {
                "stock_name": stock_name,
                **buyerStockHolding.dict()
            }
        }
        cache.update(f'{CacheName.STOCK_PORTFOLIO}:{buyOrder.user_id}', portfolio_dict)

    stockTx = addStockTx(
        session, buyOrder, isBuy=True, price=buyPrice, state=OrderStatus.COMPLETED
    )


    return stockTx


def cancelTransaction(stockTxId):

    with sqlmodel.Session(engine) as session:

        # Set the transaction to cancelled
        statement = sqlmodel.select(StockTransactions).where(
            StockTransactions.stock_tx_id == stockTxId
        )
        transactionToBeCancelled = session.exec(statement).one_or_none()

        transactionToBeCancelled.order_status = OrderStatus.CANCELLED

        session.add(transactionToBeCancelled)

        # then refund the stocks to the users portfolio
        statement = sqlmodel.select(StockPortfolios).where(
            (StockPortfolios.user_id == transactionToBeCancelled.user_id)
            & (StockPortfolios.stock_id == transactionToBeCancelled.stock_id)
        )
        sellerPortfolio = session.exec(statement).one_or_none()

        sellerPortfolio.quantity_owned += transactionToBeCancelled.quantity

        session.add(sellerPortfolio)

        session.commit()
        cancelled_dict = {
            transactionToBeCancelled.stock_tx_id: transactionToBeCancelled.dict()
        }
        cache.update(f'{CacheName.STOCK_TX}:{transactionToBeCancelled.user_id}', cancelled_dict)
        # TODO: Do we need to update the stock portfolio here?


def getTransaction(stockTxId):
    with sqlmodel.Session(engine) as session:

        statement = sqlmodel.select(StockTransactions).where(
            StockTransactions.stock_tx_id == stockTxId
        )
        result = session.exec(statement).one_or_none()

        return result


def createChildTransaction(order, parentStockTxId):
    with sqlmodel.Session(engine) as session:

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
        session.flush()
        session.refresh(childTx)
        session.commit()
        return childTx.stock_tx_id


def setToPartiallyComplete(stockTxId, quantity):
    with sqlmodel.Session(engine) as session:

        statement = sqlmodel.select(StockTransactions).where(
            StockTransactions.stock_tx_id == stockTxId
        )
        transactionToChange = session.exec(statement).one_or_none()

        transactionToChange.order_status = OrderStatus.PARTIALLY_COMPLETE
        transactionToChange.quantity = quantity

        session.add(transactionToChange)
        session.commit()
        return SuccessResponse()


def addWalletTxToStockTx(session, stockTxId, walletTxId) -> StockTransactions:

    statement = sqlmodel.select(StockTransactions).where(
        StockTransactions.stock_tx_id == stockTxId
    )
    stockTx = session.exec(statement).one_or_none()

    stockTx.wallet_tx_id = walletTxId

    session.add(stockTx)
    return stockTx