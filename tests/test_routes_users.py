"""
Integration tests for /api/users/* routes.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.asyncio
async def test_read_me(client, mock_user):
    resp = await client.get("/api/users/me")
 
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == mock_user.username
    assert data["email"] == mock_user.email
    assert data["role"] == "user"

@pytest.mark.asyncio
async def test_admin_endpoint_forbidden_for_user(client):
    """Regular user cannot access admin endpoint."""
    resp = await client.get("/api/users/admin/all-users")
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_admin_endpoint_allowed_for_admin(admin_client, mock_admin):
    resp = await admin_client.get("/api/users/admin/all-users")
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_update_avatar_forbidden_for_user(client):
    """Regular user cannot update avatar (admin only)."""
    from io import BytesIO
 
    resp = await client.patch(
        "/api/users/avatar",
        files={"file": ("avatar.jpg", BytesIO(b"fake-image"), "image/jpeg")},
    )
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_update_avatar_invalid_type(admin_client, mock_admin, db_session):
    """Admin uploading invalid file type gets 400."""
    from io import BytesIO
 
    with patch("src.api.users.UserService") as MockSvc:
        svc = AsyncMock()
        svc.get_by_id.return_value = MagicMock(id=mock_admin.id, avatar=None)
        MockSvc.return_value = svc
 
        resp = await admin_client.patch(
            "/api/users/avatar",
            files={"file": ("doc.pdf", BytesIO(b"data"), "application/pdf")},
        )
 
    assert resp.status_code == 400

@pytest.mark.asyncio
async def test_update_avatar_success(admin_client, mock_admin, db_session):
    """Admin can successfully update avatar."""
    from io import BytesIO
    from unittest.mock import patch, MagicMock, mock_open, AsyncMock

    db_user = MagicMock()
    db_user.id = mock_admin.id
    db_user.avatar = None

    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock()

    with patch("src.api.users.UserService") as MockSvc:
        with patch("src.api.users.upload_avatar", return_value="https://cdn.example.com/avatar.jpg"):
            with patch("builtins.open", mock_open()):
                with patch("os.path.exists", return_value=True):
                    with patch("os.remove"):
                        svc = AsyncMock()
                        svc.get_by_id.return_value = db_user
                        MockSvc.return_value = svc

                        resp = await admin_client.patch(
                            "/api/users/avatar",
                            files={"file": ("avatar.jpg", BytesIO(b"fake-image-data"), "image/jpeg")},
                        )

    assert resp.status_code == 200
    assert "avatar" in resp.json()