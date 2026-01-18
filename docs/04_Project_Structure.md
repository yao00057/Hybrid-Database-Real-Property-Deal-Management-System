# Project Directory Structure

## Real Property Deal Management System

---

## Complete Project Tree

```
real-estate-system/                          # Project Root
│
├── docker-compose.yml                       # Container orchestration
├── .env                                     # Root environment variables
├── .gitignore                               # Git ignore rules
├── README.md                                # Project documentation
│
├── init-scripts/                            # Database initialization
│   └── mysql/
│       └── 01-schema.sql                    # MySQL table definitions
│
├── backend/                                 # Python FastAPI Backend
│   ├── Dockerfile                           # Backend container build
│   ├── requirements.txt                     # Python dependencies
│   ├── .env                                 # Backend environment config
│   ├── main.py                              # Application entry point
│   │
│   └── app/
│       ├── __init__.py
│       │
│       ├── core/                            # Core configurations
│       │   ├── __init__.py
│       │   ├── config.py                    # Settings management
│       │   ├── security.py                  # JWT, password hashing
│       │   └── dependencies.py              # FastAPI dependencies
│       │
│       ├── database/                        # Database connections
│       │   ├── __init__.py
│       │   ├── mongodb.py                   # MongoDB connection & utils
│       │   └── mysql.py                     # MySQL connection & session
│       │
│       ├── models/                          # Data models
│       │   ├── __init__.py
│       │   ├── user.py                      # User model (MongoDB)
│       │   ├── property.py                  # Property model (MongoDB)
│       │   ├── deal.py                      # Deal model (MongoDB)
│       │   └── transaction.py               # Transaction model (MySQL)
│       │
│       ├── schemas/                         # Pydantic schemas
│       │   ├── __init__.py
│       │   ├── user.py                      # User request/response schemas
│       │   ├── property.py                  # Property schemas
│       │   ├── deal.py                      # Deal schemas
│       │   └── transaction.py               # Transaction schemas
│       │
│       ├── routers/                         # API route handlers
│       │   ├── __init__.py
│       │   ├── auth.py                      # Authentication endpoints
│       │   ├── users.py                     # User management endpoints
│       │   ├── properties.py                # Property CRUD endpoints
│       │   ├── deals.py                     # Deal management endpoints
│       │   └── transactions.py              # Financial transaction endpoints
│       │
│       ├── services/                        # Business logic layer
│       │   ├── __init__.py
│       │   ├── user_service.py              # User business logic
│       │   ├── property_service.py          # Property business logic
│       │   ├── deal_service.py              # Deal workflow logic
│       │   └── transaction_service.py       # Financial transaction logic
│       │
│       └── utils/                           # Utility functions
│           ├── __init__.py
│           ├── validators.py                # Custom validators
│           └── helpers.py                   # Helper functions
│
└── frontend/                                # Vue 3 Frontend
    ├── Dockerfile                           # Frontend container build
    ├── package.json                         # Node dependencies
    ├── vite.config.ts                       # Vite configuration
    ├── tsconfig.json                        # TypeScript config
    ├── index.html                           # HTML entry point
    │
    ├── public/                              # Static assets
    │   └── favicon.ico
    │
    └── src/
        ├── main.ts                          # Vue app entry point
        ├── App.vue                          # Root component
        ├── env.d.ts                         # Environment type definitions
        │
        ├── api/                             # API communication
        │   ├── index.ts                     # Axios instance setup
        │   ├── auth.ts                      # Auth API calls
        │   ├── users.ts                     # User API calls
        │   ├── properties.ts                # Property API calls
        │   ├── deals.ts                     # Deal API calls
        │   └── transactions.ts              # Transaction API calls
        │
        ├── components/                      # Reusable components
        │   ├── common/
        │   │   ├── AppHeader.vue
        │   │   ├── AppSidebar.vue
        │   │   └── AppFooter.vue
        │   ├── property/
        │   │   ├── PropertyCard.vue
        │   │   ├── PropertyForm.vue
        │   │   └── PropertyList.vue
        │   ├── deal/
        │   │   ├── DealCard.vue
        │   │   ├── DealTimeline.vue
        │   │   └── DealParticipants.vue
        │   └── transaction/
        │       ├── TransactionTable.vue
        │       └── TransactionForm.vue
        │
        ├── views/                           # Page components
        │   ├── HomeView.vue
        │   ├── LoginView.vue
        │   ├── DashboardView.vue
        │   ├── PropertyListView.vue
        │   ├── PropertyDetailView.vue
        │   ├── DealListView.vue
        │   ├── DealDetailView.vue
        │   └── TransactionHistoryView.vue
        │
        ├── router/                          # Vue Router
        │   └── index.ts
        │
        ├── stores/                          # Pinia state management
        │   ├── auth.ts
        │   ├── property.ts
        │   ├── deal.ts
        │   └── transaction.ts
        │
        ├── types/                           # TypeScript interfaces
        │   ├── user.ts
        │   ├── property.ts
        │   ├── deal.ts
        │   └── transaction.ts
        │
        └── styles/                          # Global styles
            ├── variables.scss
            └── global.scss
```

