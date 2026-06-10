from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from src.config import Config
from src.db.db import Base
from typing import Annotated, AsyncGenerator

engine = create_async_engine(
    url=Config.DATABASE_URL,
    # echo=True
    )


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async_Session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False 
)

async def get_session():
    async with async_Session() as session:
        yield session