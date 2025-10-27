from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError
import requests
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()


security = HTTPBearer()

def get_jwks():
    keycloak_url = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
    realm_name = os.getenv("REALM_NAME", "aclimate")
    jwks_url = f"{keycloak_url}/realms/{realm_name}/protocol/openid-connect/certs"

    response = requests.get(jwks_url)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="No se pudo obtener las claves públicas (JWKS)")
    return response.json()

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