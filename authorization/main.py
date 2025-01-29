import jwt
import sqlmodel
import dotenv
import os
from fastapi import FastAPI, Header
from pydantic import BaseModel
from typing import Annotated, Union
from sqlmodel import SQLModel

dotenv.load_dotenv()
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
PORT = os.getenv("PORT")
db_name = os.getenv("DB_NAME")


class User(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    token: str


secret = os.getenv("JWT_SECRET")
token = jwt.encode({"name": "admin", "admin" : True}, secret, algorithm="HS256")
url = f"postgresql://{username}:{password}@{host}:{PORT}/{db_name}"
engine = sqlmodel.create_engine(url)
app = FastAPI()


@app.get("/")
async def root():
    return {"message" : "hello world"}


@app.post("/login")
async def login(user: User):
    with sqlmodel.Session(engine) as session:
        query = session.query(User).where(User.username == user.username)
        result = session.exec(query)




