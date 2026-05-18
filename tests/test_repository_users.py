"""
Unit tests for UserRepository.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.users import UserRepository
from src.database.models import User
from src.schemas import UserModel

def make_user(**kwargs) -> User:
    defaults = dict(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
        confirmed=False,
        verification_token="tok123",
        role="user",
        reset_token=None,
        reset_token_expires=None,
        avatar=None,
    )
    defaults.update(kwargs)
    user = MagicMock(spec=User)
    for k, v in defaults.items():
        setattr(user, k, v)
    return user

@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    return session

@pytest.fixture
def repo(mock_session):
    return UserRepository(mock_session)

@pytest.mark.asyncio
async def test_get_user_by_id_found(repo, mock_session):
    user = make_user(id=1)
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = result_mock
 
    result = await repo.get_user_by_id(1)
 
    assert result is user

@pytest.mark.asyncio
async def test_get_user_by_id_not_found(repo, mock_session):
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = result_mock
 
    result = await repo.get_user_by_id(999)
 
    assert result is None

@pytest.mark.asyncio
async def test_get_user_by_email_found(repo, mock_session):
    user = make_user(email="found@example.com")
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = result_mock
 
    result = await repo.get_user_by_email("found@example.com")
 
    assert result.email == "found@example.com"

@pytest.mark.asyncio
async def test_get_user_by_email_not_found(repo, mock_session):
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = result_mock
 
    result = await repo.get_user_by_email("nobody@example.com")
 
    assert result is None

@pytest.mark.asyncio
async def test_get_user_by_username(repo, mock_session):
    user = make_user(username="alice")
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = result_mock
 
    result = await repo.get_user_by_username("alice")
 
    assert result.username == "alice"

@pytest.mark.asyncio
async def test_get_user_by_reset_token(repo, mock_session):
    user = make_user(reset_token="reset-abc")
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = result_mock
 
    result = await repo.get_user_by_reset_token("reset-abc")
 
    assert result.reset_token == "reset-abc"

@pytest.mark.asyncio
async def test_create_user(repo, mock_session):
    body = UserModel(username="newuser", email="new@example.com", password="secret123")
 
    created_user = make_user(username="newuser", email="new@example.com")
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
 
    with patch("src.repository.users.get_password_hash", return_value="hashed_pw"):
        with patch("src.repository.users.uuid.uuid4", return_value="fake-uuid"):
            # simulate refresh setting attributes
            async def fake_refresh(obj):
                obj.id = 1
            mock_session.refresh.side_effect = fake_refresh

            with patch("src.repository.users.User") as MockUser:
                instance = MagicMock()
                instance.id = 1
                instance.username = "newuser"
                MockUser.return_value = instance
 
                result = await repo.create_user(body)
 
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_confirm_email_success(repo, mock_session):
    user = make_user(confirmed=False, verification_token="tok123")
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = result_mock
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
 
    result = await repo.confirm_email("tok123")
 
    assert user.confirmed is True
    assert user.verification_token is None

@pytest.mark.asyncio
async def test_confirm_email_invalid_token(repo, mock_session):
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = result_mock
 
    result = await repo.confirm_email("bad-token")
 
    assert result is None