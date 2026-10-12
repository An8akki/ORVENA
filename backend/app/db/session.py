"""
Database Session Management
Async SQLAlchemy session configuration
"""
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from app.core.config import settings
from app.core.logging import logger


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Force SQL logging for debugging
    echo_pool=True,  # Log connection pool activity
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_pre_ping=True,  # Verify connections before using
)

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """
    Get database session
    
    Usage:
        async with get_db() as session:
            # Use session
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database (create tables if needed)"""
    from app.db.base import Base
    
    async with engine.begin() as conn:
        # In production, use Alembic migrations instead
        if settings.is_development:
            logger.info("Creating database tables")
            await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")
