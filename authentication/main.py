import bcrypt
import dotenv
import jwt
import os
import sqlmodel
from datetime import datetime, timedelta
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from database import Users
from schemas import *

dotenv.load_dotenv()
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("POSTGRES_PORT")
db_name = os.getenv("DB_NAME")
secret = os.getenv("JWT_SECRET")
url = f"postgresql://{username}:{password}@{HOST}:{PORT}/{db_name}"

engine = sqlmodel.create_engine(url)
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allows front end requests locally
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return RedirectResponse(url="/docs", status_code=302)

@app.post("/register",
          status_code=201,
          responses={
              201: {"model": SuccessResponse},
              400: {"model": ErrorResponse},
              409: {"model": ErrorResponse}
          })
async def register(user: User, res: Response):
    if not (user.username and user.password):
        res.status_code = 400
        return { "message": "Bad Request" }

    with sqlmodel.Session(engine) as session:
        query = sqlmodel.select(Users).where(Users.username == user.username)
        existing_user = session.exec(query).one_or_none()

        if existing_user:
            res.status_code = 409
            return {"message": "Username already exists"}

        salt = bcrypt.gensalt()
        new_user = Users(
            username=user.username,
            password=bcrypt.hashpw(user.password.encode('utf-8'), salt).decode('utf-8'),
            salt=salt.decode('utf-8'))
        session.add(new_user)
        session.commit()
        res.status_code = 201
        return {"success": True, "data": None}

@app.post("/login",
          responses={
              200: {"model": LoginResponse},
              400: {"model": ErrorResponse},
              404: {"model": ErrorResponse}
          })
async def login(user: User, res: Response,):
    if not (user.username and user.password):
        res.status_code = 400
        return {"message": "Username and password required"}

    with sqlmodel.Session(engine) as session:
        query = sqlmodel.select(Users).where(Users.username == user.username)
        result = session.exec(query).one_or_none()
        if not result:
            res.status_code = 404
            return { "message": "User not found" }

        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), result.salt.encode('utf-8')).decode('utf-8')
        if hashed_password != result.password:
            res.status_code = 401
            return {"message": "Unauthorized"}

    expiration = datetime.now() + timedelta(days=1)
    token = jwt.encode({ "username": user.username, "id": str(result.id), "exp": expiration }, secret, algorithm="HS256")
    return {"success": "true", "data": { "token": token }}
