from contextlib import asynccontextmanager
from fastapi import FastAPI
from .core.broker import *
from .routers.me_router import router as me_router
from .routers.ts_router import router as ts_router
from .routers.auth_router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker_setup()
    yield
    await broker_shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(router=me_router, prefix="/engine")
app.include_router(router=ts_router, prefix="/transaction")
app.include_router(router=auth_router, prefix="/authentication")
