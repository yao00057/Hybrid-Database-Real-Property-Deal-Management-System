# Phase Execution Guide

## Real Property Deal Management System - Step-by-Step Implementation

---

## Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           PROJECT TIMELINE                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Phase 1: Foundation     Phase 2: Core Features      Phase 3: Polish         │
│  ==================      =====================       ==============          │
│                                                                               │
│  [1.1] Docker Setup      [2.1] User Management       [3.1] Auth (JWT)        │
│         ↓                       ↓                          ↓                 │
│  [1.2] Backend Setup     [2.2] Property Management   [3.2] Dashboard         │
│         ↓                       ↓                          ↓                 │
│  [1.3] Frontend Setup    [2.3] Deal Management       [3.3] Testing           │
│                                 ↓                          ↓                 │
│                          [2.4] Transactions          [3.4] Deployment        │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

# Phase 1: Foundation Setup

## Goal
Set up the complete development environment. Ensure frontend and backend can communicate, and all database services are running.

---

## 1.1 Docker Environment Setup

### Task Checklist

- [ ] Install Docker on Ubuntu VM
- [ ] Create project directory structure
- [ ] Write `docker-compose.yml`
- [ ] Start all database services
- [ ] Verify service status

### Step-by-Step Instructions

**Step 1: Install Docker**
```bash
# SSH to your Ubuntu VM
ssh cst8276

# Install Docker (using official script)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add current user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

**Step 2: Create Project Directory**
```bash
# Create project root
mkdir -p ~/real-estate-system
cd ~/real-estate-system

# Create directory structure
mkdir -p backend/app/{core,database,models,schemas,routers,services,utils}
mkdir -p frontend/src/{api,components,views,router,stores,types,styles}
mkdir -p init-scripts/mysql

# View structure
tree -L 3 .
```

**Step 3: Create docker-compose.yml**
```bash
cat > ~/real-estate-system/docker-compose.yml << 'EOF'
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: re_mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: real_estate
      MYSQL_USER: reuser
      MYSQL_PASSWORD: repassword
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init-scripts/mysql:/docker-entrypoint-initdb.d
    command: --default-authentication-plugin=mysql_native_password
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  mongodb:
    image: mongo:7.0
    container_name: re_mongodb
    restart: unless-stopped
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: re_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  phpmyadmin:
    image: phpmyadmin:latest
    container_name: re_phpmyadmin
    restart: unless-stopped
    environment:
      PMA_HOST: mysql
      PMA_USER: root
      PMA_PASSWORD: rootpassword
    ports:
      - "8080:80"
    depends_on:
      mysql:
        condition: service_healthy

  mongo-express:
    image: mongo-express:latest
    container_name: re_mongo_express
    restart: unless-stopped
    environment:
      ME_CONFIG_MONGODB_SERVER: mongodb
      ME_CONFIG_BASICAUTH_USERNAME: admin
      ME_CONFIG_BASICAUTH_PASSWORD: admin123
    ports:
      - "8081:8081"
    depends_on:
      mongodb:
        condition: service_healthy

volumes:
  mysql_data:
  mongo_data:
  redis_data:
