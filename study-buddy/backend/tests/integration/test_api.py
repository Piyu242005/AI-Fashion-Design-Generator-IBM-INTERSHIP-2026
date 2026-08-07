"""
Integration Tests — API Endpoints
===================================
End-to-end tests for FastAPI routes using httpx AsyncClient.
Tests the full request→service→repository→response cycle
with an in-memory SQLite database (no external deps needed).
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.database import Base
from app.dependencies import get_db
from app.main import app

# ---------------------------------------------------------------------------
# Test database — in-memory SQLite (isolated per test run)
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False,
                                   connect_args={"check_same_thread": False})
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession,
                                       expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Create all tables in the test database once per session."""
    import app.models  # noqa: F401 — register models
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    """Return an AsyncClient with DB override injected."""
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_register_new_user(client: AsyncClient):
    resp = await client.post("/auth/register", json={
        "name": "Test Student",
        "email": "student@test.com",
        "password": "testpass123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "student@test.com"
    assert data["name"] == "Test Student"
    assert "hashed_password" not in data  # never expose password


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {"name": "User One", "email": "dup@test.com", "password": "password123"}
    await client.post("/auth/register", json=payload)
    resp = await client.post("/auth/register", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_valid_credentials(client: AsyncClient):
    # Register first
    await client.post("/auth/register", json={
        "name": "Login User", "email": "login@test.com", "password": "loginpass1"
    })
    # Login
    resp = await client.post("/auth/login",
        data={"username": "login@test.com", "password": "loginpass1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/auth/register", json={
        "name": "Wrong Pass", "email": "wrong@test.com", "password": "correctpass1"
    })
    resp = await client.post("/auth/login",
        data={"username": "wrong@test.com", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(client: AsyncClient):
    await client.post("/auth/register", json={
        "name": "Me User", "email": "me@test.com", "password": "mepassword1"
    })
    login = await client.post("/auth/login",
        data={"username": "me@test.com", "password": "mepassword1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    token = login.json()["access_token"]

    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@test.com"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Documents endpoints (no file processing — just API contract)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    """Helper: register + login, return auth headers."""
    await client.post("/auth/register", json={
        "name": "Doc User", "email": "docuser@test.com", "password": "docpass123"
    })
    resp = await client.post("/auth/login",
        data={"username": "docuser@test.com", "password": "docpass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.mark.asyncio
async def test_list_documents_empty(client: AsyncClient, auth_headers):
    resp = await client.get("/documents/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_delete_nonexistent_document(client: AsyncClient, auth_headers):
    resp = await client.delete("/documents/99999", headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_dashboard_stats_authenticated(client: AsyncClient, auth_headers):
    resp = await client.get("/dashboard/stats", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "document_count" in data
    assert "avg_quiz_score" in data
    assert "weak_topics" in data


@pytest.mark.asyncio
async def test_dashboard_stats_unauthenticated(client: AsyncClient):
    resp = await client.get("/dashboard/stats")
    assert resp.status_code == 401
