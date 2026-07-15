from dependency_injector.containers import DeclarativeContainer 
from dependency_injector.providers import Factory, Singleton

from .context.sql_db.psql_dbcontext import PsqlDbContext
from .context.vault.vault_service import VaultService

class InfrastructureCollection(DeclarativeContainer):

    vault_service = Singleton(VaultService)

    psql_db_context = Singleton(PsqlDbContext, vault_service=vault_service)
