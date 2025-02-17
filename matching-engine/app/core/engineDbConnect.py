from typing import override
from schemas.common import User, SuccessResponse
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
