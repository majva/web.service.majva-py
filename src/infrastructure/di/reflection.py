from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import TypeVar

from src.infrastructure.di.inject import injector

T = TypeVar("T")

# Paths that never hold injectable providers
_SKIP_DIR_NAMES = frozenset({
    "__pycache__",
    "alembic",
    "versions",
    "scripts",
    "di",
    "sto",
    "dtos",
    "aggregations",
})


class ReflectiveCollection:
    """
    Base IoC collection.

    Subclasses need nothing except inheriting this — the layer package is
    inferred from the collection module itself, then every @inject class
    under that package tree is registered automatically.
    """

    _bootstrapped: bool = False

    @classmethod
    def bootstrap(cls) -> None:
        if cls._bootstrapped:
            return

        cls._before_bootstrap()

        root, prefix = cls._layer_package()
        cls._discover_package(root, prefix)

        cls._after_bootstrap()
        cls._bootstrapped = True

    @classmethod
    def resolve(cls, interface: type[T]) -> T:
        cls.bootstrap()
        return injector.resolve(interface)

    @classmethod
    def _before_bootstrap(cls) -> None:
        """Bootstrap parent layers first."""

    @classmethod
    def _after_bootstrap(cls) -> None:
        """Hook for layer-specific registrations."""

    @classmethod
    def _layer_package(cls) -> tuple[Path, str]:
        """
        Infer this layer's package from the collection class location.

            src/infrastructure/infrastructure_collection.py
              → root = src/infrastructure
              → prefix = src.infrastructure
        """
        module = importlib.import_module(cls.__module__)
        module_file = Path(inspect.getfile(module)).resolve()
        package_root = module_file.parent
        package_prefix = cls.__module__.rsplit(".", 1)[0]
        return package_root, package_prefix

    @classmethod
    def _discover_package(cls, root: Path, package_prefix: str) -> None:
        if not root.exists():
            return

        for file_path in root.rglob("*.py"):
            if file_path.name.startswith("_"):
                continue
            if file_path.name.endswith("_collection.py"):
                continue
            if any(part in _SKIP_DIR_NAMES for part in file_path.relative_to(root).parts):
                continue

            relative = file_path.relative_to(root).with_suffix("")
            module_name = f"{package_prefix}.{'.'.join(relative.parts)}"

            try:
                module = importlib.import_module(module_name)
            except Exception:
                continue

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ != module.__name__:
                    continue
                if not getattr(obj, "__di_injectable__", False):
                    continue

                interface = cls._infer_interface(obj)
                if injector.is_registered(interface):
                    continue

                singleton = getattr(obj, "__di_singleton__", False)
                injector.register(interface, obj, singleton=singleton)

                if interface is not obj and not injector.is_registered(obj):
                    injector.register(obj, obj, singleton=singleton)

    @staticmethod
    def _infer_interface(cls_obj: type) -> type:
        explicit = getattr(cls_obj, "__di_provides__", None)
        if explicit is not None:
            return explicit

        for base in cls_obj.__bases__:
            if base is object:
                continue
            if inspect.isabstract(base) or base.__name__.startswith("I"):
                return base

        return cls_obj
