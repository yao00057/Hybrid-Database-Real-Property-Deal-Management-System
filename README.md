# Hybrid Database Real Property Deal Management System

A real property deal management system demonstrating effective use of hybrid database architecture.

## Technology Stack

- **Frontend**: Vue 3 + Vite + Element Plus + TypeScript
- **Backend**: FastAPI + Pydantic + SQLAlchemy + Motor
- **Databases**: MongoDB 7.0 + MySQL 8.0
- **DevOps**: Docker + Docker Compose
- **Platform**: Ubuntu 22.04 LTS

## Architecture

- **MongoDB**: Flexible data (users, properties, deal workflows)
- **MySQL**: Financial data (transactions, trust accounts, audit logs)

## Quick Start

```bash
# Start database services
docker compose up -d

# Start backend
cd backend && source ../venv/bin/activate && python main.py

# Start frontend
cd frontend && npm run dev
```

## Project Structure

```
real-estate-system/
├── docker-compose.yml
├── backend/
│   ├── main.py
│   └── app/
│       ├── core/
│       ├── database/
│       ├── models/
│       ├── schemas/
│       ├── routers/
│       └── services/
└── frontend/
    └── src/
        ├── api/
        ├── components/
        ├── views/
        └── router/
```

## Documentation

See `/docs` folder for detailed documentation.

## License

Academic use only - CST8276 Database Course Project
