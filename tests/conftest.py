import pytest
from unittest.mock import patch
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from app.main import app
from app import database

TEST_DB_NAME = "task_manager_test"


@pytest.fixture(autouse=True)
def disable_rate_limits():
    from app.dependencies import limiter

    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest.fixture
async def setup_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    database.db = client[TEST_DB_NAME]
    yield
    database.db = None
    await client.drop_database(TEST_DB_NAME)
    client.close()


@pytest.fixture
async def client(setup_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_token(client):
    await client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
    })
    res = await client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123",
    })
    return res.json()["access_token"]


@pytest.fixture
async def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
