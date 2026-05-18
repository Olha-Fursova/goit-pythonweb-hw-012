"""
Repository for contact database operations.
 
Provides low-level async database access methods for the Contact model.
"""
 
from typing import List
from datetime import date, timedelta
 
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
 
from src.database.models import Contact, User
from src.schemas import ContactModel
 
 
class ContactRepository:
    """Handles all database operations for the Contact model."""
 
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.
 
        :param session: Async SQLAlchemy session.
        """
        self.db = session
 
    async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
        """
        Return a paginated list of contacts belonging to the given user.
 
        :param skip: Number of records to skip (offset).
        :param limit: Maximum number of records to return.
        :param user: The owner whose contacts to fetch.
        :return: List of Contact objects.
        """
        stmt = select(Contact).filter_by(user_id=user.id).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
 
    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Return a single contact by ID, scoped to the given user.
 
        :param contact_id: The contact's primary key.
        :param user: The owner of the contact.
        :return: The Contact object or None if not found.
        """
        stmt = select(Contact).filter_by(id=contact_id, user_id=user.id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()
 
    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """
        Create and persist a new contact in the database.
 
        :param body: ContactModel schema with the contact's data.
        :param user: The owner of the new contact.
        :return: The newly created and refreshed Contact object.
        """
        contact = Contact(**body.model_dump(), user_id=user.id)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact
 
    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Delete a contact by ID, scoped to the given user.
 
        :param contact_id: The contact's primary key.
        :param user: The owner of the contact.
        :return: The deleted Contact object, or None if not found.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact
 
    async def update_contact(
        self, contact_id: int, body: ContactModel, user: User
    ) -> Contact | None:
        """
        Update an existing contact's fields.
 
        All fields from the provided body are applied to the contact.
 
        :param contact_id: The contact's primary key.
        :param body: ContactModel schema with updated data.
        :param user: The owner of the contact.
        :return: The updated Contact object, or None if not found.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.model_dump().items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact
 
    async def search_contacts(self, query: str, user: User) -> List[Contact]:
        """
        Search contacts by first name, last name, or email (case-insensitive).
 
        :param query: The search string to match against contact fields.
        :param user: The owner whose contacts to search.
        :return: List of matching Contact objects.
        """
        stmt = select(Contact).where(
            Contact.user_id == user.id,
            or_(
                Contact.first_name.ilike(f"%{query}%"),
                Contact.last_name.ilike(f"%{query}%"),
                Contact.email.ilike(f"%{query}%"),
            )
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
 
    async def upcoming_birthdays(self, user: User) -> List[Contact]:
        """
        Return contacts whose birthday falls within the next 7 days.
 
        Compares the contact's birthday (month and day) against today's
        date and the date 7 days from now, using the current year.
 
        :param user: The owner whose contacts to check.
        :return: List of Contact objects with upcoming birthdays.
        """
        today = date.today()
        next_week = today + timedelta(days=7)
 
        contacts = await self.db.execute(
            select(Contact).filter_by(user_id=user.id)
        )
 
        result = []
        for contact in contacts.scalars().all():
            birthday_this_year = contact.birthday.replace(year=today.year)
            if today <= birthday_this_year <= next_week:
                result.append(contact)
 
        return result