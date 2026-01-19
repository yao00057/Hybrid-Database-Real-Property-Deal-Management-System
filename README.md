# Real Property Deal Management System

A hybrid database solution using **MongoDB** and **MySQL** for managing real estate deals, built with **FastAPI** (Python) and **Vue 3** (TypeScript).

## Features

- **User Management**: 6 role types (buyer, seller, buyer_agent, seller_agent, buyer_lawyer, seller_lawyer)
- **Property Management**: Residential & commercial listings with filtering
- **Deal Management**: Status workflow with participant snapshots
- **Financial Transactions**: MySQL-backed with trust accounts and audit logs
- **JWT Authentication**: Role-based access control
- **Dashboard Analytics**: Real-time statistics

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3 + Vite + Element Plus + TypeScript |
| Backend | FastAPI + Pydantic + SQLAlchemy + Motor |
| Databases | MongoDB 7.0 + MySQL 8.0 |
| Cache | Redis 7 |
| DevOps | Docker + Docker Compose |
| Platform | Ubuntu 22.04 LTS |

## Quick Start - One Key Deployment

### Prerequisites

- Ubuntu 22.04 LTS (fresh installation)
- User with sudo privileges
- Internet connection

### Deploy

```bash
# 1. Clone the repository
git clone https://github.com/yao00057/Hybrid-Database-Real-Property-Deal-Management-System.git ~/real-estate-system

# 2. Run the deployment script
cd ~/real-estate-system
chmod +x deploy.sh
./deploy.sh
```

The script will:
1. Install Docker, Node.js 20.x, Python 3
2. Start database containers (MongoDB, MySQL, Redis)
3. Setup Python virtual environment and install dependencies
4. Install npm packages and start frontend
5. Display access URLs when complete

### Access URLs (after deployment)

| Service | URL |
|---------|-----|
| Frontend App | http://YOUR_SERVER_IP:5173 |
| Backend API | http://YOUR_SERVER_IP:8001 |
| API Documentation | http://YOUR_SERVER_IP:8001/docs |
| phpMyAdmin | http://YOUR_SERVER_IP:8080 |
| Mongo Express | http://YOUR_SERVER_IP:8081 |

## Project Structure

```
real-estate-system/
├── deploy.sh                 # One-key deployment script
├── docker-compose.yml        # Database services
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables
│   └── app/
│       ├── core/            # Config, security, types
│       ├── database/        # MongoDB & MySQL connections
│       ├── models/          # SQLAlchemy models
│       ├── routers/         # API endpoints
│       ├── schemas/         # Pydantic schemas
│       └── services/        # Business logic
└── frontend/
    ├── package.json         # Node dependencies
    ├── vite.config.ts       # Vite configuration
    └── src/
        ├── api/             # Axios API service
        ├── router/          # Vue Router
        ├── types.ts         # TypeScript interfaces
        └── views/           # Vue components
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/login | Login with email/password |
| POST | /api/auth/register | Register new user |
| GET | /api/auth/me | Get current user info |
| POST | /api/auth/refresh | Refresh JWT token |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/users | List all users |
| POST | /api/users | Create user |
| GET | /api/users/{id} | Get user by ID |
| PUT | /api/users/{id} | Update user |
| DELETE | /api/users/{id} | Delete user |

### Properties
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/properties | List properties (with filters) |
| POST | /api/properties | Create property |
| GET | /api/properties/{id} | Get property by ID |
| PUT | /api/properties/{id} | Update property |
| DELETE | /api/properties/{id} | Delete property |

### Deals
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/deals | List deals |
| POST | /api/deals | Create deal |
| GET | /api/deals/{id} | Get deal by ID |
| PUT | /api/deals/{id} | Update deal (status transitions) |
| DELETE | /api/deals/{id} | Delete deal |

### Transactions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/transactions | List transactions |
| POST | /api/transactions | Create transaction |
| POST | /api/transactions/{id}/complete | Complete transaction |
| GET | /api/transactions/trust-accounts/list | List trust accounts |
| POST | /api/transactions/trust-accounts | Create trust account |
| GET | /api/transactions/audit-logs/list | Get audit logs |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/dashboard/stats | Overall statistics |
| GET | /api/dashboard/properties | Property statistics |
| GET | /api/dashboard/deals | Deal statistics |
| GET | /api/dashboard/transactions | Transaction statistics |

## Role-Based Access

| Role | Users | Properties | Deals | Transactions |
|------|-------|------------|-------|--------------|
| Buyer | ❌ | Browse | My Deals | ✅ |
| Seller | ❌ | My Properties | My Deals | ✅ |
| Buyer Agent | ✅ | ✅ | ✅ | ✅ |
| Seller Agent | ✅ | ✅ | ✅ | ✅ |
| Buyer Lawyer | ✅ | ✅ | ✅ | ✅ |
| Seller Lawyer | ✅ | ✅ | ✅ | ✅ |

## Database Schema

### MongoDB Collections
- **users**: User profiles with role-specific fields
- **properties**: Residential and commercial listings
- **deals**: Deal workflow with participant snapshots

### MySQL Tables
- **transactions**: Financial transactions with ACID compliance
- **trust_accounts**: Trust account balances
- **audit_logs**: Immutable audit trail

## Development

### Manual Setup

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Useful Commands

```bash
# View logs
tail -f ~/backend.log
tail -f ~/frontend.log

# Restart services
pkill -f uvicorn && cd ~/real-estate-system/backend && ~/real-estate-system/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
pkill -f vite && cd ~/real-estate-system/frontend && npm run dev &

# Stop all
docker compose down
pkill -f uvicorn
pkill -f vite
```

## License

Academic use only - CST8276 Database Course Project

## Author

CST8276 Project Team
