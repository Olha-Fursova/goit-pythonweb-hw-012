"""
Integration tests for /api/contacts/* routes.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date

from src.database.models import Contact

def make_contact(**kwargs):
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

CONTACT_PAYLOAD = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "birthday": "1990-05-20",
    "additional_data": None,
}

@pytest.mark.asyncio
async def test_read_contacts(client):
    contacts = [make_contact(id=1), make_contact(id=2, email="jane@example.com")]
 
    with patch("src.api.contacts.ContactService") as MockSvc:
        svc = AsyncMock()
        svc.get_contacts.return_value = contacts
        MockSvc.return_value = svc
 
        resp = await client.get("/api/contacts/")
 
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

@pytest.mark.asyncio
async def test_create_contact(client):
    new_contact = make_contact(id=3)
 
    with patch("src.api.contacts.ContactService") as MockSvc:
        svc = AsyncMock()
        svc.create_contact.return_value = new_contact
        MockSvc.return_value = svc
 
        resp = await client.post("/api/contacts/", json=CONTACT_PAYLOAD)
 
    assert resp.status_code == 201

@pytest.mark.asyncio
async def test_read_contact_found(client):
    contact = make_contact(id=1)
 
    with patch("src.api.contacts.ContactService") as MockSvc:
        svc = AsyncMock()
        svc.get_contact.return_value = contact
        MockSvc.return_value = svc
 
        resp = await client.get("/api/contacts/1")
 
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_read_contact_not_found(client):
    with patch("src.api.contacts.ContactService") as MockSvc:
        svc = AsyncMock()
        svc.get_contact.return_value = None
        MockSvc.return_value = svc
 
        resp = await client.get("/api/contacts/999")
 
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_update_contact_found(client):
    updated = make_contact(id=1, first_name="Updated")
 
    with patch("src.api.contacts.ContactService") as MockSvc:
        svc = AsyncMock()
        svc.update_contact.return_value = updated
        MockSvc.return_value = svc
 
        resp = await client.put("/api/contacts/1", json=CONTACT_PAYLOAD)
 
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_update_contact_not_found(client):
    with patch("src.api.contacts.ContactService") as MockSvc:
        svc = AsyncMock()
        svc.update_contact.return_value = None
        MockSvc.return_value = svc
 
        resp = await client.put("/api/contacts/999", json=CONTACT_PAYLOAD)
 
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_remove_contact_found(client):
    contact = make_contact(id=1)
 
    with patch("src.api.contacts.ContactService") as MockSvc:
        svc = AsyncMock()
        svc.remove_contact.return_value = contact
        MockSvc.return_value = svc
 
        resp = await client.delete("/api/contacts/1")
 
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_remove_contact_not_found(client):
    with patch("src.api.contacts.ContactService") as MockSvc:
        svc = AsyncMock()
        svc.remove_contact.return_value = None
        MockSvc.return_value = svc
 
        resp = await client.delete("/api/contacts/999")
 
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_search_contacts(client):
    contacts = [make_contact(id=1)]
 
    with patch("src.api.contacts.ContactService") as MockSvc:
        svc = AsyncMock()
        svc.search_contacts.return_value = contacts
        MockSvc.return_value = svc
 
        resp = await client.get("/api/contacts/search?query=John")
 
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

@pytest.mark.asyncio
async def test_upcoming_birthdays(client):
    contacts = [make_contact(id=1)]
 
    with patch("src.api.contacts.ContactService") as MockSvc:
        svc = AsyncMock()
        svc.upcoming_birthdays.return_value = contacts
        MockSvc.return_value = svc
 
        resp = await client.get("/api/contacts/birthdays")
 
    assert resp.status_code == 200