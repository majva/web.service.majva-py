from jwt import PyJWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from keycloak import KeycloakOpenID
from fastapi import Security, HTTPException, status, Depends
import jwt

from src.domain.aggregations.user.user_auth import UserAuth

from os import environ

from src.infrastructure.context.vault.vault_service import VaultService


vault = VaultService()
# Use HTTPBearer to get the token directly from the Authorization header.
# This simplifies the Swagger UI to a simple "paste token" field.
oauth2_scheme = HTTPBearer()

keycloak_openid = KeycloakOpenID(
    server_url=str(environ.get('KEYCLOCK_HOST_AUTH')),
    client_id=vault.get_secret(key="KEYCLOAK_CLIENT_ID"),
    realm_name=environ.get("KEYCLOCK_REALM", "master"),  # Default to master if not set
    client_secret_key=vault.get_secret(key="KEYCLOAK_CLIENT_SECRET")
)

async def get_idp_public_key():
    try:
        public_key_raw = keycloak_openid.public_key()
        # Ensure proper PEM format
        if not public_key_raw.startswith("-----BEGIN PUBLIC KEY-----"):
            public_key_raw = f"-----BEGIN PUBLIC KEY-----\n{public_key_raw}\n-----END PUBLIC KEY-----"
        return public_key_raw
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get public key from Keycloak: {str(e)}. Please check Keycloak configuration.",
        )

async def get_payload(creds: HTTPAuthorizationCredentials = Security(oauth2_scheme)) -> dict:
    token = creds.credentials
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Get public key from Keycloak
        public_key = await get_idp_public_key()
        
        # Simple JWT decode with minimal options
        return jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
    except PyJWTError as e:
        print(f"JWT validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Unexpected authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
# Get user infos from the payload
async def get_user_info(payload: dict = Depends(get_payload)) -> UserAuth:
    # Safely extract roles with fallbacks for missing keys
    resource_access = payload.get("resource_access", {})
    client_id = vault.get_secret(key="KEYCLOAK_CLIENT_ID")
    client_roles = resource_access.get(client_id, {})
    roles = client_roles.get("roles", [])
    
    return UserAuth(
        id=payload.get("sub"),
        username=payload.get("preferred_username"),
        roles=roles
    )
