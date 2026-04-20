"""
Async SQLAlchemy engine + session factory.

Why asyncpg over psycopg2?
  asyncpg is a pure-async PostgreSQL driver — it never blocks the event loop.
  psycopg2 is synchronous — calling it from async FastAPI would block all
  other requests while waiting for DB I/O.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from loguru import logger

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,       # logs all SQL in dev
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,        # verifies connection before use
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,    # keeps objects usable after commit
)


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields a session, closes after request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Called at startup to create all tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created ✓")