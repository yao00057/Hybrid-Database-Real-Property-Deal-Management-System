from datetime import datetime
from typing import Optional, List
from bson import ObjectId

from app.database.mongodb import get_database
from app.schemas.property import (
    PropertyCreate, PropertyUpdate, PropertyResponse, PropertyType, PropertyStatus
)


class PropertyService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.properties

    def _doc_to_response(self, doc: dict) -> PropertyResponse:
        doc["_id"] = str(doc["_id"])
        return PropertyResponse(**doc)

    async def create_property(self, property_data: PropertyCreate) -> PropertyResponse:
        """Create a new property listing"""
        property_doc = {
            "type": property_data.type.value,
            "address": property_data.address.model_dump(),
            "listing_price": property_data.listing_price,
            "status": PropertyStatus.active.value,
            "attributes": property_data.attributes,
            "description": property_data.description,
            "images": property_data.images,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = await self.collection.insert_one(property_doc)
        property_doc["_id"] = result.inserted_id
        return self._doc_to_response(property_doc)

    async def get_property(self, property_id: str) -> Optional[PropertyResponse]:
        """Get property by ID"""
        if not ObjectId.is_valid(property_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(property_id)})
        if doc:
            return self._doc_to_response(doc)
        return None

    async def get_properties(
        self,
        page: int = 1,
        page_size: int = 10,
        property_type: Optional[str] = None,
        status: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        city: Optional[str] = None
    ) -> tuple[List[PropertyResponse], int]:
        """Get paginated list of properties with filters"""
        query = {}
        
        if property_type:
            query["type"] = property_type
        if status:
            query["status"] = status
        if min_price is not None:
            query["listing_price"] = query.get("listing_price", {})
            query["listing_price"]["$gte"] = min_price
        if max_price is not None:
            query["listing_price"] = query.get("listing_price", {})
            query["listing_price"]["$lte"] = max_price
        if city:
            query["address.city"] = {"$regex": city, "$options": "i"}

        total = await self.collection.count_documents(query)
        skip = (page - 1) * page_size

        cursor = self.collection.find(query).skip(skip).limit(page_size).sort("created_at", -1)
        properties = []
        async for doc in cursor:
            properties.append(self._doc_to_response(doc))

        return properties, total

    async def update_property(
        self, property_id: str, property_data: PropertyUpdate
    ) -> Optional[PropertyResponse]:
        """Update property"""
        if not ObjectId.is_valid(property_id):
            return None

        update_doc = {"updated_at": datetime.utcnow()}

        if property_data.listing_price is not None:
            update_doc["listing_price"] = property_data.listing_price
        if property_data.status is not None:
            update_doc["status"] = property_data.status.value
        if property_data.attributes is not None:
            update_doc["attributes"] = property_data.attributes
        if property_data.description is not None:
            update_doc["description"] = property_data.description
        if property_data.images is not None:
            update_doc["images"] = property_data.images

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(property_id)},
            {"$set": update_doc},
            return_document=True
        )

        if result:
            return self._doc_to_response(result)
        return None

    async def delete_property(self, property_id: str) -> bool:
        """Delete property"""
        if not ObjectId.is_valid(property_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(property_id)})
        return result.deleted_count > 0

    async def get_active_properties(self) -> List[PropertyResponse]:
        """Get all active property listings"""
        cursor = self.collection.find({"status": "active"})
        properties = []
        async for doc in cursor:
            properties.append(self._doc_to_response(doc))
        return properties
