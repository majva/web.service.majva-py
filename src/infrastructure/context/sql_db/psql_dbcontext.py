from contextlib import asynccontextmanager
from os import environ

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.infrastructure.context.vault.vault_service import VaultService
from src.infrastructure.di.inject import inject
from src.infrastructure.utils.config_reader import ConfigReader

Base = declarative_base()


def _to_async_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


@inject
class PsqlDbContext:
    __di_singleton__ = True

    def __init__(self, config_reader: ConfigReader, vault_service: VaultService):
        if not config_reader.is_vault_enabled():
            url = config_reader.get("database.url") or environ.get("POSTGRES_CONNECTION_STRING")
            if not url:
                raise RuntimeError(
                    "database.url (or POSTGRES_CONNECTION_STRING) is required when "
                    "vault is disabled (vaulthc.enabled=false)."
                )
        else:
            url = vault_service.get_secret(key="POSTGRES_CONNECTION_STRING")

        self._engine = create_async_engine(_to_async_url(str(url)), echo=False)
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def session(self):
        async with self._session_factory() as session:
            yield session
