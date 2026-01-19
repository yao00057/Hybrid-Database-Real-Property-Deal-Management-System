from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from passlib.context import CryptContext

from app.database.mongodb import get_database
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.types import PyObjectId

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.users

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def _doc_to_response(self, doc: dict) -> UserResponse:
        doc["_id"] = str(doc["_id"])
        return UserResponse(**doc)

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        # Check if email already exists
        existing = await self.collection.find_one({"email": user_data.email})
        if existing:
            raise ValueError("Email already registered")

        user_doc = {
            "email": user_data.email,
            "password_hash": self._hash_password(user_data.password),
            "role": user_data.role.value,
            "profile": user_data.profile.model_dump(),
            "role_specific": user_data.role_specific or {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = await self.collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        return self._doc_to_response(user_doc)

    async def get_user(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        if not ObjectId.is_valid(user_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        if doc:
            return self._doc_to_response(doc)
        return None

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email (includes password hash for auth)"""
        return await self.collection.find_one({"email": email})

    async def get_users(
        self, 
        page: int = 1, 
        page_size: int = 10,
        role: Optional[str] = None
    ) -> tuple[List[UserResponse], int]:
        """Get paginated list of users"""
        query = {}
        if role:
            query["role"] = role

        total = await self.collection.count_documents(query)
        skip = (page - 1) * page_size

        cursor = self.collection.find(query).skip(skip).limit(page_size).sort("created_at", -1)
        users = []
        async for doc in cursor:
            users.append(self._doc_to_response(doc))

        return users, total

    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """Update user"""
        if not ObjectId.is_valid(user_id):
            return None

        update_doc = {"updated_at": datetime.utcnow()}
        
        if user_data.email:
            # Check if new email is already taken by another user
            existing = await self.collection.find_one({
                "email": user_data.email,
                "_id": {"$ne": ObjectId(user_id)}
            })
            if existing:
                raise ValueError("Email already in use")
            update_doc["email"] = user_data.email

        if user_data.profile:
            update_doc["profile"] = user_data.profile.model_dump()

        if user_data.role_specific is not None:
            update_doc["role_specific"] = user_data.role_specific

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": update_doc},
            return_document=True
        )

        if result:
            return self._doc_to_response(result)
        return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        if not ObjectId.is_valid(user_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    async def get_users_by_role(self, role: str) -> List[UserResponse]:
        """Get all users with a specific role"""
        cursor = self.collection.find({"role": role})
        users = []
        async for doc in cursor:
            users.append(self._doc_to_response(doc))
        return users
