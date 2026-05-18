"""
Integration tests for /api/auth/* routes.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta, UTC

from main import app
from src.database.db import get_db
from src.database.models import User

def make_db_user(**kwargs):
    defaults = dict(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
        confirmed=True,
        verification_token=None,
        role="user",
        reset_token=None,
        reset_token_expires=None,
        avatar=None,
    )
    defaults.update(kwargs)
    u = MagicMock(spec=User)
    for k, v in defaults.items():
        setattr(u, k, v)
    return u

@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db

@pytest.fixture
def auth_client(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    return mock_db

@pytest.mark.asyncio
async def test_signup_success():
    mock_db = AsyncMock()
 
    async def override_db():
        yield mock_db
 
    app.dependency_overrides[get_db] = override_db
 
    with patch("src.api.auth.UserService") as MockService:
        svc = AsyncMock()
        svc.get_by_email.return_value = None
        svc.get_by_username.return_value = None
        new_user = make_db_user(id=1, confirmed=False, role="user")
        svc.create_user.return_value = new_user
        MockService.return_value = svc
 
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            resp = await ac.post(
                "/api/auth/signup",
                json={
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "secret123",
                },
            )
 
    app.dependency_overrides.clear()
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_signup_email_conflict():
    mock_db = AsyncMock()
 
    async def override_db():
        yield mock_db
 
    app.dependency_overrides[get_db] = override_db
 
    with patch("src.api.auth.UserService") as MockService:
        svc = AsyncMock()
        svc.get_by_email.return_value = make_db_user()
        MockService.return_value = svc
 
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            resp = await ac.post(
                "/api/auth/signup",
                json={
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "secret123",
                },
            )
 
    app.dependency_overrides.clear()
    assert resp.status_code == 409

@pytest.mark.asyncio
async def test_login_success():
    mock_db = AsyncMock()
 
    async def override_db():
        yield mock_db
 
    app.dependency_overrides[get_db] = override_db
 
    with patch("src.api.auth.UserService") as MockService:
        with patch("src.api.auth.verify_password", return_value=True):
            with patch(
                "src.api.auth.create_access_token", return_value="fake.token"
            ):
                svc = AsyncMock()
                svc.get_by_username.return_value = make_db_user(
                    confirmed=True, hashed_password="hashed"
                )
                MockService.return_value = svc
 
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as ac:
                    resp = await ac.post(
                        "/api/auth/login",
                        data={"username": "testuser", "password": "secret123"},
                    )
 
    app.dependency_overrides.clear()
    assert resp.status_code == 200
    assert resp.json()["access_token"] == "fake.token"

@pytest.mark.asyncio
async def test_login_wrong_password():
    mock_db = AsyncMock()
 
    async def override_db():
        yield mock_db
 
    app.dependency_overrides[get_db] = override_db
 
    with patch("src.api.auth.UserService") as MockService:
        with patch("src.api.auth.verify_password", return_value=False):
            svc = AsyncMock()
            svc.get_by_username.return_value = make_db_user(confirmed=True)
            MockService.return_value = svc
 
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as ac:
                resp = await ac.post(
                    "/api/auth/login",
                    data={"username": "testuser", "password": "wrong"},
                )
 
    app.dependency_overrides.clear()
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_login_unconfirmed_email():
    mock_db = AsyncMock()
 
    async def override_db():
        yield mock_db
 
    app.dependency_overrides[get_db] = override_db
 
    with patch("src.api.auth.UserService") as MockService:
        svc = AsyncMock()
        svc.get_by_username.return_value = make_db_user(confirmed=False)
        MockService.return_value = svc
 
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            resp = await ac.post(
                "/api/auth/login",
                data={"username": "testuser", "password": "secret123"},
            )
 
    app.dependency_overrides.clear()
    assert resp.status_code == 401
    assert "confirmed" in resp.json()["detail"].lower()

@pytest.mark.asyncio
async def test_verify_email_success():
    mock_db = AsyncMock()
 
    async def override_db():
        yield mock_db
 
    app.dependency_overrides[get_db] = override_db
 
    with patch("src.api.auth.UserService") as MockService:
        svc = AsyncMock()
        svc.confirm_email.return_value = make_db_user(confirmed=True)
        MockService.return_value = svc
 
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            resp = await ac.get("/api/auth/verify/valid-token")
 
    app.dependency_overrides.clear()
    assert resp.status_code == 200
    assert "verified" in resp.json()["message"].lower()

@pytest.mark.asyncio
async def test_verify_email_invalid_token():
    mock_db = AsyncMock()
 
    async def override_db():
        yield mock_db
 
    app.dependency_overrides[get_db] = override_db
 
    with patch("src.api.auth.UserService") as MockService:
        svc = AsyncMock()
        svc.confirm_email.return_value = None
        MockService.return_value = svc
 
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            resp = await ac.get("/api/auth/verify/bad-token")
 
    app.dependency_overrides.clear()
    assert resp.status_code == 400

@pytest.mark.asyncio
async def test_forgot_password_user_not_found():
    mock_db = AsyncMock()
 
    async def override_db():
        yield mock_db
 
    app.dependency_overrides[get_db] = override_db
 
    with patch("src.api.auth.UserService") as MockService:
        svc = AsyncMock()
        svc.get_by_email.return_value = None
        MockService.return_value = svc
 
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            resp = await ac.post(
                "/api/auth/forgot-password",
                json={"email": "nobody@example.com"},
            )
 
    app.dependency_overrides.clear()
    assert resp.status_code == 200
    assert "message" in resp.json()

@pytest.mark.asyncio
async def test_forgot_password_user_found():
    mock_db = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
 
    async def override_db():
        yield mock_db
 
    app.dependency_overrides[get_db] = override_db
 
    user = make_db_user()
 
    with patch("src.api.auth.UserService") as MockService:
        with patch("src.api.auth.create_reset_token", return_value="reset-tok"):
            svc = AsyncMock()
            svc.get_by_email.return_value = user
            MockService.return_value = svc
 
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as ac:
                resp = await ac.post(
                    "/api/auth/forgot-password",
                    json={"email": "test@example.com"},
                )
 
    app.dependency_overrides.clear()
    assert resp.status_code == 200
    assert resp.json()["message"] == "If this email exists, a reset link has been sent"

@pytest.mark.asyncio
async def test_reset_password_success():
    mock_db = AsyncMock()
    mock_db.commit = AsyncMock()
 
    async def override_db():
        yield mock_db
 
    app.dependency_overrides[get_db] = override_db
 
    expires = datetime.now(UTC) + timedelta(minutes=10)
    user = make_db_user(reset_token="tok", reset_token_expires=expires)
 
    with patch("src.api.auth.UserService") as MockService:
        with patch("src.api.auth.is_reset_token_valid", return_value=True):
            with patch("src.api.auth.get_password_hash", return_value="new_hashed"):
                svc = AsyncMock()
                svc.get_user_by_reset_token.return_value = user
                MockService.return_value = svc
 
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as ac:
                    resp = await ac.post(
                        "/api/auth/reset-password",
                        json={"token": "tok", "new_password": "newpass123"},
                    )
 
    app.dependency_overrides.clear()
    assert resp.status_code == 200
    assert "updated" in resp.json()["message"].lower()

@pytest.mark.asyncio
async def test_reset_password_expired_token():
    mock_db = AsyncMock()
 
    async def override_db():
        yield mock_db
 
    app.dependency_overrides[get_db] = override_db
 
    with patch("src.api.auth.UserService") as MockService:
        with patch("src.api.auth.is_reset_token_valid", return_value=False):
            svc = AsyncMock()
            svc.get_user_by_reset_token.return_value = make_db_user(
                reset_token="expired"
            )
            MockService.return_value = svc
 
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as ac:
                resp = await ac.post(
                    "/api/auth/reset-password",
                    json={"token": "expired", "new_password": "newpass123"},
                )
 
    app.dependency_overrides.clear()
    assert resp.status_code == 400