---

## Key Files Explained

### Backend Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application entry, lifespan management |
| `core/config.py` | Environment variable loading with Pydantic Settings |
| `core/security.py` | JWT token creation/validation, password hashing |
| `database/mongodb.py` | Motor client initialization, collection getters |
| `database/mysql.py` | SQLAlchemy async engine, session factory |
| `models/*.py` | SQLAlchemy models for MySQL tables |
| `schemas/*.py` | Pydantic models for request/response validation |
| `routers/*.py` | FastAPI APIRouter with endpoint definitions |
| `services/*.py` | Business logic, database operations |

### Frontend Files

| File | Purpose |
|------|---------|
| `main.ts` | Vue app initialization, plugin registration |
| `api/index.ts` | Axios instance with interceptors |
| `router/index.ts` | Route definitions, navigation guards |
| `stores/*.ts` | Pinia stores for state management |
| `views/*.vue` | Full page components |
| `components/**/*.vue` | Reusable UI components |

---

## File Templates

### backend/app/core/config.py

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    app_name: str = "RealEstateSystem"
    debug: bool = False

    # MySQL
    mysql_host: str
    mysql_port: int = 3306
    mysql_user: str
    mysql_password: str
    mysql_database: str

    # MongoDB
    mongodb_url: str
    mongodb_database: str

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @property
    def mysql_url(self) -> str:
        return f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### backend/app/database/mongodb.py

```python
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

async def close_mongodb():
    mongodb.client.close()

def get_database() -> AsyncIOMotorDatabase:
    return mongodb.db

# Collection getters
def get_users_collection():
    return mongodb.db.users

def get_properties_collection():
    return mongodb.db.properties

def get_deals_collection():
    return mongodb.db.deals
```

### backend/app/schemas/property.py

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class PropertyType(str, Enum):
    residential = "residential"
    commercial = "commercial"

class PropertyStatus(str, Enum):
    active = "active"
    pending = "pending"
    sold = "sold"
    withdrawn = "withdrawn"

class AddressSchema(BaseModel):
    street: str
    city: str
    province: str
    postal_code: str
    country: str = "Canada"

class PropertyCreate(BaseModel):
    type: PropertyType
    address: AddressSchema
    listing_price: float = Field(gt=0)
    attributes: Dict[str, Any] = {}
    description: Optional[str] = None

class PropertyUpdate(BaseModel):
    listing_price: Optional[float] = Field(default=None, gt=0)
    status: Optional[PropertyStatus] = None
    attributes: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

class PropertyResponse(BaseModel):
    id: str
    type: PropertyType
    address: AddressSchema
    listing_price: float
    status: PropertyStatus
    attributes: Dict[str, Any]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### backend/app/core/types.py (ObjectId Handling)

```python
from bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing import Any

class PyObjectId(str):
    """Custom type for handling MongoDB ObjectId in Pydantic v2"""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x), info_arg=False, return_schema=core_schema.str_schema()
            ),
        )

    @classmethod
    def validate(cls, value: Any) -> ObjectId:
        if isinstance(value, ObjectId):
            return value
        if isinstance(value, str) and ObjectId.is_valid(value):
            return ObjectId(value)
        raise ValueError(f"Invalid ObjectId: {value}")

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "string", "example": "507f1f77bcf86cd799439011"}
```

### backend/app/services/transaction_service.py (Cross-Database with Compensation)

