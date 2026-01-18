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
