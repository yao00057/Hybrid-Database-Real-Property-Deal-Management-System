"""
Cross-Database Saga Service

Coordinates writes across MongoDB and MySQL using the Saga Pattern.
When a deal with a deposit is created:
  1. Write the deal document to MongoDB
  2. Record the deposit transaction in MySQL (with ACID trust account update)
  3. If step 2 fails, compensate by deleting the deal from MongoDB

This ensures data consistency across the two database systems without
requiring distributed transactions.

Note: Step 2 uses raw aiomysql instead of SQLAlchemy ORM to avoid
greenlet context conflicts between Motor (MongoDB async) and
SQLAlchemy's greenlet-based async session.
"""

import json
import logging
from datetime import datetime
from bson import ObjectId
import aiomysql

from app.database.mongodb import get_database
from app.core.config import get_settings
from app.services.deal_service import DealService
from app.schemas.deal import (
    DealCreate, DealResponse, DealWithDepositCreate, ParticipantRefs
)

logger = logging.getLogger(__name__)


class DealDepositSaga:
    """
    Saga coordinator for cross-database deal + deposit creation.

    Execution flow:
      Step 1: Create deal in MongoDB (via DealService)
      Step 2: Create deposit in MySQL with ACID transaction (raw aiomysql)

    Compensation:
      If Step 2 fails, delete the MongoDB deal to prevent orphaned data.
    """

    def __init__(self):
        self.deal_service = DealService()

    async def execute(self, data: DealWithDepositCreate) -> dict:
        """
        Execute the saga: create deal in MongoDB, then deposit in MySQL.
        Returns both the deal and transaction responses.
        Raises on failure after compensating any partial writes.
        """
        deal_response: DealResponse = None

        try:
            # ── Step 1: Create deal document in MongoDB ──
            deal_create = DealCreate(
                property_id=data.property_id,
                offer_price=data.offer_price,
                participants=data.participants,
                closing_date=data.closing_date,
                conditions=data.conditions,
                notes=data.notes
            )
            deal_response = await self.deal_service.create_deal(deal_create)
            deal_id = str(deal_response.id)

            logger.info(f"Saga Step 1 complete: deal {deal_id} created in MongoDB")

            # ── Step 2: Create deposit transaction in MySQL (ACID) ──
            # Uses raw aiomysql to avoid greenlet context conflict with Motor
            tx_result = await self._create_deposit_mysql(
                deal_id=deal_id,
                amount=data.deposit_amount,
                to_account=data.trust_account_number,
                description=data.deposit_description or f"Initial deposit for deal {deal_id}"
            )

            logger.info(
                f"Saga Step 2 complete: transaction {tx_result['id']} created in MySQL "
                f"for deal {deal_id}"
            )

            return {
                "deal": deal_response,
                "transaction": tx_result,
                "message": "Deal and deposit created successfully (cross-database saga)"
            }

        except Exception as e:
            # ── Compensation: undo MongoDB write if MySQL failed ──
            if deal_response is not None:
                try:
                    await self._compensate_deal(str(deal_response.id))
                    logger.error(
                        f"Saga failed at Step 2 for deal {deal_response.id}: {str(e)}. "
                        f"Compensation executed — MongoDB deal deleted."
                    )
                except Exception as comp_err:
                    logger.critical(
                        f"SAGA COMPENSATION FAILED for deal {deal_response.id}: {comp_err}. "
                        f"ORPHANED DEAL in MongoDB requires manual cleanup!"
                    )
            else:
                logger.error(f"Saga failed at Step 1: {str(e)}")

            raise e

    async def _create_deposit_mysql(
        self, deal_id: str, amount: float, to_account: str, description: str
    ) -> dict:
        """
        Create a deposit transaction in MySQL with ACID compliance.
        Uses raw aiomysql to avoid SQLAlchemy greenlet conflicts.

        Atomically:
        1. INSERT transaction record
        2. UPDATE trust account balance (with SELECT ... FOR UPDATE row lock)
        3. INSERT audit log entry
        All in a single MySQL transaction — commits together or rolls back entirely.
        """
        settings = get_settings()
        conn = await aiomysql.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            db=settings.mysql_database,
            autocommit=False
        )

        try:
            async with conn.cursor() as cur:
                # 1. Insert transaction record
                await cur.execute(
                    "INSERT INTO transactions "
                    "(deal_id, amount, transaction_type, status, to_account, description, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (deal_id, amount, 'deposit', 'completed', to_account,
                     description, datetime.utcnow())
                )
                txn_id = cur.lastrowid

                # 2. Update trust account balance with row-level lock
                await cur.execute(
                    "SELECT id, balance FROM trust_accounts "
                    "WHERE account_number = %s FOR UPDATE",
                    (to_account,)
                )
                row = await cur.fetchone()
                if not row:
                    raise ValueError(
                        f"Trust account '{to_account}' not found. "
                        f"Please select a valid trust account."
                    )
                old_balance = float(row[1])
                new_balance = old_balance + amount
                await cur.execute(
                    "UPDATE trust_accounts SET balance = %s WHERE id = %s",
                    (new_balance, row[0])
                )
                logger.info(
                    f"Trust account {to_account} balance: "
                    f"{old_balance} -> {new_balance}"
                )

                # 3. Insert audit log
                audit_value = json.dumps({
                    "deal_id": deal_id,
                    "amount": amount,
                    "type": "deposit",
                    "to_account": to_account
                })
                await cur.execute(
                    "INSERT INTO audit_logs "
                    "(action, entity_type, entity_id, new_value, created_at) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    ('create', 'transaction', str(txn_id), audit_value,
                     datetime.utcnow())
                )

                # COMMIT: all 3 operations succeed atomically
                await conn.commit()

            return {
                "id": txn_id,
                "deal_id": deal_id,
                "amount": amount,
                "transaction_type": "deposit",
                "status": "completed",
                "to_account": to_account,
                "from_account": None,
                "description": description,
                "created_at": datetime.utcnow().isoformat()
            }

        except Exception:
            # ROLLBACK: undo all MySQL changes
            await conn.rollback()
            raise

        finally:
            conn.close()

    async def _compensate_deal(self, deal_id: str):
        """
        Compensation action: remove the deal from MongoDB.
        Uses direct delete (bypasses DealService.delete_deal which only allows draft deletion).
        """
        db = get_database()
        result = await db.deals.delete_one({"_id": ObjectId(deal_id)})

        if result.deleted_count > 0:
            logger.warning(f"Saga compensation: deleted deal {deal_id} from MongoDB")
        else:
            logger.error(f"Saga compensation: failed to delete deal {deal_id} — not found")
