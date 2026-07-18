from os import environ
from typing import Any

from src.infrastructure.di.inject import inject
from src.infrastructure.utils.config_reader import ConfigReader


@inject
class VaultService:
    __di_singleton__ = True

    def __init__(self, config_reader: ConfigReader):
        self.config_reader = config_reader
        self.enabled = config_reader.is_vault_enabled()
        self.hvac_Client = None
        self.path: str | None = None

        if not self.enabled:
            return

        from hvac import Client as hvac_Client

        self.hvac_Client = hvac_Client(
            url=str(config_reader.get("vaulthc.VAULT_HOST")),
            token=str(environ.get("vaulthc.VAULT_TOKEN") or environ.get("VAULT_TOKEN")),
            verify=True,
        )
        self.path = config_reader.get("vaulthc.KV_NAMESPACE")

    def get_secret(self, key: str) -> Any:
        if not self.enabled:
            value = environ.get(key)
            if value is None:
                raise ValueError(
                    f"Secret '{key}' not found in environment variables. "
                    f"Vault is disabled (vaulthc.enabled=false)."
                )
            return value

        version = int(self.config_reader.get("vaulthc.KV_VERSION"))
        secret_vault = self.hvac_Client.secrets.kv.v2.read_secret_version(
            path=self.path,
            version=version,
            mount_point="kv",
        )
        if secret_vault["data"]["data"] is None:
            raise ValueError(f"Secret {key} not found")
        return secret_vault["data"]["data"][f"{key}"]
