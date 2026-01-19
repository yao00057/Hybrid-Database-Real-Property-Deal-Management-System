from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from bson import ObjectId

from app.schemas.property import (
    PropertyCreate, PropertyUpdate, PropertyResponse, 
    PropertyListResponse, PropertyType, PropertyStatus
)
from app.services.property_service import PropertyService

router = APIRouter(prefix="/api/properties", tags=["properties"])


def validate_object_id(id_value: str, field_name: str):
    """Validate that a string is a valid MongoDB ObjectId"""
    if not id_value:
        return
    if not ObjectId.is_valid(id_value):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name}: '{id_value}' is not a valid ObjectId. It must be a 24-character hex string."
        )


@router.post("", response_model=PropertyResponse, status_code=201)
async def create_property(property_data: PropertyCreate):
    """Create a new property listing"""
    service = PropertyService()
    return await service.create_property(property_data)


@router.get("", response_model=PropertyListResponse)
async def list_properties(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    type: Optional[PropertyType] = None,
    status: Optional[PropertyStatus] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    city: Optional[str] = None
):
    """Get paginated list of properties with filters"""
    service = PropertyService()
    type_value = type.value if type else None
    status_value = status.value if status else None
    
    properties, total = await service.get_properties(
        page, page_size, type_value, status_value, min_price, max_price, city
    )
    return PropertyListResponse(
        properties=properties,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/active", response_model=list[PropertyResponse])
async def get_active_properties():
    """Get all active property listings for selection"""
    service = PropertyService()
    return await service.get_active_properties()


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: str):
    """Get property by ID"""
    validate_object_id(property_id, "property_id")
    
    service = PropertyService()
    property = await service.get_property(property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    return property


@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(property_id: str, property_data: PropertyUpdate):
    """Update property"""
    validate_object_id(property_id, "property_id")
    
    service = PropertyService()
    property = await service.update_property(property_id, property_data)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    return property


@router.delete("/{property_id}", status_code=204)
async def delete_property(property_id: str):
    """Delete property"""
    validate_object_id(property_id, "property_id")
    
    service = PropertyService()
    deleted = await service.delete_property(property_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Property not found")
