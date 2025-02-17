from schemas.common import User, SuccessResponse
from schemas.engine import SellOrder, BuyOrder
import dotenv
import os
import sqlmodel
from fastapi import FastAPI, Response, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from database import Users, Wallets


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

    with sqlmodel.Session(engine) as session:

        statement = sqlmodel.select(Wallets).where(Wallets.user_id == buyOrder.user_id)
        buyerWallet = session.exec(statement).one_or_none()

        if buyerWallet.balance < buyPrice:
            raise HTTPException(status_code=400, detail="buyer lacks funds")

        buyerWallet.balance -= buyPrice
        session.add(buyerWallet)

        amountSoldTotal = 0

        for sellOrderTouple in sellOrders:
            sellOrder, sellQuantity = sellOrderTouple

            statement = sqlmodel.select(Wallets).where(
                Wallets.user_id == sellOrder.user_id
            )
            sellerWallet = session.exec(statement).one_or_none()

            sellerWallet.balance += sellOrder.price * sellQuantity
            session.add(sellerWallet)

            amountSoldTotal += sellOrder.price * sellQuantity

        if not amountSoldTotal == buyPrice:
            raise HTTPException(status_code=400, detail="Buyer/Seller mismatch")

        session.commit()

    return SuccessResponse()


def addToWallet(userId: str, amount: int):
    if not userId:
        raise HTTPException(status_code=400, detail="User id error")

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    with sqlmodel.Session(engine) as session:
        statement = sqlmodel.select(Wallets).where(Wallets.user_id == userId)
        wallet = session.exec(statement).one_or_none()
        wallet.balance += amount
        session.add(wallet)
        session.commit()

    return SuccessResponse()


# TODO add transaction to database
def addSellTransaction():
    pass


def removeFromWallet(userId: str, amount: int):
    if not userId:
        raise HTTPException(status_code=400, detail="User id error")

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    with sqlmodel.Session(engine) as session:
        statement = sqlmodel.select(Wallets).where(Wallets.user_id == userId)
        wallet = session.exec(statement).one_or_none()

        if wallet.balance < amount:
            raise HTTPException(status_code=400, detail="Wallet lacks funds")

        wallet.balance -= amount
        session.add(wallet)
        session.commit()

    return SuccessResponse()
