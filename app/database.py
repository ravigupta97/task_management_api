"""
Database connection and session management.
Uses SQLAlchemy 2.0 async engine with optimized connection pooling.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Determine pool class based on environment
if settings.ENVIRONMENT == "testing":
    poolclass = NullPool  # No pooling for tests (each test gets fresh connections)
else:
    poolclass = QueuePool  # Connection pooling for dev/prod

# Create async engine with optimized settings
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    future=True,
    poolclass=poolclass,
    pool_size=10,  # Number of connections to maintain
    max_overflow=20,  # Additional connections when pool is exhausted
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_timeout=30,  # Timeout for getting connection from pool
    echo_pool=False,  # Don't log pool checkouts/checkins
)

# Create async session factory with optimized settings
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Keep objects accessible after commit
    autocommit=False,
    autoflush=False,
)

# Base class for all ORM models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields database sessions.
    
    Automatically handles:
    - Session creation
    - Transaction management
    - Session cleanup (even if errors occur)
    
    Usage in FastAPI endpoints:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            # Use db here
            pass
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Commit if no errors
        except Exception as e:
            await session.rollback()  # Rollback on error
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    
    WARNING: Only use in development/testing!
    In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


async def close_db() -> None:
    """
    Close database connection pool.
    Should be called on application shutdown.
    """
    await engine.dispose()
    logger.info("Database connections closed")


async def check_db_connection() -> bool:
    """
    Check if database connection is healthy.
    
    Returns:
        True if database is accessible, False otherwise
    """
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False