"""SQLAlchemy 2.0 async session management (PostgreSQL via asyncpg)."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=20, max_overflow=10)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def create_tables(target_engine=None) -> None:
    """Create all model tables if they do not exist (idempotent).

    Runs at startup so a fresh deploy against an empty database (e.g. a
    new Railway Postgres) serves bookings immediately instead of 500ing
    on missing tables.
    """
    import app.models  # noqa: F401 — register models on Base.metadata

    eng = target_engine or engine
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
