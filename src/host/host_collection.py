from __future__ import annotations

from pathlib import Path

from dependency_injector.containers import DeclarativeContainer

from src.application.application_collection import ApplicationCollection
from src.application.web import WebService
from src.infrastructure.di.reflection import ReflectiveCollection


class WebHostCollection(DeclarativeContainer, ReflectiveCollection):
    """Auto-discovers every @inject class under src.host."""

    @classmethod
    def _before_bootstrap(cls) -> None:
        ApplicationCollection.bootstrap()

    @classmethod
    def main(cls) -> None:
        cls.bootstrap()
        web_service = ApplicationCollection.resolve(WebService)
        web_service.start()
