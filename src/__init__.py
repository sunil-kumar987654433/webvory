from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.account import models as account_models
from src.account.routs import account_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("start server...")
    yield
    print("end server...")

version='v1'

app = FastAPI(
    version=version,
    title="Web Overy",
    description="web overy api service",
    lifespan=lifespan
)
app.include_router(
    router=account_router,
    prefix="/account",
    tags=['account']
)