```python
"""
Transaction Service with Application-Level Compensation

This service handles financial transactions that span both MySQL and MongoDB.
It implements the compensation pattern to maintain data consistency.

Key Design Decisions:
1. MySQL operations are performed FIRST (harder to rollback)
2. MongoDB operations follow after MySQL commit
3. If MongoDB fails, MySQL changes are rolled back
4. All failures are logged for manual review
"""

from datetime import datetime
from typing import Optional
from bson import ObjectId
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.database.mongodb import get_deals_collection
from app.database.mysql import get_mysql_session
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.core.types import PyObjectId
import logging

logger = logging.getLogger(__name__)


class ConsistencyError(Exception):
    """Raised when cross-database consistency cannot be maintained"""
    pass


class TransactionService:
    """
    Service for managing financial transactions with cross-database consistency.

    This service ensures that when a transaction is recorded (MySQL) and
    the deal status is updated (MongoDB), either both succeed or both fail.
    """

    def __init__(self, mysql_session: AsyncSession):
        self.mysql_session = mysql_session
        self.deals_collection = get_deals_collection()

    async def record_deposit(
        self,
        deal_id: PyObjectId,
        amount: float,
        description: Optional[str] = None
    ) -> TransactionResponse:
        """
        Record a deposit payment for a deal.

        Flow:
        1. Create transaction record in MySQL
        2. Update deal status in MongoDB
        3. If step 2 fails, rollback step 1

        Args:
            deal_id: MongoDB ObjectId of the deal
            amount: Deposit amount (must be positive)
            description: Optional transaction description

        Returns:
            TransactionResponse with the created transaction

        Raises:
            ConsistencyError: If cross-database consistency cannot be maintained
            ValueError: If deal_id is invalid or amount <= 0
        """
        deal_id_str = str(deal_id)  # Explicit conversion for MySQL
        transaction = None

        try:
            # ============================================
            # STEP 1: MySQL Operation (Financial Record)
            # ============================================
            transaction = Transaction(
                deal_id=deal_id_str,
                amount=amount,
                transaction_type="deposit",
                description=description or f"Deposit for deal {deal_id_str}",
                status="completed"
            )
            self.mysql_session.add(transaction)
            await self.mysql_session.commit()
            await self.mysql_session.refresh(transaction)

            logger.info(f"MySQL: Transaction {transaction.id} created for deal {deal_id_str}")

            try:
                # ============================================
                # STEP 2: MongoDB Operation (Deal Status)
                # ============================================
                update_result = await self.deals_collection.update_one(
                    {"_id": ObjectId(deal_id_str)},
                    {
                        "$set": {
                            "status": "deposit_paid",
                            "deposit_amount": amount,
                            "deposit_transaction_id": transaction.id,
                            "updated_at": datetime.utcnow()
                        },
                        "$push": {
                            "status_history": {
                                "status": "deposit_paid",
                                "timestamp": datetime.utcnow(),
                                "transaction_id": transaction.id
                            }
                        }
                    }
                )

                if update_result.modified_count == 0:
                    raise ValueError(f"Deal {deal_id_str} not found in MongoDB")

                logger.info(f"MongoDB: Deal {deal_id_str} status updated to deposit_paid")

                return TransactionResponse(
                    id=transaction.id,
                    deal_id=deal_id_str,
                    amount=amount,
                    transaction_type="deposit",
                    status="completed",
                    description=transaction.description,
                    created_at=transaction.created_at
                )

            except Exception as mongo_error:
                # ============================================
                # STEP 3: Compensation - Rollback MySQL
                # ============================================
                logger.error(f"MongoDB failed, rolling back MySQL: {mongo_error}")

                try:
                    await self.mysql_session.delete(transaction)
                    await self.mysql_session.commit()
                    logger.info(f"MySQL rollback successful for transaction {transaction.id}")

                except SQLAlchemyError as rollback_error:
                    # Critical: Both databases are now inconsistent
                    logger.critical(
                        f"CRITICAL: MySQL rollback failed! "
                        f"Transaction {transaction.id} exists but deal {deal_id_str} not updated. "
                        f"Manual intervention required. Error: {rollback_error}"
                    )
                    # Log to compensation_events table for manual review
                    await self._log_compensation_failure(
                        deal_id=deal_id_str,
                        transaction_id=transaction.id,
                        operation="deposit",
                        error=str(rollback_error)
                    )

                raise ConsistencyError(
                    f"MongoDB update failed and has been compensated. "
                    f"Original error: {mongo_error}"
                )

        except SQLAlchemyError as mysql_error:
            # MySQL failed - no compensation needed
            await self.mysql_session.rollback()
            logger.error(f"MySQL operation failed: {mysql_error}")
            raise

    async def _log_compensation_failure(
        self,
        deal_id: str,
        transaction_id: int,
        operation: str,
        error: str
    ) -> None:
        """Log compensation failures for manual review"""
        # In production, this would write to a dedicated compensation_events table
        # or send an alert to the operations team
        logger.critical(
            f"COMPENSATION_FAILURE: "
            f"deal_id={deal_id}, "
            f"transaction_id={transaction_id}, "
            f"operation={operation}, "
            f"error={error}, "
            f"timestamp={datetime.utcnow().isoformat()}"
        )


# Usage example in router:
#
# @router.post("/deals/{deal_id}/deposit")
# async def record_deposit(
#     deal_id: str,
#     amount: float,
#     mysql_session: AsyncSession = Depends(get_mysql_session)
# ):
#     service = TransactionService(mysql_session)
#     try:
#         return await service.record_deposit(PyObjectId(deal_id), amount)
#     except ConsistencyError as e:
#         raise HTTPException(status_code=500, detail=str(e))
```

### backend/app/services/deal_service.py (Snapshot Pattern)

