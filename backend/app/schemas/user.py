from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from app.core.types import PyObjectId


class UserRole(str, Enum):
    buyer = "buyer"
    seller = "seller"
    buyer_agent = "buyer_agent"
    seller_agent = "seller_agent"
    buyer_lawyer = "buyer_lawyer"
    seller_lawyer = "seller_lawyer"


class ProfileSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    address: Optional[str] = None


class AgentSpecific(BaseModel):
    license_number: str
    brokerage: str
    commission_rate: Optional[float] = Field(default=2.5, ge=0, le=10)


class LawyerSpecific(BaseModel):
    bar_number: str
    law_firm: str
    specialization: Optional[str] = "Real Estate"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole
    profile: ProfileSchema
    role_specific: Optional[Dict[str, Any]] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    profile: Optional[ProfileSchema] = None
    role_specific: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    email: EmailStr
    role: UserRole
    profile: ProfileSchema
    role_specific: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
    page: int
    page_size: int
