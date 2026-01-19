from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database.mongodb import connect_mongodb, close_mongodb
from app.database.mysql import connect_mysql, close_mysql
from app.routers import users, properties, deals, transactions, auth, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
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

# Configure CORS - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(properties.router)
app.include_router(deals.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Real Property Deal Management System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "databases": {
            "mongodb": "connected",
            "mysql": "connected"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
