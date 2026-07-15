from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager
from os import environ

from src.infrastructure.context.vault.vault_service import VaultService
from src.infrastructure.di import inject
from src.infrastructure.utils.config_reader import ConfigReader

Base = declarative_base()


@inject
class PsqlDbContext:
    __di_singleton__ = True

    def __init__(self, vault_service: VaultService, config_reader: ConfigReader):
        super(PsqlDbContext, self).__init__()

        if not config_reader.is_vault_enabled():
            url = config_reader.get("database.url")
            if not url:
                raise RuntimeError(
                    "POSTGRES_CONNECTION_STRING is required when vault is disabled "
                    "(vaulthc.enabled=false)."
                )
            self.DATABASE_URL = str(url)
        else:
            self.DATABASE_URL = vault_service.get_secret(key="POSTGRES_CONNECTION_STRING")

    @asynccontextmanager
    async def session(self):
        engine = create_async_engine(self.DATABASE_URL, echo=False)
        AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with AsyncSessionLocal() as session:
            yield session
