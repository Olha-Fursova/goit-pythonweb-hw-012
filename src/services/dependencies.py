"""
FastAPI dependency functions for authentication and authorization.
 
Provides reusable dependencies for extracting the current user
from a JWT token (with Redis caching) and enforcing role-based access.
"""
 
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union
 
from src.database.db import get_db
from src.services.auth import decode_access_token
from src.services.users import UserService
from src.services.redis import redis_client
from src.schemas import UserCache
 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
 
CACHE_TTL = 300  # seconds
 
 
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserCache:
    """
    Extract and return the currently authenticated user.
 
    First checks Redis cache using the user's ID as the key.
    If not cached, fetches the user from the database and stores
    the result in Redis for subsequent requests.
 
    :param token: JWT bearer token extracted from the Authorization header.
    :param db: Async database session.
    :return: The authenticated user as a UserCache Pydantic model.
    :raises HTTPException: 401 if the token is invalid or the user does not exist.
    """
    user_id = decode_access_token(token)
 
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
 
    cache_key = f"user:{user_id}"
 
    cached_user = await redis_client.get(cache_key)
    if cached_user:
        return UserCache.model_validate_json(cached_user).model_copy()
 
    service = UserService(db)
    user = await service.get_by_id(int(user_id))
 
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
 
    user_data = UserCache.model_validate({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": user.avatar,
        "confirmed": user.confirmed,
        "created_at": str(user.created_at),
        "role": user.role,
    })
 
    await redis_client.set(
        cache_key,
        user_data.model_dump_json(),
        ex=CACHE_TTL
    )
 
    return user_data
 
 
def require_role(allowed_roles: Union[str, List[str]]):
    """
    Return a dependency that enforces role-based access control.
 
    Can accept a single role string or a list of allowed roles.
    The returned dependency raises HTTP 403 if the current user's
    role is not in the allowed list.
 
    :param allowed_roles: A role string or list of role strings that are permitted.
    :return: An async dependency function that validates the user's role.
 
    Example::
 
        @router.delete("/admin/users/{id}")
        async def delete_user(
            current_user: UserCache = Depends(require_role("admin"))
        ):
            ...
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
 
    async def role_checker(
        current_user: UserCache = Depends(get_current_user)
    ) -> UserCache:
        """
        Check that the current user has one of the allowed roles.
 
        :param current_user: The authenticated user from get_current_user.
        :return: The current user if their role is allowed.
        :raises HTTPException: 403 if the user's role is not permitted.
        """
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
 
    return role_checker