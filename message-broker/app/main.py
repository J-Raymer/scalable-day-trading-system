from contextlib import asynccontextmanager
from fastapi import FastAPI
from .core.broker import *
from .routers.me_router import router as me_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker_setup()
    yield
    await broker_shutdown()


app = FastAPI(root_path="/message-broker", lifespan=lifespan)
app.include_router(me_router)
