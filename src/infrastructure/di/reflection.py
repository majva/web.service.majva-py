from __future__ import annotations

import importlib
import inspect
from pathlib import Path

from src.infrastructure.di.inject import injector

_SKIP_DIR_NAMES = frozenset({
    "__pycache__",
    "alembic",
    "versions",
    "scripts",
    "di",
    "dtos",
    "models",
    "res",
    "sso",  # FastAPI Depends helpers — not DI providers
})

_bootstrapped = False


def discover_package(root: Path, package_prefix: str) -> None:
    """Register every @inject class under a package tree."""
    if not root.exists():
        return

    for file_path in root.rglob("*.py"):
        if file_path.name.startswith("_"):
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

            interface = _infer_interface(obj)
            if injector.is_registered(interface):
                continue

            singleton = getattr(obj, "__di_singleton__", False)
            injector.register(interface, obj, singleton=singleton)

            if interface is not obj and not injector.is_registered(obj):
                injector.register(obj, obj, singleton=singleton)


def _infer_interface(cls_obj: type) -> type:
    for base in cls_obj.__bases__:
        if base is object:
            continue
        if inspect.isabstract(base) or base.__name__.startswith("I"):
            return base
    return cls_obj


def bootstrap_packages() -> None:
    """Scan infrastructure → core → application once."""
    global _bootstrapped
    if _bootstrapped:
        return

    src_root = Path(__file__).resolve().parents[2]
    for name in ("infrastructure", "core", "application"):
        discover_package(src_root / name, f"src.{name}")

    _bootstrapped = True
