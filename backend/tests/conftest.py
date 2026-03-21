"""Shared test fixtures."""

import os

# Override DB before any app imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"
os.environ["ANTHROPIC_API_KEY"] = "sk-test-dummy"

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.database import engine, init_db
from app.main import app
from app.models.trade import Base


@pytest.fixture(autouse=True)
async def setup_db():
    """Create fresh DB for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
