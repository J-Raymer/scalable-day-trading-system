# run locally on uvicorn using "uvicorn matching-engine.app.main:app --reload"


import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID

# import os
# import dotenv
from schemas.common import SuccessResponse, ErrorResponse, User
from schemas.engine import StockOrder
from .core import receiveOrder, cancelOrder, getUserFromId, getAllUsers

"""
dotenv.load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

async def verify_token(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"require": ["exp", "id", "username"]})
        return User(username=decoded_token["username"], id=decoded_token["id"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired Token")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=403, detail="Unauthorized")
    except jwt.MissingRequiredClaimError:
        raise HTTPException(status_code=400, detail="Missing required claim")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Unauthorized")
"""

app = FastAPI(root_path="/engine")


@app.get("/")
async def home():
    return RedirectResponse(url="/engine/docs", status_code=302)


# engine calls
@app.post(
    "/placeStockOrder",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def placeStockOrder(
    order: StockOrder, user: User
):  # REMOVE AFTER TESTING= Depends(verify_token)):
    return receiveOrder(order, user)


# TEST CALL
@app.post("/getUserFromId")
async def getUser(data):
    return getUserFromId(data.id)


# TEST CALL
@app.get("/getUsers")
async def getUsers():
    return getAllUsers()


@app.post(
    "/cancelStockTransaction",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def cancelStockTransaction(stockID: str):
    return cancelOrder()
