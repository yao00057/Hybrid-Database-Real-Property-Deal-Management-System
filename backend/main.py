from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database.mongodb import connect_mongodb, close_mongodb
from app.database.mysql import connect_mysql, close_mysql

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_mongodb()
    await connect_mysql()
    yield
    await close_mongodb()
    await close_mysql()

app = FastAPI(
    title="Real Property Deal Management System",
    description="Hybrid Database API using MongoDB + MySQL",
    version="1.0.0",
    lifespan=lifespan
)

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
