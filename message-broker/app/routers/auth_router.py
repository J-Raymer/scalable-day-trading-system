from schemas.common import ErrorResponse, SuccessResponse
from schemas.setup import Stock, StockSetup
from schemas.transaction import AddMoneyRequest
from ..core.broker import *
from fastapi import APIRouter, Header

router = APIRouter()
queue_name = "auth"

# Leaving this for later
