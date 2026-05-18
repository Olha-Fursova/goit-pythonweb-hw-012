"""
Repository for user database operations.
 
Provides low-level async database access methods for the User model.
"""
 
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
 
from src.database.models import User
from src.schemas import UserModel
from src.services.auth import get_password_hash
 
 
class UserRepository:
    """Handles all database operations for the User model."""
 
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.
 
        :param session: Async SQLAlchemy session.
        """
        self.db = session
 
    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their primary key.
 
        :param user_id: The user's ID.
        :return: The User object or None if not found.
        """
        stmt = select(User).filter_by(id=user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
 
    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email address.
 
        :param email: The email address to look up.
        :return: The User object or None if not found.
        """
        stmt = select(User).filter_by(email=email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
 
    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their username.
 
        :param username: The username to look up.
        :return: The User object or None if not found.
        """
        stmt = select(User).filter_by(username=username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
 
    async def get_user_by_reset_token(self, token: str) -> User | None:
        """
        Retrieve a user by their password reset token.
 
        :param token: The UUID reset token to look up.
        :return: The User object or None if not found.
        """
        stmt = select(User).filter_by(reset_token=token)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
 
    async def create_user(self, body: UserModel) -> User:
        """
        Create and persist a new user in the database.
 
        Hashes the password and generates a UUID email verification token
        before saving. The new user is assigned the ``user`` role by default
        and starts with ``confirmed=False``.
 
        :param body: UserModel schema containing username, email, and password.
        :return: The newly created and refreshed User object.
        """
        verification_token = str(uuid.uuid4())
        user = User(
            username=body.username,
            email=body.email,
            hashed_password=get_password_hash(body.password),
            verification_token=verification_token,
            confirmed=False,
            role="user"
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
 
    async def confirm_email(self, token: str) -> User | None:
        """
        Mark a user's email as confirmed using their verification token.
 
        Clears the ``verification_token`` field after successful confirmation
        so the token cannot be reused.
 
        :param token: The UUID verification token from the email link.
        :return: The updated User object, or None if the token is invalid.
        """
        stmt = select(User).filter_by(verification_token=token)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
 
        if not user:
            return None
 
        user.confirmed = True
        user.verification_token = None
 
        await self.db.commit()
        await self.db.refresh(user)
        return user