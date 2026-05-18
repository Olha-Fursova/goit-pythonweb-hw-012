"""
User service layer.
 
Delegates user-related business logic to the UserRepository.
"""
 
from sqlalchemy.ext.asyncio import AsyncSession
 
from src.repository.users import UserRepository
 
 
class UserService:
    """Service class for user operations."""
 
    def __init__(self, db: AsyncSession):
        """
        Initialize the UserService with a database session.
 
        :param db: Async database session.
        """
        self.repository = UserRepository(db)
 
    async def get_by_id(self, user_id: int):
        """
        Retrieve a user by their ID.
 
        :param user_id: The user's primary key.
        :return: The User object or None if not found.
        """
        return await self.repository.get_user_by_id(user_id)
 
    async def get_by_email(self, email: str):
        """
        Retrieve a user by their email address.
 
        :param email: The user's email address.
        :return: The User object or None if not found.
        """
        return await self.repository.get_user_by_email(email)
 
    async def get_by_username(self, username: str):
        """
        Retrieve a user by their username.
 
        :param username: The user's username.
        :return: The User object or None if not found.
        """
        return await self.repository.get_user_by_username(username)
 
    async def get_user_by_reset_token(self, token: str):
        """
        Retrieve a user by their password reset token.
 
        :param token: The UUID reset token.
        :return: The User object or None if not found.
        """
        return await self.repository.get_user_by_reset_token(token)
 
    async def create_user(self, body):
        """
        Create a new user account.
 
        :param body: UserModel schema with registration data.
        :return: The newly created User object.
        """
        return await self.repository.create_user(body)
 
    async def confirm_email(self, token: str):
        """
        Confirm a user's email address using a verification token.
 
        :param token: The UUID verification token from the email link.
        :return: The confirmed User object, or None if token is invalid.
        """
        return await self.repository.confirm_email(token)