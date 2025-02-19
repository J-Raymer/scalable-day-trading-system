from schemas.common import User, SuccessResponse
from schemas.engine import SellOrder, BuyOrder
import dotenv
import os
import sqlmodel
from fastapi import FastAPI, Response, Depends, HTTPException
from database import Users, Wallets, WalletTransactions, StockTransactions, OrderStatus
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
app = FastAPI(root_path="/engine")


def getUserFromId(userId: str):
    with sqlmodel.Session(engine) as session:
        query = sqlmodel.select(Users).where(Users.id == userId)
        result = session.exec(query).one_or_none()

        if result:
            return result


# takes buy order and list of sell orders
# connects to database and checks if buyer has funds
# takes funds from buyer and distributes to seller(s)
#
# Main purpose of writing it like this is to execute taking money from the buyer and giving
#   it to sellers as one transaction
def fundsBuyerToSeller(buyOrder: BuyOrder, sellOrders, buyPrice):
    if buyPrice <= 0:
        raise HTTPException(status_code=400, detail="Buy price must be greater than 0")

    if len(sellOrders) <= 0:
        raise HTTPException(status_code=400, detail="Missing sell orders")

    if not buyOrder:
        raise HTTPException(status_code=400, detail="Missing buy order")

    time = datetime.now()

    with sqlmodel.Session(engine) as session:

        statement = sqlmodel.select(Wallets).where(Wallets.user_id == buyOrder.user_id)
        buyerWallet = session.exec(statement).one_or_none()

        if buyerWallet.balance < buyPrice:
            raise HTTPException(status_code=400, detail="buyer lacks funds")

        # subtracts from buyer's wallet balance
        buyerWallet.balance -= buyPrice
        session.add(buyerWallet)

        # creates stock transaction
        stockTxId = addStockTx(session, buyOrder, False)

        # creates wallet transaction
        addWalletTx(session, buyOrder, buyPrice, stockTxId, isDebit=False)

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

            # creates stock transaction
            stockTxId = addStockTx(session, sellOrder, False)

            # creates wallet transaction
            addWalletTx(session, sellOrder, sellPrice, stockTxId, isDebit=True)

            # TODO amount sold for partial buys needs to be added to transaction

            amountSoldTotal += sellPrice

        if not amountSoldTotal == buyPrice:
            raise HTTPException(status_code=400, detail="Buyer/Seller mismatch")

        session.commit()

    return SuccessResponse()


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

    return walletTx.wallet_tx_id


# TODO add transaction to database
def addStockTx(session, order, isBuy: bool):
    time = datetime.now()

    stockTx = StockTransactions(
        stock_id=order.stock_id,
        order_status=OrderStatus.COMPLETED,
        is_buy=isBuy,
        order_type=order.order_type,
        stock_price=order.price,  # dont know if this should be price per stock or overall buy price. Price per stock could involve rounding on int division.
        quantity=order.quantity,
        parent_tx_id=None,
        time_stamp=time,
        user_id=order.user_id,
    )

    session.add(stockTx)
    session.flush()
    session.refresh(stockTx)

    return stockTx.stock_tx_id
