from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Optional
from aclimate_v3_orm_frontend.services.ws_interested_service import WsInterestedService
from aclimate_v3_orm_frontend.services.user_service import UserService
from aclimate_v3_orm_frontend.schemas.ws_interested_schema import WsInterestedCreate, WsInterestedRead, WsInterestedUpdate

router = APIRouter(
    prefix="/user-stations",
    tags=["User Weather Stations"]
)

security = HTTPBearer()

class WsInterestedRequest(BaseModel):
    ws_ext_id: str
    notification: dict

class WsInterestedUpdateRequest(BaseModel):
    notification: Optional[dict] = None

# Initialize services
ws_interested_service = WsInterestedService()
user_service = UserService()

@router.get("/{user_id}", response_model=List[WsInterestedRead], summary="Get all weather stations for a user")
async def get_user_stations(user_id: int):
    """
    Get all weather stations that a user is interested in.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        List of weather stations the user is interested in (empty list if none)
    """
    try:
        # Verify user exists
        user_exists = user_service.get_by_id(user_id)
        if not user_exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user stations (returns empty list if user has no stations)
        stations = ws_interested_service.get_by_user(user_id)
        return stations if stations else []
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}", response_model=WsInterestedRead, summary="Add a weather station to user interests")
async def add_user_station(user_id: int, station_data: WsInterestedRequest):
    """
    Add a new weather station to a user's interests.
    
    Args:
        user_id: The ID of the user
        station_data: Weather station data including ws_ext_id and notification settings
        
    Returns:
        The created weather station interest record
    """
    try:
        # Verify user exists
        user_exists = user_service.get_by_id(user_id)
        if not user_exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user is already interested in this station
        existing_stations = ws_interested_service.get_by_user(user_id)
        for station in existing_stations:
            if station.ws_ext_id == station_data.ws_ext_id:
                raise HTTPException(
                    status_code=400, 
                    detail=f"User is already interested in weather station {station_data.ws_ext_id}"
                )
        
        # Create new interest record
        new_station = WsInterestedCreate(
            user_id=user_id,
            ws_ext_id=station_data.ws_ext_id,
            notification=station_data.notification
        )
        
        created_station = ws_interested_service.create(new_station)
        return created_station
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}/{ws_ext_id}", response_model=WsInterestedRead, summary="Update weather station notification settings")
async def update_user_station(user_id: int, ws_ext_id: str, update_data: WsInterestedUpdateRequest):
    """
    Update notification settings for a user's weather station interest.
    
    Args:
        user_id: The ID of the user
        ws_ext_id: The external weather station ID
        update_data: Updated notification settings
        
    Returns:
        The updated weather station interest record
    """
    try:
        # Get user stations
        user_stations = ws_interested_service.get_by_user(user_id)
        
        # Find the specific station
        target_station = None
        for station in user_stations:
            if station.ws_ext_id == ws_ext_id:
                target_station = station
                break
        
        if not target_station:
            raise HTTPException(
                status_code=404, 
                detail=f"Weather station {ws_ext_id} not found for user {user_id}"
            )
        
        # Update the station
        update_obj = WsInterestedUpdate()
        if update_data.notification is not None:
            update_obj.notification = update_data.notification
        
        updated_station = ws_interested_service.update(target_station.id, update_obj)
        return updated_station
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}/{ws_ext_id}", summary="Remove a weather station from user interests")
async def delete_user_station(user_id: int, ws_ext_id: str):
    """
    Remove a weather station from a user's interests.
    
    Args:
        user_id: The ID of the user
        ws_ext_id: The external weather station ID to remove
        
    Returns:
        Success message
    """
    try:
        # Get user stations
        user_stations = ws_interested_service.get_by_user(user_id)
        
        # Find the specific station
        target_station = None
        for station in user_stations:
            if station.ws_ext_id == ws_ext_id:
                target_station = station
                break
        
        if not target_station:
            raise HTTPException(
                status_code=404, 
                detail=f"Weather station {ws_ext_id} not found for user {user_id}"
            )
        
        # Delete the station interest
        ws_interested_service.delete(target_station.id)
        
        return {"message": f"Weather station {ws_ext_id} removed from user {user_id} interests"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