```python
"""
Deal Service with Participant Snapshot Pattern

When a deal is created, participant information is COPIED (snapshot)
rather than referenced. This ensures legal accuracy and audit compliance.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from bson import ObjectId

from app.database.mongodb import get_deals_collection, get_users_collection
from app.schemas.deal import DealCreate, DealResponse
from app.core.types import PyObjectId
import logging

logger = logging.getLogger(__name__)


class DealService:

    def __init__(self):
        self.deals = get_deals_collection()
        self.users = get_users_collection()

    async def create_deal(self, deal_data: DealCreate) -> DealResponse:
        """
        Create a new deal with participant snapshots.

        Participant data is COPIED at creation time, not referenced.
        This ensures the deal record reflects the state at signing time,
        even if participants later update their profiles.
        """
        # Fetch and snapshot all participants
        participants_snapshot = await self._create_participants_snapshot(
            deal_data.participants
        )

        deal_doc = {
            "property_id": ObjectId(deal_data.property_id),
            "offer_price": deal_data.offer_price,
            "status": "draft",
            "conditions": [],

            # Snapshot of participants at deal creation
            "participants_snapshot": participants_snapshot,
            "snapshot_timestamp": datetime.utcnow(),

            # Also store references for lookups (but display uses snapshot)
            "participant_refs": {
                role: str(user_id)
                for role, user_id in deal_data.participants.items()
            },

            "status_history": [
                {"status": "draft", "timestamp": datetime.utcnow()}
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = await self.deals.insert_one(deal_doc)
        deal_doc["_id"] = result.inserted_id

        logger.info(
            f"Deal created with ID {result.inserted_id}, "
            f"participants snapshot taken at {deal_doc['snapshot_timestamp']}"
        )

        return self._doc_to_response(deal_doc)

    async def _create_participants_snapshot(
        self,
        participant_ids: Dict[str, PyObjectId]
    ) -> Dict[str, Any]:
        """
        Create point-in-time snapshots of all participants.

        This data will NOT change even if the user updates their profile.
        """
        snapshot = {}

        for role, user_id in participant_ids.items():
            user = await self.users.find_one({"_id": ObjectId(str(user_id))})

            if user:
                snapshot[role] = {
                    "user_id": str(user["_id"]),
                    "name": user.get("profile", {}).get("name", "Unknown"),
                    "email": user.get("email", ""),
                    "phone": user.get("profile", {}).get("phone", ""),
                    "role_type": user.get("role", ""),
                    # Role-specific fields
                    "license_number": user.get("role_specific", {}).get("license_number"),
                    "brokerage": user.get("role_specific", {}).get("brokerage"),
                    "law_firm": user.get("role_specific", {}).get("law_firm"),
                }
            else:
                logger.warning(f"User {user_id} not found for role {role}")
                snapshot[role] = {
                    "user_id": str(user_id),
                    "name": "Unknown",
                    "error": "User not found at snapshot time"
                }

        return snapshot

    def _doc_to_response(self, doc: Dict[str, Any]) -> DealResponse:
        """Convert MongoDB document to response schema"""
        return DealResponse(
            id=str(doc["_id"]),
            property_id=str(doc["property_id"]),
            offer_price=doc["offer_price"],
            status=doc["status"],
            participants_snapshot=doc["participants_snapshot"],
            snapshot_timestamp=doc["snapshot_timestamp"],
            conditions=doc.get("conditions", []),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        )
```

### frontend/src/api/index.ts

```typescript
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
    }
    return Promise.reject(error)
  }
)

export default api
```

### frontend/src/types/property.ts

```typescript
export type PropertyType = 'residential' | 'commercial'
export type PropertyStatus = 'active' | 'pending' | 'sold' | 'withdrawn'

export interface Address {
  street: string
  city: string
  province: string
  postal_code: string
  country: string
}

export interface Property {
  id: string
  type: PropertyType
  address: Address
  listing_price: number
  status: PropertyStatus
  attributes: Record<string, any>
  description?: string
  created_at: string
  updated_at: string
}

export interface PropertyCreate {
  type: PropertyType
  address: Address
  listing_price: number
  attributes?: Record<string, any>
  description?: string
}

export interface PropertyUpdate {
  listing_price?: number
  status?: PropertyStatus
  attributes?: Record<string, any>
  description?: string
}
```

---

## .gitignore Template

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv/

# Node
node_modules/
dist/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Docker
docker-compose.override.yml

# Database volumes (if local)
data/
```

---

## Development Workflow

```
1. Start databases:      docker compose up -d
2. Start backend:        cd backend && source ../venv/bin/activate && python main.py
3. Start frontend:       cd frontend && npm run dev
4. Open browser:         http://localhost:5173 (frontend)
                         http://localhost:8000/docs (API docs)
```
