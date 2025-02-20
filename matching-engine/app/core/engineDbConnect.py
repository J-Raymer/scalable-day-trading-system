from schemas.common import User, SuccessResponse
from schemas.engine import SellOrder, BuyOrder
import dotenv
import os
import sqlmodel
from fastapi import FastAPI, Response, Depends, HTTPException
from database import Users, Wallets, WalletTransactions, StockTransactions, StockPortfolios, OrderStatus
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
        
        # subtracts from buyer's wallet balance
        buyerWallet.balance -= buyPrice
        session.add(buyerWallet)

        # creates stock transaction for the buy order
        stockTxId = addStockTx(session, buyOrder, isBuy=True)

        # creates wallet transaction for taking money from the buyer
        addWalletTx(session, buyOrder, buyPrice, stockTxId, isDebit=False)

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

            # creates stock transaction for the sellOrder
            # TODO integrate this so it updates pending sell order to COMPLETED
            stockTxId = addStockTx(session, sellOrder, isBuy=False, price=sellOrder.price, state=OrderStatus.COMPLETED)

            # creates wallet transaction for paying the seller
            addWalletTx(session, sellOrder, sellPrice, stockTxId, isDebit=True)

            amountSoldTotal += sellPrice

        if not amountSoldTotal == buyPrice:
            raise HTTPException(status_code=400, detail="Buyer/Seller mismatch")

        session.commit()

    return walletTransactions


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

    if isBuy:
        stockTx.stock_price = price
        # dont know if this should be price per stock or overall buy price or 0. Price per stock could involve rounding on int division.
    else:
        stockTx.stock_price = price

    session.add(stockTx)
    session.flush()
    session.refresh(stockTx)

    return stockTx.stock_tx_id


def gatherStocks(order, user_id, stock_id, stock_amount):
    with sqlmodel.Session(engine) as session:
        statement = sqlmodel.select(StockPortfolios).where(
                    (StockPortfolios.user_id == user_id)
                    &
                    (StockPortfolios.stock_id == stock_id)
                )
        holding = session.exec(statement).one_or_none()

        if not holding or holding.quantity_owned < stock_amount:
            raise HTTPException(status_code=500, detail="You cannot sell stocks you don't own")

        holding.quantity_owned -= stock_amount
        stockTXID = addStockTx(session, order, isBuy=False, price=order.price, state=OrderStatus.IN_PROGRESS) 
        session.add(holding)
        
        session.commit()

        return stockTXID


def payOutStocks(buyOrder: BuyOrder, buyPrice):

    if not buyOrder:
        raise HTTPException(status_code=400, detail="Missing buy order")

    with sqlmodel.Session(engine) as session:

        statement = sqlmodel.select(StockPortfolios).where(
                    (StockPortfolios.user_id == buyOrder.user_id)
                    &
                    (StockPortfolios.stock_id == buyOrder.stock_id)
                )
        buyerStockHolding = session.exec(statement).one_or_none()
        buyerStockHolding.quantity_owned += buyOrder.quantity

        stockTXID = addStockTx(session, buyOrder, isBuy=True, price=buyPrice, state=OrderStatus.COMPLETED)
        session.add(buyerStockHolding)
    
        session.commit()
