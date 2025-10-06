"""
Database configuration and session management using existing schemas.
"""
from __future__ import annotations

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, Float, Text

from app.telegram.core.config import settings

logger = logging.getLogger(__name__)

# Database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Simple database models for now - can be expanded later
class ProductDB(Base):
    """SQLAlchemy model for products."""
    __tablename__ = "products"
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    merchant_id: Mapped[int]
    sku: Mapped[str]
    name: Mapped[str]
    description: Mapped[str]
    price_cents: Mapped[int]
    currency: Mapped[str]


class UserDB(Base):
    """SQLAlchemy model for users."""
    __tablename__ = "users"
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int]
    groupme_user_id: Mapped[str]
    nickname: Mapped[str]
    avatar_url: Mapped[str]
    email: Mapped[str]
    phone: Mapped[str]
    timezone: Mapped[str]
    preferred_contact_method: Mapped[str]
    trust_score: Mapped[float]
    two_factor_enabled: Mapped[bool]
    last_login_at: Mapped[str]
    login_attempts: Mapped[int]
    subscription_id: Mapped[int]
    current_plan_id: Mapped[int]


async def init_db() -> None:
    """Initialize database tables."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db() -> None:
    """Close database connections."""
    try:
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
