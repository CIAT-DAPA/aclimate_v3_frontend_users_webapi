from fastapi import APIRouter, Depends, HTTPException
import requests
import os
from dependencies.auth_dependencies import require_roles

router = APIRouter(
    prefix="/users",
    tags=["Webadmin"]
)

@router.get("/get-user/{user_id}", summary="Get a user by ID with their client roles")
def get_user_with_client_roles(
    user_id: str,
    current_user: dict = Depends(require_roles(["adminsuper"]))
):
    # Environment variables
    KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
    REALM_NAME = os.getenv("REALM_NAME", "aclimate")
    CLIENT_ID_NAME = os.getenv("CLIENT_ID", "dummy-client")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")

    # Step 1: Get admin token using client credentials
    token_resp = requests.post(
        f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token",
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID_NAME,
            "client_secret": CLIENT_SECRET
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if token_resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Failed to obtain admin token")
    token = token_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Get client UUID by clientId
    clients_resp = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients",
        headers=headers
    )
    if clients_resp.status_code != 200:
        raise HTTPException(status_code=clients_resp.status_code, detail="Failed to fetch clients")
    clients = clients_resp.json()
    client = next((c for c in clients if c["clientId"] == CLIENT_ID_NAME), None)
    if not client:
        raise HTTPException(status_code=404, detail=f"Client '{CLIENT_ID_NAME}' not found")
    client_uuid = client["id"]

    # Step 3: Get the user by ID
    user_resp = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{user_id}",
        headers=headers
    )
    if user_resp.status_code == 404:
        raise HTTPException(status_code=404, detail=f"User with ID '{user_id}' not found")
    if user_resp.status_code != 200:
        raise HTTPException(status_code=user_resp.status_code, detail="Failed to fetch user")

    user = user_resp.json()

    # Step 4: Get client roles for this user
    roles_resp = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{user_id}/role-mappings/clients/{client_uuid}",
        headers=headers
    )
    if roles_resp.status_code != 200:
        user["client_roles"] = []
    else:
        roles = roles_resp.json()
        user["client_roles"] = [{"id": r["id"], "name": r["name"]} for r in roles]

    return user
