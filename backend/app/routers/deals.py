from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from bson import ObjectId

from app.schemas.deal import (
    DealCreate, DealUpdate, DealResponse, DealListResponse,
    DealStatus, DealStatusUpdate, ConditionCreate, ConditionUpdate
)
from app.services.deal_service import DealService

router = APIRouter(prefix="/api/deals", tags=["deals"])


def validate_object_id(id_value: str, field_name: str):
    """Validate that a string is a valid MongoDB ObjectId"""
    if not id_value:
        return
    if not ObjectId.is_valid(id_value):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name}: '{id_value}' is not a valid ObjectId. It must be a 24-character hex string."
        )


@router.post("", response_model=DealResponse, status_code=201)
async def create_deal(deal_data: DealCreate):
    """Create a new deal with participant snapshots"""
    # Validate all ObjectId fields
    validate_object_id(str(deal_data.property_id), "property_id")
    if deal_data.participants:
        if deal_data.participants.buyer_id:
            validate_object_id(str(deal_data.participants.buyer_id), "buyer_id")
        if deal_data.participants.seller_id:
            validate_object_id(str(deal_data.participants.seller_id), "seller_id")
        if deal_data.participants.buyer_agent_id:
            validate_object_id(str(deal_data.participants.buyer_agent_id), "buyer_agent_id")
        if deal_data.participants.seller_agent_id:
            validate_object_id(str(deal_data.participants.seller_agent_id), "seller_agent_id")
        if deal_data.participants.buyer_lawyer_id:
            validate_object_id(str(deal_data.participants.buyer_lawyer_id), "buyer_lawyer_id")
        if deal_data.participants.seller_lawyer_id:
            validate_object_id(str(deal_data.participants.seller_lawyer_id), "seller_lawyer_id")
    
    service = DealService()
    try:
        return await service.create_deal(deal_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=DealListResponse)
async def list_deals(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[DealStatus] = None,
    property_id: Optional[str] = None
):
    """Get paginated list of deals"""
    if property_id:
        validate_object_id(property_id, "property_id")
    
    service = DealService()
    status_value = status.value if status else None
    deals, total = await service.get_deals(page, page_size, status_value, property_id)
    return DealListResponse(
        deals=deals,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(deal_id: str):
    """Get deal by ID"""
    validate_object_id(deal_id, "deal_id")
    
    service = DealService()
    deal = await service.get_deal(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.put("/{deal_id}", response_model=DealResponse)
async def update_deal(deal_id: str, deal_data: DealUpdate):
    """Update deal basic info"""
    validate_object_id(deal_id, "deal_id")
    
    service = DealService()
    deal = await service.update_deal(deal_id, deal_data)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.patch("/{deal_id}/status", response_model=DealResponse)
async def update_deal_status(deal_id: str, status_update: DealStatusUpdate):
    """Update deal status"""
    validate_object_id(deal_id, "deal_id")
    
    service = DealService()
    try:
        deal = await service.update_deal_status(deal_id, status_update)
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        return deal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{deal_id}/conditions", response_model=DealResponse)
async def add_condition(deal_id: str, condition: ConditionCreate):
    """Add a condition to a deal"""
    validate_object_id(deal_id, "deal_id")
    
    service = DealService()
    deal = await service.add_condition(deal_id, condition)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.patch("/{deal_id}/conditions/{condition_id}", response_model=DealResponse)
async def update_condition(deal_id: str, condition_id: str, update: ConditionUpdate):
    """Update a condition status"""
    validate_object_id(deal_id, "deal_id")
    
    service = DealService()
    deal = await service.update_condition(deal_id, condition_id, update)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal or condition not found")
    return deal


@router.delete("/{deal_id}", status_code=204)
async def delete_deal(deal_id: str):
    """Delete deal (only if in draft status)"""
    validate_object_id(deal_id, "deal_id")
    
    service = DealService()
    deleted = await service.delete_deal(deal_id)
    if not deleted:
        raise HTTPException(
            status_code=400,
            detail="Deal not found or cannot be deleted (only draft deals can be deleted)"
        )
