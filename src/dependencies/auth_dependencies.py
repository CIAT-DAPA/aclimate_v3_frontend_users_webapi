from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError
import requests
import os
import time
import logging
from dotenv import load_dotenv
from typing import List

logger = logging.getLogger(__name__)

load_dotenv()


security = HTTPBearer()

# JWKS cache: stores {"keys": [...], "cached_at": float}
_jwks_cache: dict = {}
_JWKS_TTL_SECONDS = int(os.getenv("JWKS_TTL_SECONDS", 300))


def get_jwks():
    keycloak_url = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
    realm_name = os.getenv("REALM_NAME", "aclimate")
    now = time.monotonic()
    if _jwks_cache.get("keys") and now - _jwks_cache.get("cached_at", 0) < _JWKS_TTL_SECONDS:
        return {"keys": _jwks_cache["keys"]}

    jwks_url = f"{keycloak_url}/realms/{realm_name}/protocol/openid-connect/certs"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; AclimateUsersAPI/1.0)",
        "Accept": "application/json",
    }
    try:
        response = requests.get(jwks_url, timeout=10, headers=headers)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión al obtener JWKS: {e}")
        raise HTTPException(status_code=503, detail=f"No se pudo obtener las claves públicas (JWKS): {str(e)}")
    if response.status_code != 200:
        logger.error(f"JWKS respondió {response.status_code}: {response.text}")
        raise HTTPException(status_code=503, detail=f"No se pudo obtener las claves públicas (JWKS): status {response.status_code}")

    data = response.json()
    _jwks_cache["keys"] = data["keys"]
    _jwks_cache["cached_at"] = now
    return data

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    unverified_header = jwt.get_unverified_header(token)

    jwks = get_jwks()
    key = next((k for k in jwks["keys"] if k["kid"] == unverified_header["kid"]), None)
    if not key:
        raise HTTPException(status_code=401, detail="Clave pública no encontrada")

    keycloak_url = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
    realm_name = os.getenv("REALM_NAME", "aclimate")

    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[unverified_header["alg"]],
            audience="account",
            issuer=f"{keycloak_url}/realms/{realm_name}",
        )
        return payload

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")

def require_roles(required_roles: List[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        client_id = os.getenv("CLIENT_ID", "dummy-client")
        client_roles = current_user.get("resource_access", {}).get(client_id, {}).get("roles", [])

        if not any(role in client_roles for role in required_roles):
            raise HTTPException(
                status_code=403,
                detail=f"Acceso denegado. Se requieren roles: {required_roles}"
            )

        return current_user

    return role_checker