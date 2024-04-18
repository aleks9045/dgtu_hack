from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import sessionmaker

from config import POSTGRES_USER, PORT, POSTGRES_PASSWORD, HOST, POSTGRES_DB


class DatabaseData:
    def __init__(self, db_url: str):
        self.__DATABASE_URL = db_url
        self.__Base: DeclarativeMeta = declarative_base()

        self.__engine = create_async_engine(self.__DATABASE_URL)
        self.__async_session = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False,
                                          autocommit=False)

    @property
    def base(self):
        return self.__Base

    @property
    def engine(self):
        return self.__engine

    @property
    def async_session(self):
        return self.__async_session


class Session(DatabaseData):
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_session() as s:
            yield s


db_session = Session(f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{HOST}:{PORT}/{POSTGRES_DB}")
