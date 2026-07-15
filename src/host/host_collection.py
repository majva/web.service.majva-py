from dependency_injector.containers import DeclarativeContainer 
from dependency_injector.providers import Callable

from src.application.application_collection import ApplicationCollection


class WebHostCollection(DeclarativeContainer):
    """ IoC container of application component providers. """

    def __init__(self):
        super(WebHostCollection, self).__init__()

    def __run_app__(self, web_service):
        web_service.start()

    main: Callable = Callable(
        __run_app__, self=None,
        web_service=ApplicationCollection.web_service,
    )
