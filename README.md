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
| Platform | Ubuntu 22.04 LTS / Windows 10/11 |

---

## Quick Start - One Key Deployment

### Option 1: Ubuntu 22.04 LTS

```bash
# 1. Clone the repository
git clone https://github.com/yao00057/Hybrid-Database-Real-Property-Deal-Management-System.git ~/real-estate-system

# 2. Run the deployment script
cd ~/real-estate-system
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Windows 10/11

**Prerequisites:**
- Windows 10/11 (64-bit)
- PowerShell running as Administrator
- Virtualization enabled in BIOS (for Docker)

**Deploy:**

```powershell
# 1. Download the script (run in PowerShell as Administrator)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/yao00057/Hybrid-Database-Real-Property-Deal-Management-System/main/deploy-windows.ps1" -OutFile "$env:TEMP\deploy-windows.ps1"

# 2. Run the deployment script
Set-ExecutionPolicy Bypass -Scope Process -Force
& "$env:TEMP\deploy-windows.ps1"
```

**Or manually:**

```powershell
# 1. Clone the repository (to Desktop)
git clone https://github.com/yao00057/Hybrid-Database-Real-Property-Deal-Management-System.git $env:USERPROFILE\Desktop\real-estate-system

# 2. Run the deployment script (as Administrator)
cd $env:USERPROFILE\Desktop\real-estate-system
Set-ExecutionPolicy Bypass -Scope Process -Force
.\deploy-windows.ps1
```

**Note:** If Docker Desktop is not installed, the script will install it and ask you to restart your computer. After restart, run the script again.

**Windows Install Location:** The project will be installed to your Desktop at:
```
C:\Users\<YourUsername>\Desktop\real-estate-system\
```

---

## What the Deployment Scripts Do

| Step | Ubuntu (deploy.sh) | Windows (deploy-windows.ps1) |
|------|-------------------|------------------------------|
| 1 | Update system packages | Install Chocolatey |
| 2 | Install Docker | Install Docker Desktop |
| 3 | Install Node.js 20.x | Install Node.js LTS |
| 4 | Install Python 3 | Install Python 3 |
| 5 | Clone repository | Clone repository |
| 6 | Start Docker containers | Start Docker containers |
| 7 | Setup Python venv & deps | Setup Python venv & deps |
| 8 | Start services | Create start/stop scripts |

---

## Access URLs (after deployment)

| Service | URL |
|---------|-----|
| Frontend App | http://localhost:5173 |
| Backend API | http://localhost:8001 |
| API Documentation | http://localhost:8001/docs |
| phpMyAdmin | http://localhost:8080 |
| Mongo Express | http://localhost:8081 |

**Note:** On Ubuntu, replace `localhost` with your server IP for remote access.

---

## How to Use the Application

### Step 1: Register an Account

1. Open http://localhost:5173 in your browser
2. Click **"Register here"** on the login page
3. Fill in your details:
   - Full Name
   - Email
   - Password (min 6 characters)
   - Select your role (Buyer, Seller, Agent, or Lawyer)
   - Phone number
4. Click **Register**

### Step 2: Login

1. Enter your email and password
2. Click **Login**
3. You'll be redirected to the Dashboard

### Step 3: Explore Features

After login, you can access different features based on your role:

| Feature | Buyer | Seller | Agent/Lawyer |
|---------|-------|--------|--------------|
| Dashboard | ✅ | ✅ | ✅ |
| View Properties | ✅ | ✅ | ✅ |
| Create Properties | ❌ | ✅ | ✅ |
| View Deals | My Deals | My Deals | All Deals |
| Create Deals | ❌ | ❌ | ✅ |
| Manage Users | ❌ | ❌ | ✅ |
| Transactions | View | View | Full Access |

### Available User Roles

| Role | Description |
|------|-------------|
| **Buyer** | Can browse properties and view their deals |
| **Seller** | Can list properties and view their deals |
| **Buyer Agent** | Full access - represents buyers in deals |
| **Seller Agent** | Full access - represents sellers in deals |
| **Buyer Lawyer** | Full access - handles legal for buyers |
| **Seller Lawyer** | Full access - handles legal for sellers |

### Basic Workflow

### Creating a Deal (Agents/Lawyers)

The Deal creation form features smart dropdown selectors:

1. **Select Property**: Choose from active property listings (shows address and price)
2. **Select Participants**: 
   - Buyer (from registered buyers)
   - Seller (from registered sellers)
   - Buyer Agent (optional)
   - Seller Agent (optional)
   - Buyer Lawyer (optional)
   - Seller Lawyer (optional)
3. **Enter Deal Details**:
   - Offer Price
   - Closing Date (optional)
   - Notes

The system automatically validates all selections and creates participant snapshots for the deal record.


1. **Seller** lists a property
2. **Buyer** browses properties
3. **Agent** creates a deal linking buyer, seller, and property
4. **Lawyer** reviews and manages deal documents
5. **Transactions** are recorded for deposits, commissions, legal fees

---

## Windows Quick Commands

After deployment on Windows, find these scripts on your **Desktop** in the `real-estate-system` folder:

| Script | Description |
|--------|-------------|
| `start-all.bat` | Start all services (databases + backend + frontend) |
| `stop-all.bat` | Stop all services |
| `start-backend.bat` | Start only the backend API |
| `start-frontend.bat` | Start only the frontend |

**Quick Start:** Just double-click `start-all.bat` on your Desktop to launch everything!

---

## Ubuntu Quick Commands

```bash
# View logs
tail -f ~/backend.log
tail -f ~/frontend.log

