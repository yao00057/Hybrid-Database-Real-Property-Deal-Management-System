# Development Environment Setup Guide

## Ubuntu Development Environment for Real Property Deal Management System

---

## Prerequisites

- Ubuntu 22.04 LTS or later
- At least 8GB RAM recommended
- 20GB+ free disk space

---

## Step 1: Install Docker

**Do NOT use snap to install Docker.** Use the official installation script:

```bash
# Download and run official Docker install script
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add current user to docker group (no sudo needed for docker commands)
sudo usermod -aG docker $USER

# Apply group changes (or log out and back in)
newgrp docker

# Verify installation
docker --version
docker compose version
```

---

## Step 2: Install Python Environment

```bash
# Update package list
sudo apt update

# Install Python 3 and essential tools
sudo apt install -y python3 python3-pip python3-venv

# Verify installation
python3 --version
pip3 --version
```

---

## Step 3: Install Node.js (for Frontend)

```bash
# Install Node.js 20.x LTS using NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version
npm --version
```

---

## Step 4: Create Project Directory

```bash
# Create project root
mkdir -p ~/real-estate-system
cd ~/real-estate-system

# Create directory structure
mkdir -p backend/app/{models,routers,database,services}
mkdir -p frontend/src/{components,views,api}

# Verify structure
tree -L 3 .
```

---

## Step 5: Setup Backend Environment

```bash
cd ~/real-estate-system

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv)
```

### Create requirements.txt

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
```

### Install Python Dependencies

```bash
pip install -r backend/requirements.txt
```

---

## Step 6: Setup Docker Compose

Create the main `docker-compose.yml` in the project root:

```bash
cat > ~/real-estate-system/docker-compose.yml << 'EOF'
version: '3.8'

services:
  # MySQL Database
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

  # MongoDB Database
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

  # Redis (Optional - for caching/sessions)
  redis:
    image: redis:7-alpine
    container_name: re_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # phpMyAdmin - MySQL Web Interface
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

  # Mongo Express - MongoDB Web Interface
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

---

## Step 7: Create MySQL Init Scripts

```bash
mkdir -p ~/real-estate-system/init-scripts/mysql

cat > ~/real-estate-system/init-scripts/mysql/01-schema.sql << 'EOF'
-- Financial Transactions Table
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
    INDEX idx_type (transaction_type),
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
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Ledger Entries Table (Double-entry bookkeeping)
CREATE TABLE IF NOT EXISTS ledger_entries (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    transaction_id INT NOT NULL,
    account_id INT NOT NULL,
    entry_type ENUM('debit', 'credit') NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    balance_after DECIMAL(14,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (account_id) REFERENCES trust_accounts(id),
    INDEX idx_transaction (transaction_id),
    INDEX idx_account (account_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
EOF
```

---

## Step 8: Create Environment Configuration

```bash
cat > ~/real-estate-system/backend/.env << 'EOF'
# Application
APP_NAME=RealEstateSystem
APP_ENV=development
DEBUG=true

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=reuser
MYSQL_PASSWORD=repassword
MYSQL_DATABASE=real_estate

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=real_estate

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
```

---

## Step 9: Start Services

```bash
cd ~/real-estate-system

# Start all containers in detached mode
docker compose up -d

# Check status
docker compose ps

# View logs (optional)
docker compose logs -f
```

### Service URLs After Startup

| Service | URL | Credentials |
|---------|-----|-------------|
| MySQL | localhost:3306 | reuser / repassword |
| MongoDB | localhost:27017 | - |
| Redis | localhost:6379 | - |
| phpMyAdmin | http://localhost:8080 | root / rootpassword |
| Mongo Express | http://localhost:8081 | admin / admin123 |

---

## Step 10: Verify Database Connections

### Test MySQL Connection

```bash
docker exec -it re_mysql mysql -u reuser -prepassword real_estate -e "SHOW TABLES;"
```

### Test MongoDB Connection

```bash
docker exec -it re_mongodb mongosh --eval "db.stats()"
```

---

## Step 11: Create Basic FastAPI Application

```bash
cat > ~/real-estate-system/backend/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database connections
mongodb_client = None
mysql_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global mongodb_client, mysql_engine

    # MongoDB connection
    mongodb_client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    app.state.mongodb = mongodb_client[os.getenv("MONGODB_DATABASE")]

    # MySQL connection
    mysql_url = f"mysql+aiomysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
    mysql_engine = create_async_engine(mysql_url, echo=True)
    app.state.mysql = sessionmaker(mysql_engine, class_=AsyncSession, expire_on_commit=False)

    print("✅ Connected to MongoDB")
    print("✅ Connected to MySQL")

    yield

    # Shutdown
    mongodb_client.close()
    await mysql_engine.dispose()
    print("🔌 Database connections closed")

app = FastAPI(
    title="Real Property Deal Management System",
    description="Hybrid Database API using MongoDB + MySQL",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vue dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Real Property Deal Management System API", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mongodb": "connected",
        "mysql": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
EOF
```

---

## Step 12: Run the Backend

```bash
cd ~/real-estate-system
source venv/bin/activate
cd backend
python main.py
```

### Access Points

- **API Root**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Step 13: Setup Frontend (Vue 3)

```bash
cd ~/real-estate-system

# Create Vue project with Vite
npm create vite@latest frontend -- --template vue-ts

cd frontend

# Install dependencies
npm install

# Install additional packages
npm install element-plus axios vue-router@4 pinia
npm install -D @types/node sass
```

---

## Quick Start Commands Reference

```bash
# Start all services
cd ~/real-estate-system && docker compose up -d

# Start backend
cd ~/real-estate-system && source venv/bin/activate && cd backend && python main.py

# Start frontend
cd ~/real-estate-system/frontend && npm run dev

# Stop all services
cd ~/real-estate-system && docker compose down

# View logs
docker compose logs -f mysql mongodb

# Reset databases (WARNING: deletes all data)
docker compose down -v && docker compose up -d
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :3306
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

### Docker Permission Denied

```bash
sudo usermod -aG docker $USER
newgrp docker
# Or log out and log back in
```

### MySQL Connection Refused

```bash
# Wait for MySQL to be ready
docker compose logs mysql

# Or restart
docker compose restart mysql
```
