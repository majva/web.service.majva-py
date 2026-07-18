import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import find_dotenv, load_dotenv

from src.infrastructure.di.inject import inject

_RES_DIR = Path(__file__).resolve().parents[2] / "host" / "res"


@inject
class ConfigReader:
    """
    Loads appsettings from src/host/res based on env_type in .env.

    development -> appsettings.development.yaml
    anything else -> appsettings.yaml
    """
    __di_singleton__ = True

    _dotenv_loaded = False

    def __init__(self):
        self._config = self._load_config()

    @classmethod
    def _ensure_dotenv_loaded(cls) -> None:
        if cls._dotenv_loaded:
            return
        dotenv_path = find_dotenv(usecwd=True)
        if dotenv_path:
            load_dotenv(dotenv_path)
        cls._dotenv_loaded = True

    @classmethod
    def _resolve_config_path(cls) -> Path:
        cls._ensure_dotenv_loaded()
        env_type = os.getenv("env_type", "development").strip().lower()
        filename = (
            "appsettings.development.yaml"
            if env_type == "development"
            else "appsettings.yaml"
        )
        return _RES_DIR / filename

    def _load_config(self) -> Dict[str, Any]:
        config_path = self._resolve_config_path()
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file) or {}
                if not isinstance(data, dict):
                    raise ValueError(f"Config root must be a mapping: {config_path}")
                return data
        except Exception as e:
            raise RuntimeError(
                f"Error loading configuration from {config_path}: {e}"
            ) from e

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation (e.g. 'app.version')."""
        try:
            value: Any = self._config
            for part in key.split("."):
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default

    def get_app_version(self) -> str:
        return self.get("app.version", "1.0.0")

    def get_app_name(self) -> str:
        return self.get("app.name", "Plugin Service API")

    def get_app_description(self) -> str:
        return self.get("app.description", "Your plugin apis")

    def get_server_host(self) -> str:
        return self.get("server.host", "0.0.0.0")

    def get_server_port(self) -> int:
        return self.get("server.port", 5000)

    def get_api_prefix(self) -> str:
        return self.get("api.prefix", "/api/v1")

    def get_cors_config(self) -> Dict[str, Any]:
        return self.get("api.cors", {}) or {}

    def is_vault_enabled(self) -> bool:
        return bool(self.get("vaulthc.enabled", False))

    @property
    def config(self) -> Dict[str, Any]:
        return self._config.copy()
