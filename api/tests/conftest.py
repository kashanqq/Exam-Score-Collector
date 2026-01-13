# api/tests/conftest.py
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) # Создаем таблицы
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)   # Удаляем таблицы

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac