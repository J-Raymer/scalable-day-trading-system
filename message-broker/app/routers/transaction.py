from schemas.common import ErrorResponse, SuccessResponse, RabbitError
from schemas.setup import Stock, StockSetup
from schemas.engine import StockOrder, CancelOrder
from schemas.transaction import AddMoneyRequest
from ..core.broker import *
from fastapi import APIRouter, Header, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get(
    "/getWalletBalance",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def get_wallet_balance():
    pass


@router.get(
    "/getWalletTransactions",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
    },
)
async def get_wallet_transactions(
    x_user_data: str = Header(None), session: AsyncSession = Depends(get_session)
):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split("|")
    pass


@router.post(
    "/addMoneyToWallet",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def add_money_to_wallet(
    req: AddMoneyRequest,
    x_user_data: str = Header(None),
    session: AsyncSession = Depends(get_session),
):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split("|")
    pass


@router.get(
    "/getStockPortfolio",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def get_stock_portfolio(
    x_user_data: str = Header(None), session: AsyncSession = Depends(get_session)
):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split("|")
    pass


@router.get(
    "/getStockTransactions",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def get_stock_transactions(
    x_user_data: str = Header(None), session: AsyncSession = Depends(get_session)
):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split("|")
    pass


@router.post(
    "/createStock",
    status_code=201,
    responses={
        201: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def create_stock(
    stock: Stock,
    x_user_data: str = Header(None),
    session: AsyncSession = Depends(get_session),
):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split("|")
    pass


@router.post(
    "/addStockToUser",
    status_code=201,
    responses={
        201: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def add_stock_to_user(
    new_stock: StockSetup,
    x_user_data: str = Header(None),
    session: AsyncSession = Depends(get_session),
):
    if not x_user_data:
        raise HTTPException(status_code=400, detail="User data is missing in headers")
    username, user_id = x_user_data.split("|")
    pass
