from schemas.common import User
import dotenv
import os
import sqlmodel
from fastapi import FastAPI, Response, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from database import Users


dotenv.load_dotenv()
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


def getUserFromId(userId):
    with sqlmodel.Session(engine) as session:
        query = sqlmodel.select(Users).where(Users.user_id == userId)
        result = session.exec(query).one_or_none()

        if result:
            return result

    return User(username="", id=-1)


def getAllUsers():
    with sqlmodel.Session(engine) as session:
        query = sqlmodel.select(Users)
        result = session.exec(query)

        if result:
            return query
