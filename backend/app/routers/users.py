from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from bson import ObjectId

from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, UserRole
)
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


def validate_object_id(id_value: str, field_name: str):
    """Validate that a string is a valid MongoDB ObjectId"""
    if not id_value:
        return
    if not ObjectId.is_valid(id_value):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name}: '{id_value}' is not a valid ObjectId. It must be a 24-character hex string."
        )


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate):
    """Create a new user"""
    service = UserService()
    try:
        return await service.create_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    role: Optional[UserRole] = None
):
    """Get paginated list of users"""
    service = UserService()
    role_value = role.value if role else None
    users, total = await service.get_users(page, page_size, role_value)
    return UserListResponse(
        users=users,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/all", response_model=list[UserResponse])
async def get_all_users():
    """Get all users for selection dropdowns"""
    service = UserService()
    users, _ = await service.get_users(1, 1000, None)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID"""
    validate_object_id(user_id, "user_id")
    
    service = UserService()
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_data: UserUpdate):
    """Update user"""
    validate_object_id(user_id, "user_id")
    
    service = UserService()
    try:
        user = await service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str):
    """Delete user"""
    validate_object_id(user_id, "user_id")
    
    service = UserService()
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/role/{role}", response_model=list[UserResponse])
async def get_users_by_role(role: UserRole):
    """Get all users with a specific role"""
    service = UserService()
    return await service.get_users_by_role(role.value)
