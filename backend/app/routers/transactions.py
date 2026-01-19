from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.mysql import get_session
from app.schemas.transaction import (
    TransactionCreate, TransactionResponse, TransactionListResponse,
    TrustAccountCreate, TrustAccountUpdate, TrustAccountResponse, TrustAccountListResponse,
    TransactionType, AuditLogResponse
)
from app.services.transaction_service import (
    TransactionService, TrustAccountService, AuditLogService
)

router = APIRouter(prefix="/api", tags=["transactions"])


# Transaction endpoints
@router.post("/transactions", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    transaction_data: TransactionCreate,
    session: AsyncSession = Depends(get_session)
):
    """Record a new financial transaction"""
    service = TransactionService(session)
    return await service.create_transaction(transaction_data)


@router.get("/transactions", response_model=TransactionListResponse)
async def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    deal_id: Optional[str] = None,
    type: Optional[TransactionType] = None,
    session: AsyncSession = Depends(get_session)
):
    """Get paginated list of transactions"""
    service = TransactionService(session)
    type_value = type.value if type else None
    transactions, total = await service.get_transactions(page, page_size, deal_id, type_value)
    return TransactionListResponse(
        transactions=transactions,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get transaction by ID"""
    service = TransactionService(session)
    transaction = await service.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.get("/deals/{deal_id}/transactions", response_model=list[TransactionResponse])
async def get_deal_transactions(
    deal_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get all transactions for a deal"""
    service = TransactionService(session)
    return await service.get_deal_transactions(deal_id)


# Trust Account endpoints
@router.post("/accounts", response_model=TrustAccountResponse, status_code=201)
async def create_trust_account(
    account_data: TrustAccountCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new trust account"""
    service = TrustAccountService(session)
    try:
        return await service.create_account(account_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/accounts", response_model=TrustAccountListResponse)
async def list_trust_accounts(
    session: AsyncSession = Depends(get_session)
):
    """Get all trust accounts"""
    service = TrustAccountService(session)
    accounts, total = await service.get_accounts()
    return TrustAccountListResponse(accounts=accounts, total=total)


@router.get("/accounts/{account_id}", response_model=TrustAccountResponse)
async def get_trust_account(
    account_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get trust account by ID"""
    service = TrustAccountService(session)
    account = await service.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.put("/accounts/{account_id}", response_model=TrustAccountResponse)
async def update_trust_account(
    account_id: int,
    account_data: TrustAccountUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update trust account"""
    service = TrustAccountService(session)
    account = await service.update_account(account_id, account_data)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


# Audit Log endpoints
@router.get("/audit-logs", response_model=list[AuditLogResponse])
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    """Get audit logs"""
    service = AuditLogService(session)
    logs, _ = await service.get_logs(page, page_size, entity_type, entity_id)
    return logs
