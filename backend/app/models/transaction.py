from sqlalchemy import Column, Integer, String, Numeric, Enum, Text, TIMESTAMP, JSON, BigInteger
from sqlalchemy.sql import func
from app.database.mysql import Base
import enum


class TransactionTypeEnum(enum.Enum):
    deposit = "deposit"
    payment = "payment"
    refund = "refund"
    commission = "commission"
    adjustment = "adjustment"


class TransactionStatusEnum(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    reversed = "reversed"


class AccountStatusEnum(enum.Enum):
    active = "active"
    frozen = "frozen"
    closed = "closed"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    deal_id = Column(String(50), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    transaction_type = Column(
        Enum(TransactionTypeEnum),
        nullable=False
    )
    status = Column(
        Enum(TransactionStatusEnum),
        default=TransactionStatusEnum.completed
    )
    from_account = Column(String(100), nullable=True)
    to_account = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class TrustAccount(Base):
    __tablename__ = "trust_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_number = Column(String(50), unique=True, nullable=False)
    holder_name = Column(String(100), nullable=False)
    balance = Column(Numeric(14, 2), default=0.00)
    status = Column(
        Enum(AccountStatusEnum),
        default=AccountStatusEnum.active
    )
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=True, index=True)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(50), nullable=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
