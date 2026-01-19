from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
import logging

from app.database.mongodb import get_database
from app.schemas.deal import (
    DealCreate, DealUpdate, DealResponse, DealStatus,
    DealStatusUpdate, ConditionCreate, ConditionUpdate, ConditionStatus
)

logger = logging.getLogger(__name__)


# Valid status transitions
VALID_TRANSITIONS = {
    DealStatus.draft: [DealStatus.submitted, DealStatus.cancelled],
    DealStatus.submitted: [DealStatus.conditional, DealStatus.firm, DealStatus.cancelled, DealStatus.expired],
    DealStatus.conditional: [DealStatus.firm, DealStatus.cancelled, DealStatus.expired],
    DealStatus.firm: [DealStatus.closing, DealStatus.cancelled],
    DealStatus.closing: [DealStatus.completed, DealStatus.cancelled],
    DealStatus.completed: [],
    DealStatus.cancelled: [],
    DealStatus.expired: []
}


class DealService:
    def __init__(self):
        self.db = get_database()
        self.deals = self.db.deals
        self.users = self.db.users
        self.properties = self.db.properties

    def _doc_to_response(self, doc: dict) -> DealResponse:
        doc["_id"] = str(doc["_id"])
        doc["property_id"] = str(doc["property_id"])
        return DealResponse(**doc)

    async def _create_participants_snapshot(
        self, participant_refs: Dict[str, str]
    ) -> Dict[str, Any]:
        snapshot = {}

        for role, user_id in participant_refs.items():
            if not user_id:
                continue
            user = await self.users.find_one({"_id": ObjectId(user_id)})

            if user:
                snapshot[role] = {
                    "user_id": str(user["_id"]),
                    "name": user.get("profile", {}).get("name", "Unknown"),
                    "email": user.get("email", ""),
                    "phone": user.get("profile", {}).get("phone", ""),
                    "role_type": user.get("role", ""),
                    "license_number": user.get("role_specific", {}).get("license_number"),
                    "brokerage": user.get("role_specific", {}).get("brokerage"),
                    "law_firm": user.get("role_specific", {}).get("law_firm"),
                }
            else:
                logger.warning(f"User {user_id} not found for role {role}")
                snapshot[role] = {
                    "user_id": user_id,
                    "name": "Unknown",
                    "error": "User not found at snapshot time"
                }

        return snapshot

    async def create_deal(self, deal_data: DealCreate) -> DealResponse:
        participant_refs = {}
        for field in ["buyer_id", "seller_id", "buyer_agent_id",
                      "seller_agent_id", "buyer_lawyer_id", "seller_lawyer_id"]:
            value = getattr(deal_data.participants, field, None)
            if value:
                participant_refs[field.replace("_id", "")] = str(value)

        participants_snapshot = await self._create_participants_snapshot(participant_refs)

        conditions = []
        for cond in deal_data.conditions:
            conditions.append({
                "id": str(ObjectId()),
                "type": cond.type.value,
                "description": cond.description,
                "deadline": cond.deadline,
                "status": ConditionStatus.pending.value,
                "created_at": datetime.utcnow()
            })

        deal_doc = {
            "property_id": ObjectId(str(deal_data.property_id)),
            "offer_price": deal_data.offer_price,
            "status": DealStatus.draft.value,
            "participants_snapshot": participants_snapshot,
            "participant_refs": participant_refs,
            "snapshot_timestamp": datetime.utcnow(),
            "conditions": conditions,
            "closing_date": deal_data.closing_date,
            "notes": deal_data.notes,
            "status_history": [
                {"status": DealStatus.draft.value, "timestamp": datetime.utcnow()}
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = await self.deals.insert_one(deal_doc)
        deal_doc["_id"] = result.inserted_id

        logger.info(f"Deal created with ID {result.inserted_id}")
        return self._doc_to_response(deal_doc)

    async def get_deal(self, deal_id: str) -> Optional[DealResponse]:
        if not ObjectId.is_valid(deal_id):
            return None
        doc = await self.deals.find_one({"_id": ObjectId(deal_id)})
        if doc:
            return self._doc_to_response(doc)
        return None

    async def get_deals(
        self,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        property_id: Optional[str] = None
    ) -> tuple[List[DealResponse], int]:
        query = {}
        if status:
            query["status"] = status
        if property_id and ObjectId.is_valid(property_id):
            query["property_id"] = ObjectId(property_id)

        total = await self.deals.count_documents(query)
        skip = (page - 1) * page_size

        cursor = self.deals.find(query).skip(skip).limit(page_size).sort("created_at", -1)
        deals = []
        async for doc in cursor:
            deals.append(self._doc_to_response(doc))

        return deals, total

    async def update_deal(self, deal_id: str, deal_data: DealUpdate) -> Optional[DealResponse]:
        if not ObjectId.is_valid(deal_id):
            return None

        update_doc = {"updated_at": datetime.utcnow()}

        if deal_data.offer_price is not None:
            update_doc["offer_price"] = deal_data.offer_price
        if deal_data.closing_date is not None:
            update_doc["closing_date"] = deal_data.closing_date
        if deal_data.notes is not None:
            update_doc["notes"] = deal_data.notes

        result = await self.deals.find_one_and_update(
            {"_id": ObjectId(deal_id)},
            {"$set": update_doc},
            return_document=True
        )

        if result:
            return self._doc_to_response(result)
        return None

    async def update_deal_status(
        self, deal_id: str, status_update: DealStatusUpdate
    ) -> Optional[DealResponse]:
        if not ObjectId.is_valid(deal_id):
            return None

        deal = await self.deals.find_one({"_id": ObjectId(deal_id)})
        if not deal:
            return None

        current_status = DealStatus(deal["status"])
        new_status = status_update.status

        if new_status not in VALID_TRANSITIONS.get(current_status, []):
            raise ValueError(
                f"Invalid status transition from {current_status.value} to {new_status.value}"
            )

        update_doc = {
            "status": new_status.value,
            "updated_at": datetime.utcnow()
        }

        history_entry = {
            "status": new_status.value,
            "timestamp": datetime.utcnow(),
            "note": status_update.note
        }

        result = await self.deals.find_one_and_update(
            {"_id": ObjectId(deal_id)},
            {
                "$set": update_doc,
                "$push": {"status_history": history_entry}
            },
            return_document=True
        )

        if result:
            if new_status == DealStatus.completed:
                await self.properties.update_one(
                    {"_id": deal["property_id"]},
                    {"$set": {"status": "sold", "updated_at": datetime.utcnow()}}
                )
            return self._doc_to_response(result)
        return None

    async def add_condition(
        self, deal_id: str, condition: ConditionCreate
    ) -> Optional[DealResponse]:
        if not ObjectId.is_valid(deal_id):
            return None

        condition_doc = {
            "id": str(ObjectId()),
            "type": condition.type.value,
            "description": condition.description,
            "deadline": condition.deadline,
            "status": ConditionStatus.pending.value,
            "created_at": datetime.utcnow()
        }

        result = await self.deals.find_one_and_update(
            {"_id": ObjectId(deal_id)},
            {
                "$push": {"conditions": condition_doc},
                "$set": {"updated_at": datetime.utcnow()}
            },
            return_document=True
        )

        if result:
            return self._doc_to_response(result)
        return None

    async def update_condition(
        self, deal_id: str, condition_id: str, update: ConditionUpdate
    ) -> Optional[DealResponse]:
        if not ObjectId.is_valid(deal_id):
            return None

        update_fields = {
            "conditions.$.status": update.status.value,
            "updated_at": datetime.utcnow()
        }

        if update.status == ConditionStatus.satisfied:
            update_fields["conditions.$.satisfied_at"] = datetime.utcnow()

        if update.description:
            update_fields["conditions.$.description"] = update.description

        result = await self.deals.find_one_and_update(
            {"_id": ObjectId(deal_id), "conditions.id": condition_id},
            {"$set": update_fields},
            return_document=True
        )

        if result:
            return self._doc_to_response(result)
        return None

    async def delete_deal(self, deal_id: str) -> bool:
        if not ObjectId.is_valid(deal_id):
            return False
        result = await self.deals.delete_one({
            "_id": ObjectId(deal_id),
            "status": DealStatus.draft.value
        })
        return result.deleted_count > 0
