"""Shared test client: ONE in-memory DB + ONE dependency override for the
whole suite, so test modules cannot stomp each other's overrides."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "detailing_crm"))
import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.core.database import Base, get_db
from app.main import app

engine = create_async_engine("sqlite+aiosqlite:///:memory:")
Session = async_sessionmaker(engine, expire_on_commit=False)

async def _override_db():
    async with Session() as s:
        yield s

@pytest.fixture(scope="session", autouse=True)
def _setup():
    async def make():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.get_event_loop().run_until_complete(make())
    app.dependency_overrides[get_db] = _override_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def client():
    return TestClient(app, base_url="http://localhost")
