from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.models.transaction import (
    Transaction, TrustAccount, AuditLog,
    TransactionTypeEnum, TransactionStatusEnum, AccountStatusEnum
)
from app.schemas.transaction import (
    TransactionCreate, TransactionResponse,
    TrustAccountCreate, TrustAccountUpdate, TrustAccountResponse,
    AuditLogResponse
)

logger = logging.getLogger(__name__)


class TransactionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transaction(
        self, transaction_data: TransactionCreate
    ) -> TransactionResponse:
        """Create a new financial transaction"""
        transaction = Transaction(
            deal_id=transaction_data.deal_id,
            amount=Decimal(str(transaction_data.amount)),
            transaction_type=TransactionTypeEnum(transaction_data.transaction_type.value),
            status=TransactionStatusEnum.completed,
            from_account=transaction_data.from_account,
            to_account=transaction_data.to_account,
            description=transaction_data.description
        )

        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)

        # Create audit log
        await self._create_audit_log(
            action="create",
            entity_type="transaction",
            entity_id=str(transaction.id),
            new_value={
                "deal_id": transaction.deal_id,
                "amount": float(transaction.amount),
                "type": transaction.transaction_type.value
            }
        )

        logger.info(f"Transaction {transaction.id} created for deal {transaction.deal_id}")
        return self._to_response(transaction)

    async def get_transaction(self, transaction_id: int) -> Optional[TransactionResponse]:
        """Get transaction by ID"""
        result = await self.session.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        transaction = result.scalar_one_or_none()
        if transaction:
            return self._to_response(transaction)
        return None

    async def get_transactions(
        self,
        page: int = 1,
        page_size: int = 10,
        deal_id: Optional[str] = None,
        transaction_type: Optional[str] = None
    ) -> tuple[List[TransactionResponse], int]:
        """Get paginated list of transactions"""
        query = select(Transaction)

        if deal_id:
            query = query.where(Transaction.deal_id == deal_id)
        if transaction_type:
            query = query.where(Transaction.transaction_type == TransactionTypeEnum(transaction_type))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        offset = (page - 1) * page_size
        query = query.order_by(Transaction.created_at.desc()).offset(offset).limit(page_size)

        result = await self.session.execute(query)
        transactions = result.scalars().all()

        return [self._to_response(t) for t in transactions], total

    async def get_deal_transactions(self, deal_id: str) -> List[TransactionResponse]:
        """Get all transactions for a deal"""
        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.deal_id == deal_id)
            .order_by(Transaction.created_at.desc())
        )
        transactions = result.scalars().all()
        return [self._to_response(t) for t in transactions]

    def _to_response(self, transaction: Transaction) -> TransactionResponse:
        return TransactionResponse(
            id=transaction.id,
            deal_id=transaction.deal_id,
            amount=float(transaction.amount),
            transaction_type=transaction.transaction_type.value,
            status=transaction.status.value,
            from_account=transaction.from_account,
            to_account=transaction.to_account,
            description=transaction.description,
            created_at=transaction.created_at
        )

    async def _create_audit_log(
        self,
        action: str,
        entity_type: str,
        entity_id: str = None,
        old_value: dict = None,
        new_value: dict = None,
        user_id: str = None
    ):
        """Create an audit log entry"""
        audit = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value
        )
        self.session.add(audit)
        await self.session.commit()


class TrustAccountService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_account(
        self, account_data: TrustAccountCreate
    ) -> TrustAccountResponse:
        """Create a new trust account"""
        # Check if account number already exists
        result = await self.session.execute(
            select(TrustAccount).where(TrustAccount.account_number == account_data.account_number)
        )
        if result.scalar_one_or_none():
            raise ValueError("Account number already exists")

        account = TrustAccount(
            account_number=account_data.account_number,
            holder_name=account_data.holder_name,
            balance=Decimal(str(account_data.initial_balance)),
            status=AccountStatusEnum.active
        )

        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)

        logger.info(f"Trust account {account.account_number} created")
        return self._to_response(account)

    async def get_account(self, account_id: int) -> Optional[TrustAccountResponse]:
        """Get trust account by ID"""
        result = await self.session.execute(
            select(TrustAccount).where(TrustAccount.id == account_id)
        )
        account = result.scalar_one_or_none()
        if account:
            return self._to_response(account)
        return None

    async def get_account_by_number(self, account_number: str) -> Optional[TrustAccountResponse]:
        """Get trust account by account number"""
        result = await self.session.execute(
            select(TrustAccount).where(TrustAccount.account_number == account_number)
        )
        account = result.scalar_one_or_none()
        if account:
            return self._to_response(account)
        return None

    async def get_accounts(self) -> tuple[List[TrustAccountResponse], int]:
        """Get all trust accounts"""
        result = await self.session.execute(
            select(TrustAccount).order_by(TrustAccount.created_at.desc())
        )
        accounts = result.scalars().all()
        return [self._to_response(a) for a in accounts], len(accounts)

    async def update_account(
        self, account_id: int, account_data: TrustAccountUpdate
    ) -> Optional[TrustAccountResponse]:
        """Update trust account"""
        result = await self.session.execute(
            select(TrustAccount).where(TrustAccount.id == account_id)
        )
        account = result.scalar_one_or_none()

        if not account:
            return None

        if account_data.holder_name:
            account.holder_name = account_data.holder_name
        if account_data.status:
            account.status = AccountStatusEnum(account_data.status.value)

        await self.session.commit()
        await self.session.refresh(account)

        return self._to_response(account)

    async def update_balance(
        self, account_id: int, amount: float, operation: str = "add"
    ) -> Optional[TrustAccountResponse]:
        """Update account balance (add or subtract)"""
        result = await self.session.execute(
            select(TrustAccount).where(TrustAccount.id == account_id)
        )
        account = result.scalar_one_or_none()

        if not account:
            return None

        if account.status != AccountStatusEnum.active:
            raise ValueError("Cannot update balance on non-active account")

        amount_decimal = Decimal(str(amount))
        if operation == "add":
            account.balance += amount_decimal
        elif operation == "subtract":
            if account.balance < amount_decimal:
                raise ValueError("Insufficient balance")
            account.balance -= amount_decimal

        await self.session.commit()
        await self.session.refresh(account)

        return self._to_response(account)

    def _to_response(self, account: TrustAccount) -> TrustAccountResponse:
        return TrustAccountResponse(
            id=account.id,
            account_number=account.account_number,
            holder_name=account.holder_name,
            balance=float(account.balance),
            status=account.status.value,
            created_at=account.created_at,
            updated_at=account.updated_at
        )


class AuditLogService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_logs(
        self,
        page: int = 1,
        page_size: int = 50,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None
    ) -> tuple[List[AuditLogResponse], int]:
        """Get audit logs with filters"""
        query = select(AuditLog)

        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type)
        if entity_id:
            query = query.where(AuditLog.entity_id == entity_id)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        offset = (page - 1) * page_size
        query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(page_size)

        result = await self.session.execute(query)
        logs = result.scalars().all()

        return [self._to_response(log) for log in logs], total

    def _to_response(self, log: AuditLog) -> AuditLogResponse:
        return AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            old_value=log.old_value,
            new_value=log.new_value,
            ip_address=log.ip_address,
            created_at=log.created_at
        )
