from schemas.common import SuccessResponse
from schemas.engine import BuyOrder
import dotenv
import os
import sqlmodel
from fastapi import HTTPException
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

engine = sqlmodel.create_engine(url)


def getStockData():
    with sqlmodel.Session(engine) as session:
        query = sqlmodel.select(Stocks)
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
        
        buyerStockTxId = payOutStocks(session, buyOrder, buyPrice)

        statement = sqlmodel.select(Wallets).where(Wallets.user_id == buyOrder.user_id)
        buyerWallet = session.exec(statement).one_or_none()

        if buyerWallet.balance < buyPrice:
            raise HTTPException(status_code=400, detail="buyer lacks funds")

        # subtracts from buyer's wallet balance
        buyerWallet.balance -= buyPrice
        session.add(buyerWallet)

        # creates wallet transaction for taking money from the buyer
        addWalletTx(session, buyOrder, buyPrice, buyerStockTxId, isDebit=False)

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
                raise HTTPException(status_code=500, detail="Missing Sell Transaction to update")

            incompleteTx.order_status = OrderStatus.COMPLETED

            session.add(incompleteTx)
 
            # creates wallet transaction for paying the seller
            addWalletTx(session, sellOrder, sellPrice, sellerStockTxId, isDebit=True)

            amountSoldTotal += sellPrice

        if not amountSoldTotal == buyPrice:
            raise HTTPException(status_code=400, detail="Buyer/Seller mismatch")

        session.commit()


def addWalletTx(session, order, orderValue, stockTxId, isDebit: bool):
    time = datetime.now()
    walletTx = WalletTransactions(
        user_id=order.user_id,
        stock_tx_id=stockTxId,
        is_debit=isDebit,
        amount=orderValue,
        timestamp=time,
    )

    session.add(walletTx)


def addStockTx(session, order, isBuy: bool, price: int, state: OrderStatus):
    time = datetime.now()

    stockTx = StockTransactions(
        stock_id=order.stock_id,
        order_status=state,
        is_buy=isBuy,
        order_type=order.order_type,
        quantity=order.quantity,
        parent_tx_id=None,
        time_stamp=time,
        user_id=order.user_id,
    )

    # we should just put this ^^^ but for clarity im just gonna leave it like this for now
    if isBuy:
        stockTx.stock_price = price  # buy orders will pass in the total buy price from the combined orders
    else:
        stockTx.stock_price = (
            price  # sell order will pass in their individual sell price
        )

    session.add(stockTx)
    session.flush()
    session.refresh(stockTx)

    return stockTx.stock_tx_id


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
        stockTXID = addStockTx(
            session,
            order,
            isBuy=False,
            price=order.price,
            state=OrderStatus.IN_PROGRESS,
        )
        session.add(holding)

        session.commit()

        return stockTXID


def payOutStocks(session, buyOrder: BuyOrder, buyPrice):

    if not buyOrder:
        raise HTTPException(status_code=400, detail="Missing buy order")

    statement = sqlmodel.select(StockPortfolios).where(
                (StockPortfolios.user_id == buyOrder.user_id)
                &
                (StockPortfolios.stock_id == buyOrder.stock_id)
            )
    buyerStockHolding = session.exec(statement).one_or_none()

    if not buyerStockHolding:
        newStockHolding = StockPortfolios(
            user_id = buyOrder.user_id,
            stock_id = buyOrder.stock_id,
            quantity_owned = buyOrder.quantity
        )
        session.add(newStockHolding)
    else:
        buyerStockHolding.quantity_owned += buyOrder.quantity
        session.add(buyerStockHolding)

    stockTxId = addStockTx(session, buyOrder, isBuy=True, price=buyPrice, state=OrderStatus.COMPLETED)

    return stockTxId


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
            &
            (StockPortfolios.stock_id == transactionToBeCancelled.stock_id)
        )
        sellerPortfolio = session.exec(statement).one_or_none()

        sellerPortfolio.quantity_owned += transactionToBeCancelled.quantity

        session.add(sellerPortfolio)

        session.commit()


def getTransaction(stockTxId):
    with sqlmodel.Session(engine) as session:

        statement = sqlmodel.select(StockTransactions).where(
            StockTransactions.stock_tx_id == stockTxId
        )
        result = session.exec(statement).one_or_none()

        return result
