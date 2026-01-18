# Technical Architecture & Tech Stack

## Real Property Deal Management System

---

## 1. Technology Stack Overview

```
┌────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│  Vue 3 + Composition API + Vite + Element Plus + Axios         │
└────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                         BACKEND                                 │
│           FastAPI + Pydantic + SQLAlchemy + Motor              │
└────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│     MongoDB      │ │      MySQL       │ │      Redis       │
│   (Docker)       │ │    (Docker)      │ │   (Docker)       │
│                  │ │                  │ │   [Optional]     │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

---

## 2. Frontend Stack

### Framework: Vue 3 (Composition API)

**Why Vue 3?**
- Easier learning curve than React
- Cleaner logic organization with Composition API
- Excellent for form-heavy admin systems
- Strong TypeScript support

### Build Tool: Vite

**Why Vite?**
- Instant dev server startup
- Lightning-fast HMR (Hot Module Replacement)
- Native ES modules support
- Optimized production builds

### UI Component Library: Element Plus

**Why Element Plus?**
- Complete set of enterprise-grade components
- Ready-to-use tables, forms, dialogs, menus
- Consistent design language
- Excellent documentation
- **300% efficiency boost** - no custom CSS needed

### HTTP Client: Axios

**Why Axios?**
- Promise-based HTTP client
- Request/response interceptors
- Automatic JSON transformation
- Error handling utilities

---

## 3. Backend Stack

### Framework: FastAPI

**Why FastAPI?**
- Modern, async Python framework
- Auto-generated Swagger/OpenAPI docs
- Built-in request validation
- High performance (Starlette + Pydantic)
- Type hints for better IDE support

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Property(BaseModel):
    name: str
    price: float
    type: str

@app.post("/properties")
async def create_property(property: Property):
    # Auto-validated by Pydantic
    return {"status": "created"}
```

### MySQL ORM: SQLAlchemy + aiomysql

**Why SQLAlchemy?**
- Industry-standard Python ORM
- Supports async operations with aiomysql driver
- Powerful query builder
- Database migrations with Alembic

```python
from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    deal_id = Column(String(50), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    transaction_type = Column(String(20))
```

### MongoDB Driver: Motor

**Why Motor?**
- Official async MongoDB driver for Python
- Non-blocking operations
- Perfect for FastAPI's async nature
- **Never use pymongo in FastAPI** - it blocks the event loop

```python
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.real_estate

async def create_property(property_data: dict):
    result = await db.properties.insert_one(property_data)
    return str(result.inserted_id)
```

### Data Validation: Pydantic

**Why Pydantic?**
- Built into FastAPI
- Runtime type validation
- JSON serialization/deserialization
- Clear error messages

### ObjectId Serialization Configuration

**The Problem:**

MongoDB uses `ObjectId` objects, but:
- JSON APIs need strings
- MySQL stores `deal_id` as `VARCHAR(50)`
- Pydantic doesn't know how to serialize `ObjectId` by default

```python
# This will fail without proper configuration
return {"id": document["_id"]}  # ObjectId is not JSON serializable!
```

**The Solution:**

Create a custom `PyObjectId` type and configure Pydantic for automatic serialization:

```python
# app/core/types.py
from bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing import Annotated, Any

class PyObjectId(str):
    """Custom type for handling MongoDB ObjectId in Pydantic v2"""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Any,
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
                lambda x: str(x),
                info_arg=False,
                return_schema=core_schema.str_schema(),
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
        cls,
        _core_schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        return {"type": "string", "example": "507f1f77bcf86cd799439011"}
```

**Usage in Schemas:**

```python
# app/schemas/deal.py
from pydantic import BaseModel
from app.core.types import PyObjectId

class DealResponse(BaseModel):
    id: PyObjectId                    # Auto-serializes to string in JSON
    property_id: PyObjectId
    status: str
    offer_price: float

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}  # Fallback for nested objects
```

**Cross-Database Usage:**

```python
# When writing to MySQL, always convert explicitly
async def record_transaction(deal_id: PyObjectId, amount: float):
    transaction = Transaction(
        deal_id=str(deal_id),  # Explicit conversion for MySQL VARCHAR
        amount=amount
    )
    # ...
```

---

## 4. Infrastructure Stack

### Containerization: Docker + Docker Compose

**Why Docker?**
- Consistent development environment
- Easy deployment
- Isolated services
- Native performance on Ubuntu

**docker-compose.yml Example:**

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: real_estate
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  phpmyadmin:
    image: phpmyadmin
    environment:
      PMA_HOST: mysql
    ports:
      - "8080:80"
    depends_on:
      - mysql

  mongo-express:
    image: mongo-express
    environment:
      ME_CONFIG_MONGODB_SERVER: mongodb
    ports:
      - "8081:8081"
    depends_on:
      - mongodb

volumes:
  mysql_data:
  mongo_data:
