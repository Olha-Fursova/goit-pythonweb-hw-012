from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.users import UserRepository


class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def get_by_id(self, user_id: int):
        return await self.repository.get_user_by_id(user_id)

    async def get_by_email(self, email: str):
        return await self.repository.get_user_by_email(email)

    async def get_by_username(self, username: str):
        return await self.repository.get_user_by_username(username)
    
    async def get_user_by_reset_token(self, token: str):
        return await self.repository.get_user_by_reset_token(token)

    async def create_user(self, body):
        return await self.repository.create_user(body)
    
    async def confirm_email(self, token):
        return await self.repository.confirm_email(token)