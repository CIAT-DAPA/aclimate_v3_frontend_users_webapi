from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
from aclimate_v3_orm_frontend.services.user_service import UserService
from aclimate_v3_orm_frontend.schemas.user_schema import UserUpdate, UserRead
from aclimate_v3_orm_frontend.enums.profile_type import ProfileType

router = APIRouter(
    prefix="/user",
    tags=["User Profile"]
)

# Enum para los valores permitidos de profile
class AllowedProfileType(str, Enum):
    FARMER = "FARMER"
    TECHNICIAN = "TECHNICIAN"

class UpdateProfileRequest(BaseModel):
    profile: AllowedProfileType = Field(..., description="Profile type: FARMER or TECHNICIAN")

user_service = UserService()

@router.put("/{user_id}/profile", response_model=UserRead, summary="Update user profile")
async def update_user_profile(
    user_id: int,
    profile_data: UpdateProfileRequest
):
    """
    Update a user's profile type. Only FARMER and TECHNICIAN profiles are allowed.
    
    Args:
        user_id: The ID of the user to update
        profile_data: Profile data containing the new profile type
        current_user: Current authenticated user from token
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: 404 if user not found, 400 if validation fails
    """
    try:
        # Verify user exists
        existing_user = user_service.get_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        # Convert string to ProfileType enum
        profile_enum = ProfileType(profile_data.profile.value)
        
        # Create update object
        user_update = UserUpdate(profile=profile_enum)
        
        # Update user
        updated_user = user_service.update(user_id, user_update)
        
        return updated_user
        
    except ValueError as ve:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid profile type. Allowed values: FARMER, TECHNICIAN"
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