```

---

## 5. Development Tools

| Tool | Purpose |
|------|---------|
| VS Code | Primary IDE (Linux version) |
| Postman | API testing (or use FastAPI's /docs) |
| Git | Version control |
| Docker Desktop | Container management |
| DBeaver | Database GUI (optional) |

### VS Code Extensions Recommended

- Python
- Pylance
- Vue - Official
- Volar
- Docker
- GitLens
- Thunder Client (API testing)

---

## 6. Database Schema Design

### MongoDB Collections

**users collection:**
```json
{
  "_id": ObjectId("..."),
  "email": "john@example.com",
  "role": "buyer",
  "profile": {
    "name": "John Doe",
    "phone": "555-1234"
  },
  "created_at": ISODate("2024-01-15")
}
```

**properties collection:**
```json
{
  "_id": ObjectId("..."),
  "type": "residential",
  "address": {
    "street": "123 Main St",
    "city": "Toronto",
    "province": "ON",
    "postal_code": "M5V 1A1"
  },
  "attributes": {
    "bedrooms": 3,
    "bathrooms": 2,
    "sqft": 1500,
    "year_built": 2010
  },
  "listing_price": 750000,
  "status": "active"
}
```

**deals collection:**
```json
{
  "_id": ObjectId("..."),
  "property_id": ObjectId("..."),
  "participants": {
    "buyer_id": ObjectId("..."),
    "seller_id": ObjectId("..."),
    "buyer_agent_id": ObjectId("..."),
    "seller_agent_id": ObjectId("..."),
    "buyer_lawyer_id": ObjectId("..."),
    "seller_lawyer_id": ObjectId("...")
  },
  "offer_price": 720000,
  "status": "conditional",
  "conditions": [
    {"type": "financing", "status": "pending", "deadline": "2024-02-01"},
    {"type": "inspection", "status": "satisfied", "completed_at": "2024-01-20"}
  ],
  "closing_date": ISODate("2024-03-01"),
  "created_at": ISODate("2024-01-15")
}
```

### MySQL Tables

**transactions table:**
```sql
CREATE TABLE transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    deal_id VARCHAR(50) NOT NULL,
    amount DECIMAL(12,2) NOT NULL CHECK (amount > 0),
    transaction_type ENUM('deposit', 'payment', 'refund', 'commission') NOT NULL,
    from_account VARCHAR(100),
    to_account VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_deal_id (deal_id),
    INDEX idx_type (transaction_type)
);
```

**trust_accounts table:**
```sql
CREATE TABLE trust_accounts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    account_number VARCHAR(50) UNIQUE NOT NULL,
    holder_name VARCHAR(100) NOT NULL,
    balance DECIMAL(14,2) DEFAULT 0.00,
    status ENUM('active', 'frozen', 'closed') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**audit_logs table:**
```sql
CREATE TABLE audit_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(50),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(50),
    old_value JSON,
    new_value JSON,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_created_at (created_at)
);
```

---

## 7. API Design

### RESTful Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/properties | List all properties |
| POST | /api/properties | Create new property |
| GET | /api/properties/{id} | Get property details |
| PUT | /api/properties/{id} | Update property |
| DELETE | /api/properties/{id} | Delete property |
| GET | /api/deals | List all deals |
| POST | /api/deals | Create new deal |
| PATCH | /api/deals/{id}/status | Update deal status |
| POST | /api/transactions | Record transaction |
| GET | /api/transactions/deal/{deal_id} | Get deal transactions |

### Auto-Generated Documentation

FastAPI automatically generates:
- **Swagger UI** at `/docs`
- **ReDoc** at `/redoc`

---

## 8. Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Security Layers                         │
├─────────────────────────────────────────────────────────────┤
│  1. Input Validation    │ Pydantic schemas                  │
│  2. Authentication      │ JWT tokens                        │
│  3. Authorization       │ Role-based access control         │
│  4. Data Encryption     │ HTTPS, hashed passwords           │
│  5. Audit Logging       │ All sensitive operations logged   │
│  6. Environment Vars    │ Secrets in .env files             │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Deployment Architecture

### Development Environment
```
Ubuntu VM (local)
├── Docker Compose
│   ├── MySQL container
│   ├── MongoDB container
│   ├── Redis container (optional)
│   └── Admin tools (phpMyAdmin, mongo-express)
├── Backend (FastAPI - uvicorn dev server)
└── Frontend (Vite dev server)
```

### Production Environment (Future)
```
Cloud Provider (AWS/GCP/Azure)
├── Container Orchestration (Docker Swarm / K8s)
│   ├── API containers (load balanced)
│   ├── Frontend containers (nginx)
│   └── Worker containers (background tasks)
├── Managed MySQL (RDS / Cloud SQL)
├── Managed MongoDB (Atlas / DocumentDB)
└── CDN for static assets
```
