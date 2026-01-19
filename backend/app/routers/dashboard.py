from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database.mongodb import get_database
from app.database.mysql import get_session
from app.models.transaction import Transaction
from app.core.security import get_current_user, TokenData

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


class DashboardStats(BaseModel):
    total_users: int
    total_properties: int
    active_properties: int
    total_deals: int
    deals_by_status: Dict[str, int]
    total_transactions: int
    total_transaction_amount: float
    recent_activity: List[Dict[str, Any]]


class PropertyStats(BaseModel):
    total: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    avg_price: float
    price_range: Dict[str, float]


class DealStats(BaseModel):
    total: int
    by_status: Dict[str, int]
    avg_offer_price: float
    completed_this_month: int
    pending_conditions: int


class TransactionStats(BaseModel):
    total_count: int
    total_amount: float
    by_type: Dict[str, float]
    this_month_amount: float


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    session: AsyncSession = Depends(get_session),
    _current_user: TokenData = Depends(get_current_user)
):
    """Get overall dashboard statistics"""
    db = get_database()

    # MongoDB stats
    total_users = await db.users.count_documents({})
    total_properties = await db.properties.count_documents({})
    active_properties = await db.properties.count_documents({"status": "active"})
    total_deals = await db.deals.count_documents({})

    # Deals by status
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    deals_by_status = {}
    async for doc in db.deals.aggregate(pipeline):
        deals_by_status[doc["_id"]] = doc["count"]

    # MySQL transaction stats
    result = await session.execute(
        select(func.count(Transaction.id), func.sum(Transaction.amount))
    )
    row = result.one()
    total_transactions = row[0] or 0
    total_transaction_amount = float(row[1] or 0)

    # Recent activity (last 10 deals)
    recent_deals = []
    cursor = db.deals.find().sort("created_at", -1).limit(10)
    async for deal in cursor:
        recent_deals.append({
            "id": str(deal["_id"]),
            "type": "deal",
            "status": deal["status"],
            "amount": deal["offer_price"],
            "created_at": deal["created_at"].isoformat()
        })

    return DashboardStats(
        total_users=total_users,
        total_properties=total_properties,
        active_properties=active_properties,
        total_deals=total_deals,
        deals_by_status=deals_by_status,
        total_transactions=total_transactions,
        total_transaction_amount=total_transaction_amount,
        recent_activity=recent_deals
    )


@router.get("/properties", response_model=PropertyStats)
async def get_property_stats(_current_user: TokenData = Depends(get_current_user)):
    """Get property statistics"""
    db = get_database()

    total = await db.properties.count_documents({})

    # By type
    type_pipeline = [{"$group": {"_id": "$type", "count": {"$sum": 1}}}]
    by_type = {}
    async for doc in db.properties.aggregate(type_pipeline):
        by_type[doc["_id"]] = doc["count"]

    # By status
    status_pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
    by_status = {}
    async for doc in db.properties.aggregate(status_pipeline):
        by_status[doc["_id"]] = doc["count"]

    # Price stats
    price_pipeline = [
        {"$group": {
            "_id": None,
            "avg_price": {"$avg": "$listing_price"},
            "min_price": {"$min": "$listing_price"},
            "max_price": {"$max": "$listing_price"}
        }}
    ]
    avg_price = 0
    price_range = {"min": 0, "max": 0}
    async for doc in db.properties.aggregate(price_pipeline):
        avg_price = doc.get("avg_price", 0) or 0
        price_range = {
            "min": doc.get("min_price", 0) or 0,
            "max": doc.get("max_price", 0) or 0
        }

    return PropertyStats(
        total=total,
        by_type=by_type,
        by_status=by_status,
        avg_price=avg_price,
        price_range=price_range
    )


@router.get("/deals", response_model=DealStats)
async def get_deal_stats(_current_user: TokenData = Depends(get_current_user)):
    """Get deal statistics"""
    db = get_database()

    total = await db.deals.count_documents({})

    # By status
    status_pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
    by_status = {}
    async for doc in db.deals.aggregate(status_pipeline):
        by_status[doc["_id"]] = doc["count"]

    # Average offer price
    price_pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$offer_price"}}}]
    avg_offer_price = 0
    async for doc in db.deals.aggregate(price_pipeline):
        avg_offer_price = doc.get("avg", 0) or 0

    # Completed this month
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    completed_this_month = await db.deals.count_documents({
        "status": "completed",
        "updated_at": {"$gte": month_start}
    })

    # Pending conditions count
    pending_pipeline = [
        {"$unwind": "$conditions"},
        {"$match": {"conditions.status": "pending"}},
        {"$count": "total"}
    ]
    pending_conditions = 0
    async for doc in db.deals.aggregate(pending_pipeline):
        pending_conditions = doc.get("total", 0)

    return DealStats(
        total=total,
        by_status=by_status,
        avg_offer_price=avg_offer_price,
        completed_this_month=completed_this_month,
        pending_conditions=pending_conditions
    )


@router.get("/transactions", response_model=TransactionStats)
async def get_transaction_stats(
    session: AsyncSession = Depends(get_session),
    _current_user: TokenData = Depends(get_current_user)
):
    """Get transaction statistics"""
    from app.models.transaction import TransactionTypeEnum

    # Total count and amount
    result = await session.execute(
        select(func.count(Transaction.id), func.sum(Transaction.amount))
    )
    row = result.one()
    total_count = row[0] or 0
    total_amount = float(row[1] or 0)

    # By type
    type_result = await session.execute(
        select(Transaction.transaction_type, func.sum(Transaction.amount))
        .group_by(Transaction.transaction_type)
    )
    by_type = {}
    for row in type_result:
        by_type[row[0].value] = float(row[1] or 0)

    # This month
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_result = await session.execute(
        select(func.sum(Transaction.amount))
        .where(Transaction.created_at >= month_start)
    )
    this_month_amount = float(month_result.scalar() or 0)

    return TransactionStats(
        total_count=total_count,
        total_amount=total_amount,
        by_type=by_type,
        this_month_amount=this_month_amount
    )
