from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager
from os import environ

Base = declarative_base()

class PsqlDbContext:

    def __init__(self, vault_service):
        super(PsqlDbContext, self).__init__()

        if environ.get("ENVIRONMENT") == "development":
            self.DATABASE_URL = str(environ.get("POSTGRES_CONNECTION_STRING"))
        else:
            self.DATABASE_URL = vault_service.get_secret(key="POSTGRES_CONNECTION_STRING")

    # Dependency
    @asynccontextmanager
    async def session(self):
        engine = create_async_engine(self.DATABASE_URL, echo=False)
        AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with AsyncSessionLocal() as session:
            yield session
