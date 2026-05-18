"""
Unit tests for ContactRepository.
"""

import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.database.models import Contact, User
from src.schemas import ContactModel

def make_contact(**kwargs) -> Contact:
    defaults = dict(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        birthday=date(1990, 5, 20),
        additional_data=None,
        user_id=1,
    )
    defaults.update(kwargs)
    c = MagicMock(spec=Contact)
    for k, v in defaults.items():
        setattr(c, k, v)
    return c

def make_user(id: int = 1) -> MagicMock:
    u = MagicMock(spec=User)
    u.id = id
    return u

@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def repo(mock_session):
    return ContactRepository(mock_session)

@pytest.mark.asyncio
async def test_get_contacts(repo, mock_session):
    contacts = [make_contact(id=1), make_contact(id=2)]
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = contacts
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    mock_session.execute.return_value = result_mock
 
    user = make_user()
    result = await repo.get_contacts(0, 100, user)
 
    assert len(result) == 2

@pytest.mark.asyncio
async def test_get_contact_by_id_found(repo, mock_session):
    contact = make_contact(id=5)
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = contact
    mock_session.execute.return_value = result_mock
 
    user = make_user()
    result = await repo.get_contact_by_id(5, user)
 
    assert result.id == 5

@pytest.mark.asyncio
async def test_get_contact_by_id_not_found(repo, mock_session):
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = result_mock
 
    user = make_user()
    result = await repo.get_contact_by_id(999, user)
 
    assert result is None
 
@pytest.mark.asyncio
async def test_create_contact(repo, mock_session):
    body = ContactModel(
        first_name="Jane",
        last_name="Smith",
        email="jane@example.com",
        phone="9876543210",
        birthday=date(1995, 3, 15),
    )
    user = make_user()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
 
    from unittest.mock import patch
    with patch("src.repository.contacts.Contact") as MockContact:
        instance = MagicMock()
        instance.id = 1
        MockContact.return_value = instance
 
        result = await repo.create_contact(body, user)
 
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
 
@pytest.mark.asyncio
async def test_remove_contact_found(repo, mock_session):
    contact = make_contact(id=1)
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = contact
    mock_session.execute.return_value = result_mock
    mock_session.delete = AsyncMock()
    mock_session.commit = AsyncMock()
 
    user = make_user()
    result = await repo.remove_contact(1, user)
 
    assert result is contact
    mock_session.delete.assert_awaited_once_with(contact)

@pytest.mark.asyncio
async def test_remove_contact_not_found(repo, mock_session):
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = result_mock
 
    user = make_user()
    result = await repo.remove_contact(999, user)
 
    assert result is None

@pytest.mark.asyncio
async def test_update_contact_found(repo, mock_session):
    contact = make_contact(id=1)
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = contact
    mock_session.execute.return_value = result_mock
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
 
    body = ContactModel(
        first_name="Updated",
        last_name="Name",
        email="updated@example.com",
        phone="0000000000",
        birthday=date(1990, 1, 1),
    )
    user = make_user()
    result = await repo.update_contact(1, body, user)
 
    mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_contact_not_found(repo, mock_session):
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = result_mock
 
    body = ContactModel(
        first_name="X",
        last_name="Y",
        email="xy@example.com",
        phone="111",
        birthday=date(2000, 1, 1),
    )
    user = make_user()
    result = await repo.update_contact(999, body, user)
 
    assert result is None
 
@pytest.mark.asyncio
async def test_upcoming_birthdays(repo, mock_session):
    today = date.today()
    contact_soon = make_contact(birthday=date(1990, today.month, today.day))
    contact_far = make_contact(
        birthday=date(1990, 1, 1) if today.month != 1 else date(1990, 6, 1)
    )
 
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = [contact_soon, contact_far]
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock
    mock_session.execute.return_value = result_mock
 
    user = make_user()
    result = await repo.upcoming_birthdays(user)
 
    assert contact_soon in result