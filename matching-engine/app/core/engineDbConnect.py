from schemas.common import SuccessResponse
from schemas.engine import BuyOrder
import sqlmodel
from sqlmodel import Session, select
from .db import get_db_session
from fastapi import HTTPException
from database import Stocks, Wallets, WalletTransactions, StockTransactions, StockPortfolios, OrderStatus
from datetime import datetime

def getStockData():
    with get_db_session() as session:
        query = select(Stocks)
        result = session.exec(query)
        return result.all()

def fundsBuyerToSeller(buyOrder: BuyOrder, sellOrders, buyPrice):
    with get_db_session() as session:
        if buyPrice <= 0:
            raise HTTPException(status_code=400, detail="Buy price must be greater than 0")

        if len(sellOrders) <= 0:
            raise HTTPException(status_code=400, detail="Missing sell orders")

        if not buyOrder:
            raise HTTPException(status_code=400, detail="Missing buy order")

        buyerStockTxId = payOutStocks(session, buyOrder, buyPrice)

        statement = select(Wallets).where(Wallets.user_id == buyOrder.user_id)
        buyerWallet = session.exec(statement).one_or_none()

        if buyerWallet.balance < buyPrice:
            raise HTTPException(status_code=400, detail="Buyer lacks funds")

        buyerWallet.balance -= buyPrice
        session.add(buyerWallet)

        addWalletTx(session, buyOrder, buyPrice, buyerStockTxId, isDebit=False)

        amountSoldTotal = 0

        for sellOrderTouple in sellOrders:
            sellOrder, sellQuantity = sellOrderTouple
            sellPrice = sellOrder.price * sellQuantity

            statement = select(Wallets).where(Wallets.user_id == sellOrder.user_id)
            sellerWallet = session.exec(statement).one_or_none()

            sellerWallet.balance += sellPrice
            session.add(sellerWallet)

            stockTxId = addStockTx(session, sellOrder, isBuy=False, price=sellOrder.price, state=OrderStatus.COMPLETED)
            addWalletTx(session, sellOrder, sellPrice, stockTxId, isDebit=True)

            amountSoldTotal += sellPrice

        if not amountSoldTotal == buyPrice:
            raise HTTPException(status_code=400, detail="Buyer/Seller mismatch")

        session.commit()

def addWalletTx(session, order, orderValue, stockTxId, isDebit: bool):
    time = datetime.now()
    walletTx = WalletTransactions(
        user_id=order.user_id,
        stock_tx_id=stockTxId,
        is_debit=isDebit,
        amount=orderValue,
        timestamp=time,
    )
    session.add(walletTx)

def addStockTx(session, order, isBuy: bool, price: int, state: OrderStatus):
    time = datetime.now()
    stockTx = StockTransactions(
        stock_id=order.stock_id,
        order_status=state,
        is_buy=isBuy,
        order_type=order.order_type,
        quantity=order.quantity,
        parent_tx_id=None,
        time_stamp=time,
        user_id=order.user_id,
    )

    stockTx.stock_price = price

    session.add(stockTx)
    session.flush()
    session.refresh(stockTx)

    return stockTx.stock_tx_id

def gatherStocks(order, user_id, stock_id, stock_amount):
    with get_db_session() as session:
        statement = select(StockPortfolios).where(
                    (StockPortfolios.user_id == user_id) & (StockPortfolios.stock_id == stock_id)
                )
        holding = session.exec(statement).one_or_none()

        if not holding or holding.quantity_owned < stock_amount:
            raise HTTPException(status_code=500, detail="You cannot sell stocks you don't own")

        holding.quantity_owned -= stock_amount
        stockTXID = addStockTx(session, order, isBuy=False, price=order.price, state=OrderStatus.IN_PROGRESS)
        session.add(holding)
        
        session.commit()

        return stockTXID

def payOutStocks(session, buyOrder: BuyOrder, buyPrice):
    if not buyOrder:
        raise HTTPException(status_code=400, detail="Missing buy order")

    statement = select(StockPortfolios).where(
                (StockPortfolios.user_id == buyOrder.user_id) & (StockPortfolios.stock_id == buyOrder.stock_id)
            )
    buyerStockHolding = session.exec(statement).one_or_none()

    if not buyerStockHolding:
        newStockHolding = StockPortfolios(
            user_id=buyOrder.user_id,
            stock_id=buyOrder.stock_id,
            quantity_owned=buyOrder.quantity
        )
        session.add(newStockHolding)
    else:
        buyerStockHolding.quantity_owned += buyOrder.quantity
        session.add(buyerStockHolding)

    stockTxId = addStockTx(session, buyOrder, isBuy=True, price=buyPrice, state=OrderStatus.COMPLETED)

    return stockTxId