import bcrypt
import dotenv
import jwt
import os
import sqlmodel
from datetime import datetime, timedelta
from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from database import Users


dotenv.load_dotenv()
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
PORT = os.getenv("PORT")
db_name = os.getenv("DB_NAME")

secret = os.getenv("JWT_SECRET")
url = f"postgresql://{username}:{password}@{host}:{PORT}/{db_name}"
engine = sqlmodel.create_engine(url)
app = FastAPI()


class User(BaseModel):
    username: str | None = None
    password: str | None = None

@app.get("/")
async def home():
    return RedirectResponse(url="/docs", status_code=302)

@app.post("/register")
async def register(user: User, res: Response):
    if not (user.username and user.password):
        res.status_code = 400
        return { "message": "Bad Request" }

    with sqlmodel.Session(engine) as session:
        query = sqlmodel.select(Users).where(Users.username == user.username)
        existing_user = session.exec(query).one_or_none()

        if existing_user:
            res.status_code = 409
            return { "message": "Username already exists" }

        salt = bcrypt.gensalt()
        new_user = Users(
            username=user.username,
            password=bcrypt.hashpw(user.password.encode('utf-8'), salt).decode('utf-8'),
            salt=salt.decode('utf-8'))
        session.add(new_user)
        session.commit()
        res.status_code = 201
        return { "success": "true", "data": None }


@app.post("/login")
async def login(user: User, res: Response):
    if not (user.username and user.password):
        res.status_code = 400
        return { "message": "Bad Request" }

    with sqlmodel.Session(engine) as session:
        query = sqlmodel.select(Users).where(Users.username == user.username)
        result = session.exec(query).one_or_none()
        if not result:
            res.status_code = 404
            return { "message": "User not found" }

        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), result.salt.encode('utf-8')).decode('utf-8')
        if hashed_password != result.password:
            res.status_code = 401
            return { "message": "Unauthorized" }

    expiration = datetime.now() + timedelta(days=1)
    token = jwt.encode({ "username": user.username, "id": result.id, "exp": expiration }, secret, algorithm="HS256")
    return { "success": "true", "data": { "token": token } }
