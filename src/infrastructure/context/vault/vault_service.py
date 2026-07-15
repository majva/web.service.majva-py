
from hvac import (
    Client as hvac_Client
)

from os import environ
from typing import Any


class VaultService:

    def __init__(self):
        self.hvac_Client = hvac_Client(
            url= str(environ.get("VAULT_HOST")),
            token= str(environ.get("VAULT_TOKEN")),
            verify=True
        )
        self.path: str = environ.get("KV_NAMESPACE")

    def get_secret(self, key: str, version: int=int(environ.get("KV_VERSION"))) -> Any:
        secret_valut = self.hvac_Client.secrets.kv.v2.read_secret_version(path=self.path, version=version, mount_point="kv")
        return secret_valut['data']['data'][f"{key}"]
