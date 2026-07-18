from src.infrastructure.di.reflection import bootstrap_packages


def bootstrap_di() -> None:
    """Discover and register all @inject classes under src/."""
    bootstrap_packages()
