from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.services.auth import decode_access_token
from src.services.users import UserService
from src.services.redis import redis_client
from src.schemas import UserCache

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)

CACHE_TTL = 300 


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
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

async def get_current_admin_user(
    current_user: UserCache = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user