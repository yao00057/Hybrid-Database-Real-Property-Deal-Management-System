# CST8276 Project Proposal

## Real Property Deal Management System
### Hybrid Database Architecture with Python, MongoDB, and MySQL

---

## Document Index

| # | Document | Description |
|---|----------|-------------|
| 01 | [Project_Proposal.md](./01_Project_Proposal.md) | Complete project proposal with background, objectives, and justification |
| 02 | [Technical_Architecture.md](./02_Technical_Architecture.md) | Technology stack details, database schemas, API design |
| 03 | [Development_Setup_Guide.md](./03_Development_Setup_Guide.md) | Step-by-step Ubuntu environment setup instructions |
| 04 | [Project_Structure.md](./04_Project_Structure.md) | Directory structure and file templates |
| 05 | [Development_Milestones.md](./05_Development_Milestones.md) | Implementation phases and task checklist |
| 06 | [Phase_Execution_Guide.md](./06_Phase_Execution_Guide.md) | **Detailed phase-by-phase execution guide with copy-paste commands** |

---

## Quick Overview

### What is this project?

A **real property deal management system** that demonstrates the effective use of a **hybrid database architecture**:

- **MongoDB** for flexible data: users, properties, deal workflows
- **MySQL** for financial data: transactions, trust accounts, audit logs
- **Python (FastAPI)** as the integration layer
- **Vue 3** for the frontend interface

### Why hybrid databases?

| Challenge | MongoDB Solution | MySQL Solution |
|-----------|------------------|----------------|
| Different user roles with varying attributes | Flexible schema | - |
| Residential vs Commercial properties | Document-based storage | - |
| Complex deal workflows | Nested documents | - |
| Financial accuracy | - | ACID transactions |
| Audit compliance | - | Immutable records |

---

## Technology Stack Summary

```
Frontend:    Vue 3 + Vite + Element Plus + TypeScript
Backend:     FastAPI + Pydantic + SQLAlchemy + Motor
Databases:   MongoDB 7.0 + MySQL 8.0
DevOps:      Docker + Docker Compose
Platform:    Ubuntu 22.04 LTS
```

---

## Quick Start (After Setup)

```bash
# 1. Start database services
cd ~/real-estate-system
docker compose up -d

# 2. Start backend (in one terminal)
source venv/bin/activate
cd backend
python main.py

# 3. Start frontend (in another terminal)
cd frontend
npm run dev

# 4. Access the application
# Frontend:  http://localhost:5173
# API Docs:  http://localhost:8000/docs
# phpMyAdmin: http://localhost:8080
# Mongo Express: http://localhost:8081
```

---

## Project Scope

### In Scope
- User role management (6 role types)
- Property management (residential + commercial)
- Deal lifecycle management
- Financial transaction tracking
- RESTful API with auto-documentation

### Out of Scope
- Payment gateway integration
- Government registry integration
- AI valuation models

---

## Key Learning Outcomes

1. **Hybrid Database Design** - When to use SQL vs NoSQL
2. **Async Python** - Motor, aiomysql with FastAPI
3. **Modern Frontend** - Vue 3 Composition API
4. **Containerization** - Docker for development
5. **API Design** - RESTful best practices

---

## Author

**CST8276 Database Course Project**

---

## License

Academic use only.
