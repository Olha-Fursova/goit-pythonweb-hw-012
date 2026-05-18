"""
Contact service layer.
 
Delegates contact-related business logic to the ContactRepository.
"""
 
from sqlalchemy.ext.asyncio import AsyncSession
 
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel
from src.database.models import User
 
 
class ContactService:
    """Service class for contact operations."""
 
    def __init__(self, db: AsyncSession):
        """
        Initialize the ContactService with a database session.
 
        :param db: Async database session.
        """
        self.contact_repository = ContactRepository(db)
 
    async def create_contact(self, body: ContactModel, user: User):
        """
        Create a new contact for the given user.
 
        :param body: Contact data to create.
        :param user: The owner of the contact.
        :return: The newly created Contact object.
        """
        return await self.contact_repository.create_contact(body, user)
 
    async def get_contacts(self, skip: int, limit: int, user: User):
        """
        Return a paginated list of contacts for the given user.
 
        :param skip: Number of records to skip.
        :param limit: Maximum number of records to return.
        :param user: The owner of the contacts.
        :return: List of Contact objects.
        """
        return await self.contact_repository.get_contacts(skip, limit, user)
 
    async def get_contact(self, contact_id: int, user: User):
        """
        Return a single contact by ID for the given user.
 
        :param contact_id: The contact's primary key.
        :param user: The owner of the contact.
        :return: The Contact object or None if not found.
        """
        return await self.contact_repository.get_contact_by_id(contact_id, user)
 
    async def update_contact(self, contact_id: int, body: ContactModel, user: User):
        """
        Update an existing contact's data.
 
        :param contact_id: The contact's primary key.
        :param body: Updated contact data.
        :param user: The owner of the contact.
        :return: The updated Contact object or None if not found.
        """
        return await self.contact_repository.update_contact(contact_id, body, user)
 
    async def remove_contact(self, contact_id: int, user: User):
        """
        Delete a contact by ID.
 
        :param contact_id: The contact's primary key.
        :param user: The owner of the contact.
        :return: The deleted Contact object or None if not found.
        """
        return await self.contact_repository.remove_contact(contact_id, user)
 
    async def search_contacts(self, query: str, user: User):
        """
        Search contacts by first name, last name, or email.
 
        :param query: The search string.
        :param user: The owner of the contacts.
        :return: List of matching Contact objects.
        """
        return await self.contact_repository.search_contacts(query, user)
 
    async def upcoming_birthdays(self, user: User):
        """
        Return contacts with birthdays in the next 7 days.
 
        :param user: The owner of the contacts.
        :return: List of Contact objects with upcoming birthdays.
        """
        return await self.contact_repository.upcoming_birthdays(user)