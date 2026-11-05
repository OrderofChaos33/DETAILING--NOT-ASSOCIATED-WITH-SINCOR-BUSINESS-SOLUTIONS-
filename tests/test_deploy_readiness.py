"""Deploy-readiness: a fresh host (e.g. Railway) must boot usable.

1. Startup creates the model tables on an empty database (idempotent).
2. EXTRA_ALLOWED_HOSTS env extends the TrustedHost list so the platform's
   own domain can serve the app before the custom domain is pointed at it.
3. Unknown hosts are still rejected (the owner's lockdown stays intact).
"""
import importlib
import sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "detailing_crm"))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine

import app.core.config as config
import app.core.database as database
from app.main import app


@pytest.mark.asyncio
async def test_create_tables_creates_all_model_tables():
    eng = create_async_engine("sqlite+aiosqlite:///:memory:")
    await database.create_tables(eng)
    async with eng.connect() as conn:
        names = await conn.run_sync(lambda c: set(inspect(c).get_table_names()))
    assert {"clients", "vehicles", "appointments", "leads"} <= names
    # idempotent: second run is a no-op, not an error
    await database.create_tables(eng)
    await eng.dispose()


def test_extra_allowed_hosts_parsed_from_env(monkeypatch):
    monkeypatch.setenv("EXTRA_ALLOWED_HOSTS", "foo.up.railway.app, bar.example.com ")
    reloaded = importlib.reload(config)
    try:
        assert reloaded.EXTRA_ALLOWED_HOSTS == ["foo.up.railway.app", "bar.example.com"]
    finally:
        monkeypatch.delenv("EXTRA_ALLOWED_HOSTS", raising=False)
        importlib.reload(config)


def test_unknown_host_rejected(client):
    r = client.get("/health", headers={"host": "evil.example.com"})
    assert r.status_code == 400


def test_startup_lifespan_creates_tables(monkeypatch):
    eng = create_async_engine("sqlite+aiosqlite:///:memory:")
    monkeypatch.setattr(database, "engine", eng)
    with TestClient(app, base_url="http://localhost") as c:
        r = c.get("/health")
        assert r.status_code == 200
    import asyncio

    async def names():
        async with eng.connect() as conn:
            return await conn.run_sync(lambda c: set(inspect(c).get_table_names()))

    assert "clients" in asyncio.run(names())
