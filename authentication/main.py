import bcrypt
import dotenv
import jwt
import os
import sqlmodel
from sqlmodel import func
from datetime import datetime, timedelta
from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from database import Users
from schemas.common import *

# dotenv.load_dotenv()
# USERNAME = os.getenv("USERNAME")
# PASSWORD = os.getenv("PASSWORD")
# HOST = os.getenv("HOST")
# PORT = os.getenv("POSTGRES_PORT")
# DB_NAME = os.getenv("DB_NAME")
JWT_SECRET =  'secret123456'
# url = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
url = f"postgresql://admin:isolated-dean-primal-starving@localhost:5433/day_trader"

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

def generate_token(user: Users):
    expiration = datetime.now() + timedelta(days=1)
    token = jwt.encode({ "username": user.user_name,
                         "name": user.name,
                         "id": str(user.id),
                         "exp": expiration},
                       JWT_SECRET,
                       algorithm="HS256")
    return token


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
async def register(user: RegisterRequest):
    if not (user.user_name and user.password and user.name):
        raise HTTPException(status_code=400, detail="Username, name and password required")

    with sqlmodel.Session(engine) as session:
        query = sqlmodel.select(Users).where(func.lower(Users.user_name) == func.lower(user.user_name))
        existing_user = session.exec(query).one_or_none()

        if existing_user:
            raise HTTPException(status_code=409, detail="Username already exists")

        salt = bcrypt.gensalt()
        new_user = Users(
            user_name=user.user_name,
            password=bcrypt.hashpw(user.password.encode('utf-8'), salt).decode('utf-8'),
            name=user.name,
            salt=salt.decode('utf-8'))
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        token = generate_token(new_user)
        return SuccessResponse(data={"token": token})

@app.post("/login",
          responses={
              200: {"model": LoginResponse},
              400: {"model": ErrorResponse},
              404: {"model": ErrorResponse}
          })
async def login(user: LoginRequest, res: Response, ):
    if not (user.user_name and user.password):
        raise HTTPException(status_code=400, detail="Username and password required")

    with sqlmodel.Session(engine) as session:
        query = sqlmodel.select(Users).where(Users.user_name == user.user_name)
        result = session.exec(query).one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="User not found")

        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), result.salt.encode('utf-8')).decode('utf-8')
        if hashed_password != result.password:
            res.status_code = 401
            raise HTTPException(status_code=401, detail="Unauthorized")
    token = generate_token(result)
    return SuccessResponse(data={ "token": token })
