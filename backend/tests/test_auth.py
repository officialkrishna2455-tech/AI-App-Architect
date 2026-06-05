import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.database import Base, get_db

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.anyio
async def test_register_user():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "password123", "name": "Test User"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert data["role"] == "user"

@pytest.mark.anyio
async def test_login_user():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post(
            "/api/v1/auth/register",
            json={"email": "login@example.com", "password": "password123"}
        )
        response = await ac.post(
            "/api/v1/auth/login",
            json={"email": "login@example.com", "password": "password123"}
        )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.anyio
async def test_invalid_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/login",
            json={"email": "wrong@example.com", "password": "wrongpassword"}
        )
    assert response.status_code == 401

@pytest.mark.anyio
async def test_refresh_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post(
            "/api/v1/auth/register",
            json={"email": "refresh@example.com", "password": "password123"}
        )
        login_res = await ac.post(
            "/api/v1/auth/login",
            json={"email": "refresh@example.com", "password": "password123"}
        )
        refresh_token = login_res.json()["refresh_token"]

        refresh_res = await ac.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
    assert refresh_res.status_code == 200
    assert "access_token" in refresh_res.json()

@pytest.mark.anyio
async def test_get_me():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post(
            "/api/v1/auth/register",
            json={"email": "me@example.com", "password": "password123"}
        )
        login_res = await ac.post(
            "/api/v1/auth/login",
            json={"email": "me@example.com", "password": "password123"}
        )
        access_token = login_res.json()["access_token"]

        me_res = await ac.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "me@example.com"
