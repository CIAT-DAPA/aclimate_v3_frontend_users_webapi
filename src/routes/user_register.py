from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
import httpx

from aclimate_v3_orm_frontend.services.user_service import UserService
from aclimate_v3_orm_frontend.schemas.user_schema import UserCreate, UserRead
from aclimate_v3_orm_frontend.models.user import User
from aclimate_v3_orm_frontend.models.app import App
from aclimate_v3_orm_frontend.enums.profile_type import ProfileType

router = APIRouter(
    prefix="/register",
    tags=["User Register"]
)

# Variables de entorno Keycloak
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
REALM_NAME = os.getenv("REALM_NAME")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

class Credential(BaseModel):
    type: str = "password"
    value: str
    temporary: bool = False

class UserRegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    firstName: Optional[str] = ""
    lastName: Optional[str] = ""
    emailVerified: Optional[bool] = False
    enabled: Optional[bool] = True
    attributes: Optional[Dict[str, str]] = None
    app_id: int
    profile: ProfileType

async def get_admin_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Keycloak credentials error")
    return response.json()["access_token"]


user_service = UserService()

@router.post("/", response_model=UserRead, summary="Registrar usuario en Keycloak y base de datos local")
async def register_user(
    request: UserRegisterRequest,
):
    token = await get_admin_token()

    # 1. Crear usuario en Keycloak
    user_payload = {
        "username": request.username,
        "email": request.email,
        "enabled": request.enabled,
        "emailVerified": request.emailVerified,
        "firstName": request.firstName or "",
        "lastName": request.lastName or "",
        "credentials": [{
            "type": "password",
            "value": request.password,
            "temporary": False
        }],
        "attributes": request.attributes or {}
    }

    async with httpx.AsyncClient() as client:
        kc_resp = await client.post(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users",
            headers={"Authorization": f"Bearer {token}"},
            json=user_payload,
        )
        if kc_resp.status_code not in (201, 204):
            raise HTTPException(status_code=400, detail=f"Keycloak error: {kc_resp.text}")

        users_resp = await client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users?username={request.username}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if users_resp.status_code != 200 or not users_resp.json():
            raise HTTPException(status_code=500, detail="No se pudo obtener el usuario de Keycloak")
        ext_key_clock_id = users_resp.json()[0]["id"]

    # 2. Guardar usuario en base de datos local usando el servicio
    user_in = UserCreate(
        ext_key_clock_id=ext_key_clock_id,
        app_id=request.app_id,
        profile=request.profile,
        enable=True
    )
    db_user = user_service.create(user_in)

    return db_user