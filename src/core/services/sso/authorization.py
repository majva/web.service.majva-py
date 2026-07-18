"""
Optional Keycloak auth helpers for FastAPI Depends.

Nothing is constructed at import time — clients and secrets resolve lazily
after bootstrap_di() so local/dev startups are not blocked by SSO config.
"""

from __future__ import annotations

from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError
from keycloak import KeycloakOpenID
from os import environ

from src.core.services.sso.user_auth import UserAuth
from src.infrastructure.context.vault.vault_service import VaultService
from src.infrastructure.di.inject import resolve

oauth2_scheme = HTTPBearer()

_vault: Optional[VaultService] = None
_keycloak: Optional[KeycloakOpenID] = None


def _get_vault() -> VaultService:
    global _vault
    if _vault is None:
        _vault = resolve(VaultService)
    return _vault


def _get_keycloak() -> KeycloakOpenID:
    global _keycloak
    if _keycloak is None:
        vault = _get_vault()
        _keycloak = KeycloakOpenID(
            server_url=str(environ.get("KEYCLOCK_HOST_AUTH")),
            client_id=vault.get_secret(key="KEYCLOAK_CLIENT_ID"),
            realm_name=environ.get("KEYCLOCK_REALM", "master"),
            client_secret_key=vault.get_secret(key="KEYCLOAK_CLIENT_SECRET"),
        )
    return _keycloak


async def get_idp_public_key() -> str:
    try:
        public_key_raw = _get_keycloak().public_key()
        if not public_key_raw.startswith("-----BEGIN PUBLIC KEY-----"):
            public_key_raw = (
                f"-----BEGIN PUBLIC KEY-----\n{public_key_raw}\n-----END PUBLIC KEY-----"
            )
        return public_key_raw
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get public key from Keycloak: {e}. "
            "Please check Keycloak configuration.",
        )


async def get_payload(
    creds: HTTPAuthorizationCredentials = Security(oauth2_scheme),
) -> dict:
    token = creds.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        public_key = await get_idp_public_key()
        return jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_user_info(payload: dict = Depends(get_payload)) -> UserAuth:
    vault = _get_vault()
    resource_access = payload.get("resource_access", {})
    client_id = vault.get_secret(key="KEYCLOAK_CLIENT_ID")
    client_roles = resource_access.get(client_id, {})
    roles = client_roles.get("roles", [])

    return UserAuth(
        id=payload.get("sub"),
        username=payload.get("preferred_username"),
        roles=roles,
    )
