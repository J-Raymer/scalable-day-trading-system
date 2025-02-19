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

time = datetime.now()


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

    with sqlmodel.Session(engine) as session:

        statement = sqlmodel.select(Wallets).where(Wallets.user_id == buyOrder.user_id)
        buyerWallet = session.exec(statement).one_or_none()

        if buyerWallet.balance < buyPrice:
            raise HTTPException(status_code=400, detail="buyer lacks funds")
        
        # NOTE we have to track these, for matching up with stock transactions
        walletTransactions = []

        # subtracts from buyer's wallet balance
        buyerWallet.balance -= buyPrice
        session.add(buyerWallet)

        transactionId = addWalletTx(session, buyOrder, buyPrice, isDebit=False)
        walletTransactions.append((buyOrder, transaction_id))

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

            transactionID = addWalletTx(session, sellOrder, sellPrice, isDebit=True)

            walletTransactions.append((sellOrder, transactionID))

            amountSoldTotal += sellPrice

        if not amountSoldTotal == buyPrice:
            raise HTTPException(status_code=400, detail="Buyer/Seller mismatch")

        session.commit()

    return walletTransactions


def addWalletTx(session, order, orderValue, isDebit: bool):
    walletTx = WalletTransactions(
        user_id=order.user_id,
        is_debit=isDebit,
        amount=orderValue,
        timestamp=time,
    )

    print(walletTx.wallet_tx_id)

    session.add(walletTx)

    return walletTx.wallet_tx_id


# TODO add transaction to database
def addStockTx(session, order, walletTxId):
    session.add(
        StockTransactions(
            stock_id=order.stock_id,
            wallet_tx_id=walletTxId,
            order_status=OrderStatus.COMPLETED,
            is_buy=order.is_buy,
            order_type=order.order_type,
            stock_price=order.price,  # dont know if this should be price per stock or overall buy price. Price per stock could involve rounding on int division.
            quantity=order.quantity,
            parent_tx_id=None,
            time_stamp=time,
            user_id=order.user_id,
        )
    )


def checkStockPortfolio(user_id, stock_id, stock_amount):
    with sqlmodel.Session(engine) as session:
        statement = sqlmodel.select(StockPortfolios).where(
                    (StockPortfolios.user_id == user_id)
                    &
                    (StockPortfolios.stock_id == stock_id)
                )
        holding = session.exec(statement).one_or_none()

        if not holding or holding.quantity_owned < stock_amount:
            return False
        else:
            return True


def transferStocks(buyOrder: BuyOrder, sellOrders, order_wallet_transactions): 
    if len(sellOrders) <= 0:
        raise HTTPException(status_code=400, detail="Missing sell orders")

    if not buyOrder:
        raise HTTPException(status_code=400, detail="Missing buy order")

    with sqlmodel.Session(engine) as session:
        
        for sellOrderTuple in sellOrders:
            sellOrder, sellQuantity = sellOrderTuple

            statement = sqlmodel.select(StockPortfolios).where(
                        (StockPortfolios.user_id == sellOrder.user_id)
                        &
                        (StockPortfolios.stock_id == sellOrder.stock_id)
                    )
            sellerStockHolding = session.exec(statement).one_or_none()
            sellerStockHolding.quantity_owned -= sellQuantity

            addStockTX(session, sellOrder, wallet_transaction)
        






