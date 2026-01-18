from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import get_settings

settings = get_settings()

class MongoDB:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

mongodb = MongoDB()

async def connect_mongodb():
    mongodb.client = AsyncIOMotorClient(settings.mongodb_url)
    mongodb.db = mongodb.client[settings.mongodb_database]
    print("Connected to MongoDB")

async def close_mongodb():
    if mongodb.client:
        mongodb.client.close()
        print("MongoDB connection closed")

def get_database() -> AsyncIOMotorDatabase:
    return mongodb.db

def get_users_collection():
    return mongodb.db.users

def get_properties_collection():
    return mongodb.db.properties

def get_deals_collection():
    return mongodb.db.deals
