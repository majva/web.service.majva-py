from __future__ import annotations

import inspect
from functools import wraps
from typing import Any, Callable, Optional, Type, TypeVar, get_type_hints

T = TypeVar("T")


class Injector:
    """Simple type-based dependency injector used by @inject and collections."""

    def __init__(self) -> None:
        self._factories: dict[type, Callable[[], Any]] = {}
        self._singletons: dict[type, Any] = {}
        self._singleton_flags: set[type] = set()

    def register(
        self,
        interface: type,
        factory: Callable[[], Any],
        *,
        singleton: bool = False,
    ) -> None:
        self._factories[interface] = factory
        if singleton:
            self._singleton_flags.add(interface)
        else:
            self._singleton_flags.discard(interface)
            self._singletons.pop(interface, None)

    def register_instance(self, interface: type, instance: Any) -> None:
        self._singletons[interface] = instance
        self._singleton_flags.add(interface)
        self._factories[interface] = lambda: instance

    def resolve(self, interface: type[T]) -> T:
        if interface in self._singleton_flags and interface in self._singletons:
            return self._singletons[interface]

        factory = self._factories.get(interface)
        if factory is None:
            raise RuntimeError(
                f"No provider registered for '{interface.__name__}'. "
                f"Mark the implementation with @inject and ensure collections are bootstrapped."
            )

        instance = factory()
        if interface in self._singleton_flags:
            self._singletons[interface] = instance
        return instance

    def is_registered(self, interface: type) -> bool:
        return interface in self._factories or interface in self._singletons


injector = Injector()


def resolve(interface: type[T]) -> T:
    """Prefer CoreCollection.resolve for services; this is the low-level resolver."""
    return injector.resolve(interface)


def register(
    interface: type,
    factory: Callable[[], Any],
    *,
    singleton: bool = False,
) -> None:
    injector.register(interface, factory, singleton=singleton)


def inject(cls: Type[T]) -> Type[T]:
    """
    Class decorator that resolves constructor dependencies by type hint
    through CoreCollection / InfrastructureCollection reflection.

    Example:
        @inject
        class ProfileService(IProfileService):
            def __init__(self, profile_repository: IProfileRepository):
                ...
    """
    original_init = cls.__init__
    signature = inspect.signature(original_init)

    @wraps(original_init)
    def new_init(self, *args, **kwargs):
        try:
            type_hints = get_type_hints(original_init)
        except Exception:
            type_hints = getattr(original_init, "__annotations__", {})

        bound = signature.bind_partial(self, *args, **kwargs)
        for name, param in signature.parameters.items():
            if name == "self":
                continue
            if name in bound.arguments:
                continue
            if param.default is not inspect.Parameter.empty:
                continue

            annotation = type_hints.get(name, param.annotation)
            if annotation is inspect.Parameter.empty:
                raise TypeError(
                    f"Cannot inject '{cls.__name__}.{name}': missing type annotation."
                )

            kwargs[name] = _resolve_reflected(annotation)

        original_init(self, *args, **kwargs)

    cls.__init__ = new_init
    cls.__di_injectable__ = True
    return cls


def _resolve_reflected(annotation: type) -> Any:
    """
    Route reflected resolution through the owning collection when possible.
    """
    module_name = getattr(annotation, "__module__", "") or ""

    if module_name.startswith("src.host."):
        from src.host.host_collection import WebHostCollection

        return WebHostCollection.resolve(annotation)

    if module_name.startswith("src.application."):
        from src.application.application_collection import ApplicationCollection

        return ApplicationCollection.resolve(annotation)

    if module_name.startswith("src.core."):
        from src.core.core_collection import CoreCollection

        return CoreCollection.resolve(annotation)

    if module_name.startswith("src.infrastructure."):
        from src.infrastructure.infrastructure_collection import InfrastructureCollection

        return InfrastructureCollection.resolve(annotation)

    return injector.resolve(annotation)


def provides(
    interface: Optional[type] = None,
    *,
    singleton: bool = False,
) -> Callable[[Type[T]], Type[T]]:
    """
    Optional explicit provider binding.
    Prefer @inject + CoreCollection reflection; use this only when needed.
    """

    def decorator(cls: Type[T]) -> Type[T]:
        target = interface or cls

        def factory() -> T:
            return cls()

        injector.register(target, factory, singleton=singleton)
        if target is not cls:
            injector.register(cls, factory, singleton=singleton)

        cls.__di_provides__ = target
        return cls

    return decorator
