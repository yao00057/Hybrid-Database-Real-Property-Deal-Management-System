from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    deposit = "deposit"
    payment = "payment"
    refund = "refund"
    commission = "commission"
    adjustment = "adjustment"


class TransactionStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    reversed = "reversed"


class AccountStatus(str, Enum):
    active = "active"
    frozen = "frozen"
    closed = "closed"


class TransactionCreate(BaseModel):
    deal_id: str
    amount: float = Field(gt=0)
    transaction_type: TransactionType
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    description: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    deal_id: str
    amount: float
    transaction_type: TransactionType
    status: TransactionStatus
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int
    page: int
    page_size: int


class TrustAccountCreate(BaseModel):
    account_number: str = Field(min_length=5, max_length=50)
    holder_name: str = Field(min_length=1, max_length=100)
    initial_balance: float = Field(default=0, ge=0)


class TrustAccountUpdate(BaseModel):
    holder_name: Optional[str] = None
    status: Optional[AccountStatus] = None


class TrustAccountResponse(BaseModel):
    id: int
    account_number: str
    holder_name: str
    balance: float
    status: AccountStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrustAccountListResponse(BaseModel):
    accounts: List[TrustAccountResponse]
    total: int


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    old_value: Optional[dict] = None
    new_value: Optional[dict] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
