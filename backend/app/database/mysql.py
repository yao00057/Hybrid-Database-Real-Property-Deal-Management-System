from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import get_settings

settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.mysql_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for ORM models
Base = declarative_base()


async def connect_mysql():
    """Initialize MySQL connection and create tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Connected to MySQL")


async def close_mysql():
    """Close MySQL connection"""
    await engine.dispose()
    print("MySQL connection closed")


async def get_session() -> AsyncSession:
    """Dependency for getting async session"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