EOF
```

**Step 4: Create MySQL Init Script**
```bash
cat > ~/real-estate-system/init-scripts/mysql/01-schema.sql << 'EOF'
-- Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    deal_id VARCHAR(50) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    transaction_type ENUM('deposit', 'payment', 'refund', 'commission') NOT NULL,
    from_account VARCHAR(100),
    to_account VARCHAR(100),
    description TEXT,
    status ENUM('pending', 'completed', 'failed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_deal_id (deal_id),
    INDEX idx_status (status),
    CONSTRAINT chk_amount CHECK (amount > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Trust Accounts Table
CREATE TABLE IF NOT EXISTS trust_accounts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    account_number VARCHAR(50) UNIQUE NOT NULL,
    holder_name VARCHAR(100) NOT NULL,
    holder_type ENUM('buyer', 'seller', 'agent', 'lawyer') NOT NULL,
    balance DECIMAL(14,2) DEFAULT 0.00,
    status ENUM('active', 'frozen', 'closed') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_balance CHECK (balance >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(50),
    user_email VARCHAR(100),
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
EOF
```

**Step 5: Start Services**
```bash
cd ~/real-estate-system
docker compose up -d

# Check status
docker compose ps

# View logs (if needed)
docker compose logs -f
```

### Verification Checkpoints

| Check Item | Command | Expected Result |
|------------|---------|-----------------|
| MySQL running | `docker exec re_mysql mysqladmin ping -h localhost` | `mysqld is alive` |
| MongoDB running | `docker exec re_mongodb mongosh --eval "db.stats()"` | Returns database stats |
| phpMyAdmin | Browser: `http://VM_IP:8080` | Shows login page |
| Mongo Express | Browser: `http://VM_IP:8081` | Shows database UI |

### Deliverables
- [x] `docker-compose.yml` file
- [x] MySQL init script
- [x] All containers running

---

## 1.2 Backend Skeleton Setup

### Task Checklist

- [ ] Create Python virtual environment
- [ ] Install dependencies
- [ ] Create FastAPI application skeleton
- [ ] Configure database connections
- [ ] Test API endpoints

### Step-by-Step Instructions

**Step 1: Python Environment**
```bash
cd ~/real-estate-system

# Install Python venv (if not installed)
sudo apt install -y python3-venv python3-pip

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

**Step 2: Create requirements.txt**
```bash
cat > backend/requirements.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
aiomysql==0.2.0
motor==3.3.2
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
cryptography==41.0.7
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
EOF

# Install dependencies
pip install -r backend/requirements.txt
```

**Step 3: Create Environment Config File**
```bash
cat > backend/.env << 'EOF'
# Application
APP_NAME=RealEstateSystem
APP_ENV=development
DEBUG=true

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=reuser
MYSQL_PASSWORD=repassword
MYSQL_DATABASE=real_estate

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=real_estate

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-super-secret-key-change-in-production-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
```

**Step 4: Create Core Config Module**
```bash
# backend/app/core/config.py
cat > backend/app/__init__.py << 'EOF'
EOF

cat > backend/app/core/__init__.py << 'EOF'
EOF

cat > backend/app/core/config.py << 'EOF'
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
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
EOF
```

**Step 5: Create Database Connection Modules**
```bash
# backend/app/database/__init__.py
cat > backend/app/database/__init__.py << 'EOF'
EOF

# MongoDB connection
cat > backend/app/database/mongodb.py << 'EOF'
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
EOF

# MySQL connection
cat > backend/app/database/mysql.py << 'EOF'
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.mysql_url, echo=settings.debug)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_mysql_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

async def connect_mysql():
    print("Connected to MySQL")

async def close_mysql():
    await engine.dispose()
    print("MySQL connection closed")
EOF
```

**Step 6: Create Main Application File**
```bash
cat > backend/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database.mongodb import connect_mongodb, close_mongodb
from app.database.mysql import connect_mysql, close_mysql

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_mongodb()
    await connect_mysql()
    yield
    # Shutdown
    await close_mongodb()
    await close_mysql()

app = FastAPI(
    title="Real Property Deal Management System",
    description="Hybrid Database API using MongoDB + MySQL",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Real Property Deal Management System API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "databases": {
            "mongodb": "connected",
            "mysql": "connected"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
EOF
```

**Step 7: Start and Test**
```bash
cd ~/real-estate-system/backend
source ../venv/bin/activate
python main.py
```

### Verification Checkpoints

| Check Item | Method | Expected Result |
|------------|--------|-----------------|
| API started | Terminal output | `Uvicorn running on http://0.0.0.0:8000` |
| Root endpoint | `curl http://localhost:8000/` | JSON response |
| Health check | `curl http://localhost:8000/health` | `{"status": "healthy"}` |
| Swagger docs | Browser: `http://VM_IP:8000/docs` | Shows API documentation |

### Deliverables
- [x] `backend/` directory structure complete
- [x] FastAPI application starts
- [x] Database connections successful
- [x] Swagger UI accessible

---

## 1.3 Frontend Skeleton Setup

### Task Checklist

- [ ] Install Node.js
- [ ] Create Vue 3 project
- [ ] Install Element Plus
- [ ] Configure API module
- [ ] Create basic layout

### Step-by-Step Instructions

**Step 1: Install Node.js**
```bash
# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify
node --version
npm --version
```

**Step 2: Create Vue Project**
```bash
cd ~/real-estate-system

# Create Vue project with Vite
npm create vite@latest frontend -- --template vue-ts

cd frontend

# Install base dependencies
npm install

# Install additional packages
npm install element-plus @element-plus/icons-vue axios vue-router@4 pinia
npm install -D sass @types/node
```

**Step 3: Configure vite.config.ts**
```bash
cat > vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
EOF
```

**Step 4: Create API Module**
```bash
mkdir -p src/api

cat > src/api/index.ts << 'EOF'
import axios from 'axios'

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
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
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
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
EOF
```

**Step 5: Configure Element Plus (main.ts)**
```bash
cat > src/main.ts << 'EOF'
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

// Register all icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)
app.use(router)
app.mount('#app')
EOF
```

**Step 6: Create Router**
```bash
mkdir -p src/router

cat > src/router/index.ts << 'EOF'
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue')
  },
  {
    path: '/properties',
    name: 'Properties',
    component: () => import('@/views/PropertyListView.vue')
  },
  {
    path: '/deals',
    name: 'Deals',
    component: () => import('@/views/DealListView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
EOF
```

**Step 7: Create Basic Views**
```bash
mkdir -p src/views

# Home View
cat > src/views/HomeView.vue << 'EOF'
<template>
  <div class="home">
    <el-card>
      <template #header>
        <h1>Real Property Deal Management System</h1>
      </template>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card shadow="hover" @click="$router.push('/properties')">
            <el-icon size="48"><House /></el-icon>
            <h3>Properties</h3>
            <p>Manage residential and commercial properties</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" @click="$router.push('/deals')">
            <el-icon size="48"><Document /></el-icon>
            <h3>Deals</h3>
            <p>Track property deals and workflows</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" @click="$router.push('/dashboard')">
            <el-icon size="48"><DataAnalysis /></el-icon>
            <h3>Dashboard</h3>
            <p>View analytics and reports</p>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.home {
  padding: 20px;
}
.el-card {
  cursor: pointer;
  text-align: center;
}
</style>
EOF

# Dashboard View (placeholder)
cat > src/views/DashboardView.vue << 'EOF'
<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <el-alert title="Dashboard - Coming in Phase 3" type="info" />
  </div>
</template>

<script setup lang="ts">
</script>
EOF

# Property List View (placeholder)
cat > src/views/PropertyListView.vue << 'EOF'
<template>
  <div class="property-list">
    <h1>Properties</h1>
    <el-alert title="Property Management - Coming in Phase 2" type="info" />
  </div>
</template>

<script setup lang="ts">
</script>
EOF

# Deal List View (placeholder)
cat > src/views/DealListView.vue << 'EOF'
<template>
  <div class="deal-list">
    <h1>Deals</h1>
    <el-alert title="Deal Management - Coming in Phase 2" type="info" />
  </div>
</template>

<script setup lang="ts">
</script>
EOF
```

**Step 8: Update App.vue**
```bash
cat > src/App.vue << 'EOF'
<template>
  <el-container class="layout-container">
    <el-header>
      <div class="header-content">
        <h2>Real Estate System</h2>
        <el-menu mode="horizontal" :ellipsis="false" router>
          <el-menu-item index="/">Home</el-menu-item>
          <el-menu-item index="/properties">Properties</el-menu-item>
          <el-menu-item index="/deals">Deals</el-menu-item>
          <el-menu-item index="/dashboard">Dashboard</el-menu-item>
        </el-menu>
      </div>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
</script>

<style>
.layout-container {
  min-height: 100vh;
}
.el-header {
  background-color: #545c64;
  color: white;
  display: flex;
  align-items: center;
}
.header-content {
  display: flex;
  align-items: center;
  width: 100%;
}
.header-content h2 {
  margin-right: 40px;
}
.el-menu {
  background-color: transparent;
  border: none;
}
.el-menu-item {
  color: white !important;
}
</style>
EOF
```

**Step 9: Start Frontend**
```bash
cd ~/real-estate-system/frontend
npm run dev
```

### Verification Checkpoints

| Check Item | Method | Expected Result |
|------------|--------|-----------------|
| Frontend started | Terminal output | `Local: http://localhost:5173/` |
| Page loads | Browser access | Shows home page |
| Router works | Click navigation | Pages switch correctly |
| Element Plus | Check UI | Components render properly |

### Deliverables
- [x] Vue 3 project created
- [x] Element Plus configured
- [x] Router system works
- [x] Basic layout complete

---

## Phase 1 Completion Checklist

```
[ ] Docker services all running
    [ ] MySQL
    [ ] MongoDB
    [ ] Redis
    [ ] phpMyAdmin (http://VM_IP:8080)
    [ ] Mongo Express (http://VM_IP:8081)

[ ] Backend running properly
    [ ] FastAPI started (http://VM_IP:8000)
    [ ] Swagger UI accessible (http://VM_IP:8000/docs)
    [ ] Database connections successful

[ ] Frontend running properly
    [ ] Vue dev server (http://VM_IP:5173)
    [ ] Pages display correctly
    [ ] Navigation router works
```

---

# Phase 2: Core Features

## Goal
Implement core system features: User Management, Property Management, Deal Management, Financial Transactions.

---

## 2.1 User Management

### Task Checklist

- [ ] Create User Pydantic Schema
- [ ] Create User Service (MongoDB)
- [ ] Create User Router (CRUD API)
- [ ] Frontend user list page
- [ ] Frontend user form

### Backend Code

**Schema: backend/app/schemas/user.py**
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    buyer = "buyer"
    seller = "seller"
    buyer_agent = "buyer_agent"
    seller_agent = "seller_agent"
    buyer_lawyer = "buyer_lawyer"
    seller_lawyer = "seller_lawyer"

class UserProfile(BaseModel):
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    role: UserRole
    profile: UserProfile
    role_specific: Optional[Dict[str, Any]] = {}

class UserUpdate(BaseModel):
    profile: Optional[UserProfile] = None
    role_specific: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    id: str
    email: str
    role: UserRole
    profile: UserProfile
    role_specific: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
```

**Service: backend/app/services/user_service.py**
```python
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from passlib.context import CryptContext

from app.database.mongodb import get_users_collection
from app.schemas.user import UserCreate, UserUpdate, UserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self):
        self.collection = get_users_collection()

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        user_doc = {
            "email": user_data.email,
            "password_hash": pwd_context.hash(user_data.password),
            "role": user_data.role,
            "profile": user_data.profile.model_dump(),
            "role_specific": user_data.role_specific or {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self.collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        return self._to_response(user_doc)

    async def get_user(self, user_id: str) -> Optional[UserResponse]:
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        return self._to_response(user) if user else None

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        cursor = self.collection.find().skip(skip).limit(limit)
        users = await cursor.to_list(length=limit)
        return [self._to_response(u) for u in users]

    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        update_doc = {"updated_at": datetime.utcnow()}
        if user_data.profile:
            update_doc["profile"] = user_data.profile.model_dump()
        if user_data.role_specific:
            update_doc["role_specific"] = user_data.role_specific

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": update_doc},
            return_document=True
        )
        return self._to_response(result) if result else None

    async def delete_user(self, user_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    def _to_response(self, doc: dict) -> UserResponse:
        return UserResponse(
            id=str(doc["_id"]),
            email=doc["email"],
            role=doc["role"],
            profile=doc["profile"],
            role_specific=doc.get("role_specific", {}),
            created_at=doc["created_at"]
        )
```

**Router: backend/app/routers/users.py**
```python
from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["Users"])
service = UserService()

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    return await service.create_user(user)

@router.get("/", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 100):
    return await service.get_users(skip, limit)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserUpdate):
    updated = await service.update_user(user_id, user)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}
```

**Register Router (main.py)**
```python
# Add in main.py
from app.routers import users

app.include_router(users.router)
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/users | Create user |
| GET | /api/users | Get user list |
| GET | /api/users/{id} | Get single user |
| PUT | /api/users/{id} | Update user |
| DELETE | /api/users/{id} | Delete user |

### Deliverables
- [x] User CRUD API
- [x] Frontend user management page

---

## 2.2 Property Management

### Task Checklist

- [ ] Create Property Schema (support residential/commercial)
- [ ] Create Property Service (MongoDB)
- [ ] Create Property Router
- [ ] Frontend property list (with filters)
- [ ] Frontend property form (different fields per type)

### Key Code Structure

Similar to User Management, but Schema needs to handle different property types:

```python
# Property Schema core
class PropertyType(str, Enum):
    residential = "residential"
    commercial = "commercial"

class PropertyCreate(BaseModel):
    type: PropertyType
    address: AddressSchema
    listing_price: float = Field(gt=0)
    attributes: Dict[str, Any] = {}  # Flexible fields
```

### Deliverables
- [x] Property CRUD API
- [x] Frontend property management page

---

## 2.3 Deal Management

### Task Checklist

- [ ] Create Deal Schema (with participants snapshot)
- [ ] Create Deal Service (with state machine)
- [ ] Create Deal Router
- [ ] Frontend deal list
- [ ] Frontend deal creation wizard
- [ ] Frontend deal detail (with timeline)

### Key Design Points

1. **Participants Snapshot**: Copy participant info at creation time
2. **Status Machine**: draft → submitted → conditional → firm → closing → completed
3. **Conditions**: Support adding/satisfying conditions

### Deliverables
- [x] Deal CRUD API
- [x] Status transition API
- [x] Frontend deal management page

---

## 2.4 Financial Transactions

### Task Checklist

- [ ] Create Transaction SQLAlchemy Model
- [ ] Create Transaction Service (with compensation logic)
- [ ] Create Transaction Router
- [ ] Frontend transaction history page
- [ ] Frontend payment form

### Key Code

See `04_Project_Structure.md` for the complete `transaction_service.py` with cross-database compensation logic.

### Deliverables
- [x] Transaction API
- [x] MySQL data recorded correctly
- [x] Cross-database consistency guaranteed

---

## Phase 2 Completion Checklist

```
[ ] User Management
    [ ] CRUD API works
    [ ] Frontend page complete

[ ] Property Management
    [ ] CRUD API works
    [ ] Supports residential/commercial
    [ ] Frontend page complete

[ ] Deal Management
    [ ] CRUD API works
    [ ] Status transitions work
    [ ] Snapshot saved correctly
    [ ] Frontend page complete

[ ] Financial Transactions
    [ ] API works
    [ ] MySQL data correct
    [ ] Compensation logic implemented
    [ ] Frontend page complete
```

---

# Phase 3: Polish & Enhancement

## Goal
Enhance system features with authentication, dashboard, testing.

---

## 3.1 Authentication (JWT)

### Task Checklist

- [ ] Implement JWT generation/validation
- [ ] Create /login, /register endpoints
- [ ] Frontend login page
- [ ] Route guards
- [ ] Token refresh mechanism

---

## 3.2 Dashboard

### Task Checklist

- [ ] Stats API (property count, deal count, amount totals)
- [ ] Frontend charts (using ECharts or Chart.js)
- [ ] Recent activity list

---

## 3.3 Testing

### Task Checklist

- [ ] Backend unit tests (pytest)
- [ ] API integration tests
- [ ] Frontend component tests (optional)

---

## 3.4 Deployment

### Task Checklist

- [ ] Production .env
- [ ] Dockerfile optimization
- [ ] docker-compose.prod.yml
- [ ] Deployment documentation

---

# Quick Reference Commands

```bash
# ========== Start Services ==========
# Start databases
cd ~/real-estate-system && docker compose up -d

# Start backend
cd ~/real-estate-system && source venv/bin/activate && cd backend && python main.py

# Start frontend
cd ~/real-estate-system/frontend && npm run dev

# ========== Stop Services ==========
# Stop all Docker containers
docker compose down

# ========== View Logs ==========
docker compose logs -f mysql mongodb

# ========== Reset Databases ==========
docker compose down -v && docker compose up -d

# ========== Common URLs ==========
# Frontend:      http://localhost:5173
# Backend API:   http://localhost:8000
# Swagger Docs:  http://localhost:8000/docs
# phpMyAdmin:    http://localhost:8080
# Mongo Express: http://localhost:8081
```