# Restart services
pkill -f uvicorn && cd ~/real-estate-system/backend && source ../venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
pkill -f vite && cd ~/real-estate-system/frontend && npm run dev &

# Stop all
docker compose down
pkill -f uvicorn
pkill -f vite
```

---

## Project Structure

```
real-estate-system/
├── deploy.sh                 # Ubuntu deployment script
├── deploy-windows.ps1        # Windows deployment script
├── docker-compose.yml        # Database services
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
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

---

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

---

## Role-Based Access

| Role | Users | Properties | Deals | Transactions |
|------|-------|------------|-------|--------------|
| Buyer | - | Browse | My Deals | View |
| Seller | - | My Properties | My Deals | View |
| Buyer Agent | Full | Full | Full | Full |
| Seller Agent | Full | Full | Full | Full |
| Buyer Lawyer | Full | Full | Full | Full |
| Seller Lawyer | Full | Full | Full | Full |

---

## Database Schema

### MongoDB Collections
- **users**: User profiles with role-specific fields
- **properties**: Residential and commercial listings
- **deals**: Deal workflow with participant snapshots

### MySQL Tables
- **transactions**: Financial transactions with ACID compliance
- **trust_accounts**: Trust account balances
- **audit_logs**: Immutable audit trail

---

## Default Credentials

| Service | Username | Password |
|---------|----------|----------|
| MySQL | real_estate_user | real_estate_pass |
| MySQL (root) | root | rootpassword |
| MongoDB | (no auth) | (development mode) |
| phpMyAdmin | real_estate_user | real_estate_pass |

---

## Troubleshooting

### Windows: Script fails at Python installation
If the script says "Python not found" after installation:
1. **Close PowerShell completely**
2. **Reopen PowerShell as Administrator**
3. **Run the script again** - it will detect the installed Python

```powershell
# Re-run the deployment script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/yao00057/Hybrid-Database-Real-Property-Deal-Management-System/main/deploy-windows.ps1" -OutFile "$env:TEMP\deploy-windows.ps1"
& "$env:TEMP\deploy-windows.ps1"
```

### Windows: Docker Desktop not installed
If Docker Desktop is not installed:
1. The script will install Docker Desktop automatically
2. **You must restart your computer** after installation
3. After restart, **launch Docker Desktop** from Start Menu
4. Wait for Docker to fully start (whale icon in system tray stops animating)
5. Run the deployment script again

### Windows: Docker not starting
1. Ensure **virtualization is enabled in BIOS/UEFI**
   - Restart computer → Enter BIOS (F2, F10, or DEL key)
   - Find "Virtualization Technology" or "VT-x" → Enable it
2. Open Docker Desktop and wait for it to fully start
3. Check the whale icon in system tray is stable (not animating)

### Windows: Script fails mid-way
If the script fails after some steps completed:
```powershell
# Delete the incomplete installation and start fresh
Remove-Item -Recurse -Force $env:USERPROFILE\Desktop\real-estate-system

# Re-run the script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/yao00057/Hybrid-Database-Real-Property-Deal-Management-System/main/deploy-windows.ps1" -OutFile "$env:TEMP\deploy-windows.ps1"
& "$env:TEMP\deploy-windows.ps1"
```

### Port already in use
```bash
# Ubuntu
sudo lsof -i :8001  # Find process using port
sudo kill -9 <PID>  # Kill the process
```

```powershell
# Windows (PowerShell as Admin)
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

### Database connection failed
```bash
# Check if containers are running
docker ps

# Restart containers
docker compose down
docker compose up -d
```

### Windows: npm or node not found
If npm/node commands fail after installation:
1. Close PowerShell
2. Reopen PowerShell as Administrator
3. Try the command again

---

## License

Academic use only - CST8276 Database Course Project

## Author

CST8276 Project Team

---

## Seed Test Data

After deployment, you can quickly create test accounts for all 6 user roles:

### Ubuntu/Linux
```bash
cd ~/real-estate-system
./seed-data.sh
```

### Windows
```
Double-click seed-data.bat in the project folder
```

### Test Accounts Created

| Role | Email | Password |
|------|-------|----------|
| Buyer | buyer1@test.com | test123 |
| Buyer | buyer2@test.com | test123 |
| Seller | seller1@test.com | test123 |
| Seller | seller2@test.com | test123 |
| Buyer Agent | buyeragent1@test.com | test123 |
| Buyer Agent | buyeragent2@test.com | test123 |
| Seller Agent | selleragent1@test.com | test123 |
| Seller Agent | selleragent2@test.com | test123 |
| Buyer Lawyer | buyerlawyer1@test.com | test123 |
| Buyer Lawyer | buyerlawyer2@test.com | test123 |
| Seller Lawyer | sellerlawyer1@test.com | test123 |
| Seller Lawyer | sellerlawyer2@test.com | test123 |

Use these accounts to quickly test the application without manually registering users.
