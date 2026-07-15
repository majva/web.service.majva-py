from src.host.host_collection import WebHostCollection


def bootstrap_di() -> None:
    """Bootstrap all reflected DI layers from host down to infrastructure."""
    WebHostCollection.bootstrap()
