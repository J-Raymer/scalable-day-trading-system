from schemas.common import ErrorResponse, SuccessResponse
from schemas.setup import Stock, StockSetup
from schemas.transaction import AddMoneyRequest
from ..core.broker import *
from fastapi import APIRouter, Header

router = APIRouter()
queue_name = "transaction"


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
async def get_wallet_balance(x_user_data: str = Header(None)):
    return await sendRequest(
        x_user_data=x_user_data, body="", content="GET_WALLET", q_name=queue_name
    )


@router.get(
    "/getWalletTransactions",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
    },
)
async def get_wallet_transactions(x_user_data: str = Header(None)):
    return await sendRequest(
        x_user_data=x_user_data, body="", content="GET_WALLET_TX", q_name=queue_name
    )


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
):
    print("call recieved", flush=True)
    return await sendRequest(
        x_user_data=x_user_data,
        body=req.model_dump_json(),
        content="ADD_MONEY",
        q_name=queue_name,
    )


@router.get(
    "/getStockPortfolio",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def get_stock_portfolio(x_user_data: str = Header(None)):
    return await sendRequest(
        x_user_data=x_user_data,
        body="",
        content="GET_STOCK_PORTFOLIO",
        q_name=queue_name,
    )


@router.get(
    "/getStockTransactions",
    responses={
        200: {"model": SuccessResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def get_stock_transactions(x_user_data: str = Header(None)):
    return await sendRequest(
        x_user_data=x_user_data,
        body="",
        content="GET_STOCK_TX",
        q_name=queue_name,
    )


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
):
    return await sendRequest(
        x_user_data=x_user_data,
        body=stock.model_dump_json(),
        content="CREATE_STOCK",
        q_name=queue_name,
    )


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
):
    return await sendRequest(
        x_user_data=x_user_data,
        body=new_stock.model_dump_json(),
        content="ADD_STOCK",
        q_name=queue_name,
    )


@router.get("/getStockPrices")
async def getStockPrice():
    return await sendRequest(
        x_user_data="NO_AUTH",
        body="",
        content="GET_PRICES",
        q_name="matching-engine",
    )
