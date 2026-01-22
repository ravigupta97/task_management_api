
"""
Database connection and session management.
Uses SQLAlchemy 2.0 async engine for non-blocking database operations.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# Create async engine
# echo=True in development shows SQL queries in console (helpful for debugging)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    future=True,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,  # Connection pool size
    max_overflow=20  # Max connections beyond pool_size
)

# Create async session factory
# expire_on_commit=False prevents lazy loading issues after commit
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for all ORM models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields database sessions.
    
    Usage in FastAPI endpoints:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            # Use db here
            pass
    
    Automatically handles:
    - Session creation
    - Transaction management
    - Session cleanup (even if errors occur)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Commit if no errors
        except Exception:
            await session.rollback()  # Rollback on error
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


async def close_db() -> None:
    """
    Close database connection pool.
    Should be called on application shutdown.
    """
    await engine.dispose()