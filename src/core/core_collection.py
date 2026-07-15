from dependency_injector.containers import DeclarativeContainer 
from dependency_injector.providers import Factory, Singleton

from src.infrastructure.infrastructure_collection import InfrastructureCollection

from .business.account.account_business import AccountBusiness
from .services.vault.vault_service import VaultService
from .services.sso.authenticate_service import AuthenticateService
from .services.log_management.log_manager import LogManager

class CoreCollection(DeclarativeContainer):
    """ IoC container of business service providers """

    vault_service: Singleton = Singleton(VaultService)

    logger_service: Singleton = Singleton(LogManager, instance="stdout", vault_service=vault_service)

    authentication_service: Factory = Factory(
        AuthenticateService,
        vault=vault_service
    )

    account_business: Factory = Factory(
        AccountBusiness,
        account_repository=InfrastructureCollection.account_repository,
        authentication_service=authentication_service
    )
