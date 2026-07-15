from __future__ import annotations

from dependency_injector.containers import DeclarativeContainer

from src.core.core_collection import CoreCollection
from src.infrastructure.di.reflection import ReflectiveCollection


class ApplicationCollection(DeclarativeContainer, ReflectiveCollection):
    """Auto-discovers every @inject class under src.application."""

    @classmethod
    def _before_bootstrap(cls) -> None:
        CoreCollection.bootstrap()
