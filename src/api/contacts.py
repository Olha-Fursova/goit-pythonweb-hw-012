"""
API routes for contact management.
 
Provides CRUD operations, search, and birthday lookup
for the authenticated user's contacts.
"""
 
from typing import List
 
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
 
from src.database.db import get_db
from src.database.models import User
from src.services.dependencies import get_current_user
from src.schemas import ContactModel, ContactResponse
from src.services.contacts import ContactService
 
router = APIRouter(prefix="/contacts", tags=["contacts"])
 
 
@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return a paginated list of the current user's contacts.
 
    :param skip: Number of records to skip (for pagination).
    :param limit: Maximum number of records to return.
    :param db: Async database session.
    :param current_user: The currently authenticated user.
    :return: List of contacts.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, current_user)
    return contacts
 
 
@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new contact for the current user.
 
    :param body: Contact data to create.
    :param db: Async database session.
    :param current_user: The currently authenticated user.
    :return: The newly created contact.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, current_user)
 
 
@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactModel,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing contact by ID.
 
    :param body: Updated contact data.
    :param contact_id: ID of the contact to update.
    :param db: Async database session.
    :param current_user: The currently authenticated user.
    :return: The updated contact.
    :raises HTTPException: 404 if the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, current_user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
 
 
@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a contact by ID.
 
    :param contact_id: ID of the contact to delete.
    :param db: Async database session.
    :param current_user: The currently authenticated user.
    :return: The deleted contact.
    :raises HTTPException: 404 if the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, current_user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
 
 
@router.get("/search", response_model=List[ContactResponse])
async def search_contacts(
    query: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search contacts by first name, last name, or email.
 
    :param query: Search string to match against contact fields.
    :param db: Async database session.
    :param current_user: The currently authenticated user.
    :return: List of matching contacts.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.search_contacts(query, current_user)
    return contacts
 
 
@router.get("/birthdays", response_model=List[ContactResponse])
async def upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return contacts with birthdays in the next 7 days.
 
    :param db: Async database session.
    :param current_user: The currently authenticated user.
    :return: List of contacts with upcoming birthdays.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.upcoming_birthdays(current_user)
    return contacts
 
 
@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return a single contact by ID.
 
    :param contact_id: ID of the contact to retrieve.
    :param db: Async database session.
    :param current_user: The currently authenticated user.
    :return: The requested contact.
    :raises HTTPException: 404 if the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, current_user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact