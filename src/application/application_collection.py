from dependency_injector.containers import DeclarativeContainer 
from dependency_injector.providers import Factory

from .web import WebService
from src.core.core_collection import CoreCollection


class ApplicationCollection(DeclarativeContainer):

    web_service: Factory = Factory(
        WebService,
        authentication_service=CoreCollection.authentication_service,
        account_business=CoreCollection.account_business,
        logger_service=CoreCollection.logger_service
    )
