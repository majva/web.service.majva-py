from __future__ import annotations

from dependency_injector.containers import DeclarativeContainer

from src.infrastructure.di.reflection import ReflectiveCollection


class InfrastructureCollection(DeclarativeContainer, ReflectiveCollection):
    """Auto-discovers every @inject class under src.infrastructure."""
