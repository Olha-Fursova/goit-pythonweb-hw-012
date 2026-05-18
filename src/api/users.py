"""
API routes for user profile management.
"""
 
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
import shutil
import os
import uuid
 
from src.services.dependencies import get_current_user, require_role
from src.services.cloudinary import upload_avatar
from src.services.users import UserService
from src.database.db import get_db
from src.core.limiter import limiter
from src.schemas import UserCache
from src.services.redis import redis_client
 
router = APIRouter(prefix="/users", tags=["users"])
 
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/jpg"]
 
 
@router.get("/me")
@limiter.limit("5/minute")
async def read_me(
    request: Request,
    current_user: UserCache = Depends(get_current_user)
):
    """
    Return the current authenticated user's profile.
 
    :param request: The incoming HTTP request.
    :param current_user: The currently authenticated user from cache.
    :return: User profile data as a dict.
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "avatar": current_user.avatar,
        "confirmed": current_user.confirmed,
        "created_at": current_user.created_at,
        "role": current_user.role,
    }
 
 
@router.patch("/avatar")
async def update_avatar(
    file: UploadFile = File(...),
    current_user: UserCache = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the avatar for the current admin user.
 
    Only users with the 'admin' role can update avatars.
    The file is uploaded to Cloudinary and the URL is saved to the database.
 
    :param file: Uploaded image file (JPEG or PNG).
    :param current_user: The currently authenticated admin user.
    :param db: Async database session.
    :return: Dict with the new avatar URL.
    :raises HTTPException: If the file type is invalid.
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type")
 
    unique_id = str(uuid.uuid4())
    file_path = f"/tmp/temp_{current_user.id}_{unique_id}.jpg"
 
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file.file.close()
 
    avatar_url = upload_avatar(file_path, f"user_{current_user.id}_{unique_id}")
 
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass
 
    # Update the actual DB model, not the Pydantic cache object
    service = UserService(db)
    user_db = await service.get_by_id(current_user.id)
    if user_db is None:
        raise HTTPException(status_code=404, detail="User not found")
 
    user_db.avatar = avatar_url
    await db.commit()
    await db.refresh(user_db)
 
    # Invalidate Redis cache so next request gets fresh data
    cache_key = f"user:{current_user.id}"
    await redis_client.delete(cache_key)
 
    return {"avatar": avatar_url}
 
 
@router.get("/admin/all-users")
async def get_all_users(
    current_user: UserCache = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    Return a list of all users. Admin only.
 
    :param current_user: The currently authenticated admin user.
    :param db: Async database session.
    :return: Confirmation message (extend with real user list as needed).
    """
    return {"message": "Only admin can see this"}