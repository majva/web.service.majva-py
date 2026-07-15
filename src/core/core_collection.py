from __future__ import annotations

from dependency_injector.containers import DeclarativeContainer

from src.infrastructure.di.reflection import ReflectiveCollection
from src.infrastructure.infrastructure_collection import InfrastructureCollection


class CoreCollection(DeclarativeContainer, ReflectiveCollection):
    """Auto-discovers every @inject class under src.core."""

    @classmethod
    def _before_bootstrap(cls) -> None:
        InfrastructureCollection.bootstrap()
