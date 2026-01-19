from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from app.core.types import PyObjectId


class PropertyType(str, Enum):
    residential = "residential"
    commercial = "commercial"


class PropertyStatus(str, Enum):
    active = "active"
    pending = "pending"
    sold = "sold"
    withdrawn = "withdrawn"


class AddressSchema(BaseModel):
    street: str
    city: str
    province: str = "ON"
    postal_code: str
    country: str = "Canada"


class ResidentialAttributes(BaseModel):
    bedrooms: int = Field(ge=0)
    bathrooms: float = Field(ge=0)
    sqft: int = Field(ge=0)
    year_built: Optional[int] = None
    parking_spaces: Optional[int] = 0
    has_basement: Optional[bool] = False
    has_garage: Optional[bool] = False


class CommercialAttributes(BaseModel):
    sqft: int = Field(ge=0)
    zoning: str
    lot_size: Optional[float] = None
    cap_rate: Optional[float] = None
    lease_terms: Optional[str] = None
    num_units: Optional[int] = None


class PropertyCreate(BaseModel):
    type: PropertyType
    address: AddressSchema
    listing_price: float = Field(gt=0)
    attributes: Dict[str, Any] = {}
    description: Optional[str] = None
    images: List[str] = []


class PropertyUpdate(BaseModel):
    listing_price: Optional[float] = Field(default=None, gt=0)
    status: Optional[PropertyStatus] = None
    attributes: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    images: Optional[List[str]] = None


class PropertyResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    type: PropertyType
    address: AddressSchema
    listing_price: float
    status: PropertyStatus
    attributes: Dict[str, Any]
    description: Optional[str] = None
    images: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True


class PropertyListResponse(BaseModel):
    properties: list[PropertyResponse]
    total: int
    page: int
    page_size: int
