from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from bson import ObjectId
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.schemas.deal import (
    DealCreate, DealUpdate, DealResponse, DealListResponse,
    DealStatus, DealStatusUpdate, ConditionCreate, ConditionUpdate,
    DealWithDepositCreate, DealWithDepositResponse
)
from app.services.deal_service import DealService
from app.services.saga_service import DealDepositSaga
from app.database.mongodb import get_database
from app.database.mysql import get_session, async_session_factory
from app.models.transaction import Transaction

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
    
    # Validate property exists and is not sold
    db = get_database()
    prop = await db.properties.find_one({"_id": ObjectId(str(deal_data.property_id))})
    if not prop:
        raise HTTPException(status_code=400, detail="Property not found")
    if prop.get("status") == "sold":
        raise HTTPException(
            status_code=400,
            detail="Cannot create deal: this property is already sold."
        )

    # Check for existing active deals on this property
    active_statuses = ["draft", "submitted", "conditional", "firm", "closing"]
    active_deal_count = await db.deals.count_documents({
        "property_id": ObjectId(str(deal_data.property_id)),
        "status": {"$in": active_statuses}
    })
    if active_deal_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot create deal: this property already has {active_deal_count} active deal(s). "
                   f"Complete or cancel existing deals first."
        )

    service = DealService()
    try:
        return await service.create_deal(deal_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/with-deposit", response_model=DealWithDepositResponse, status_code=201)
async def create_deal_with_deposit(data: DealWithDepositCreate):
    """
    Create a deal with initial deposit using cross-database Saga Pattern.

    This endpoint coordinates writes across MongoDB (deal) and MySQL (deposit transaction).
    If the MySQL write fails, the MongoDB deal is automatically rolled back (compensated).
    """
    # Validate ObjectId fields
    validate_object_id(str(data.property_id), "property_id")
    if data.participants:
        for field in ["buyer_id", "seller_id", "buyer_agent_id",
                      "seller_agent_id", "buyer_lawyer_id", "seller_lawyer_id"]:
            value = getattr(data.participants, field, None)
            if value:
                validate_object_id(str(value), field)

    # ── Validate property exists and is available ──
    db = get_database()
    prop = await db.properties.find_one({"_id": ObjectId(str(data.property_id))})
    if not prop:
        raise HTTPException(status_code=400, detail="Property not found")
    if prop.get("status") == "sold":
        raise HTTPException(
            status_code=400,
            detail="Cannot create deal: this property is already sold."
        )

    # ── Check no active deals on this property ──
    active_statuses = ["draft", "submitted", "conditional", "firm", "closing"]
    active_deal_count = await db.deals.count_documents({
        "property_id": ObjectId(str(data.property_id)),
        "status": {"$in": active_statuses}
    })
    if active_deal_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot create deal: this property already has {active_deal_count} active deal(s). "
                   f"Complete or cancel existing deals first."
        )

    # ── Validate deposit amount <= offer price ──
    if data.deposit_amount > data.offer_price:
        raise HTTPException(
            status_code=400,
            detail=f"Deposit amount cannot exceed offer price."
        )

    saga = DealDepositSaga()
    try:
        result = await saga.execute(data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cross-database saga failed: {str(e)}"
        )


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
    try:
        deal = await service.update_condition(deal_id, condition_id, update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not deal:
        raise HTTPException(status_code=404, detail="Deal or condition not found")
    return deal


@router.delete("/{deal_id}", status_code=204)
async def delete_deal(deal_id: str):
    """Delete deal (only if in draft status and no linked transactions)"""
    validate_object_id(deal_id, "deal_id")

    # Cross-database integrity check: verify no transactions exist in MySQL for this deal
    async with async_session_factory() as session:
        result = await session.execute(
            select(func.count(Transaction.id)).where(Transaction.deal_id == deal_id)
        )
        txn_count = result.scalar()
        if txn_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete deal: {txn_count} financial transaction(s) are linked to this deal in MySQL. "
                       f"Delete the associated transactions first to maintain cross-database consistency."
            )

    service = DealService()
    deleted = await service.delete_deal(deal_id)
    if not deleted:
        raise HTTPException(
            status_code=400,
            detail="Deal not found or cannot be deleted (only draft deals can be deleted)"
        )
