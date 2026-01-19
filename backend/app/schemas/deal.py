from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from app.core.types import PyObjectId


class DealStatus(str, Enum):
    draft = "draft"
    submitted = "submitted"
    conditional = "conditional"
    firm = "firm"
    closing = "closing"
    completed = "completed"
    cancelled = "cancelled"
    expired = "expired"


class ConditionStatus(str, Enum):
    pending = "pending"
    satisfied = "satisfied"
    waived = "waived"
    failed = "failed"


class ConditionType(str, Enum):
    financing = "financing"
    inspection = "inspection"
    appraisal = "appraisal"
    sale_of_property = "sale_of_property"
    other = "other"


class ParticipantRefs(BaseModel):
    buyer_id: Optional[PyObjectId] = None
    seller_id: Optional[PyObjectId] = None
    buyer_agent_id: Optional[PyObjectId] = None
    seller_agent_id: Optional[PyObjectId] = None
    buyer_lawyer_id: Optional[PyObjectId] = None
    seller_lawyer_id: Optional[PyObjectId] = None


class ConditionSchema(BaseModel):
    type: ConditionType
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: ConditionStatus = ConditionStatus.pending
    satisfied_at: Optional[datetime] = None


class ConditionCreate(BaseModel):
    type: ConditionType
    description: Optional[str] = None
    deadline: Optional[datetime] = None


class ConditionUpdate(BaseModel):
    status: ConditionStatus
    description: Optional[str] = None


class StatusHistoryEntry(BaseModel):
    status: DealStatus
    timestamp: datetime
    note: Optional[str] = None


class DealCreate(BaseModel):
    property_id: PyObjectId
    offer_price: float = Field(gt=0)
    participants: ParticipantRefs
    closing_date: Optional[datetime] = None
    conditions: List[ConditionCreate] = []
    notes: Optional[str] = None


class DealUpdate(BaseModel):
    offer_price: Optional[float] = Field(default=None, gt=0)
    closing_date: Optional[datetime] = None
    notes: Optional[str] = None


class DealStatusUpdate(BaseModel):
    status: DealStatus
    note: Optional[str] = None


class DealResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    property_id: PyObjectId
    offer_price: float
    status: DealStatus
    participants_snapshot: Dict[str, Any]
    participant_refs: Dict[str, str]
    conditions: List[Dict[str, Any]]
    closing_date: Optional[datetime] = None
    notes: Optional[str] = None
    status_history: List[Dict[str, Any]]
    snapshot_timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True


class DealListResponse(BaseModel):
    deals: list[DealResponse]
    total: int
    page: int
    page_size: int
