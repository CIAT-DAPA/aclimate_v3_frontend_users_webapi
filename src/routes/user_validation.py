from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from aclimate_v3_orm_frontend.services.user_service import UserService
from aclimate_v3_orm_frontend.schemas.user_schema import UserCreate
from aclimate_v3_orm_frontend.enums.profile_type import ProfileType

router = APIRouter(
    prefix="/validate",
    tags=["User Validation"]
)

class UserValidationRequest(BaseModel):
    email: str
    email_verified: bool
    family_name: str
    given_name: str
    name: str
    preferred_username: str
    sub: str
    app_id: str
    profile: str

@router.post("/user")
async def validate_user(user_data: UserValidationRequest):
    user_service = UserService()
    
    # Check if user exists by ext_key_clock_id (sub)
    existing_users = user_service.get_by_ext_key_clock_id(user_data.sub)
    
    if existing_users:
        # User exists, return the first user found
        return {"exists": True, "user": existing_users[0]}
    
    # User doesn't exist, create new user
    # Note: You might want to adjust app_id and profile based on your needs
    new_user = UserCreate(
        ext_key_clock_id=user_data.sub,
        app_id=user_data.app_id,  # Default app_id, adjust as needed
        profile=user_data.profile,  # Default profile, adjust as needed
        enable=True
    )
    
    try:
        created_user = user_service.create(new_user)
        return {"exists": False, "user": created_user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))