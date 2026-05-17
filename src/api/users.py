from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import shutil
import os
import uuid

from src.database.models import User
from src.services.dependencies import get_current_user
from src.services.cloudinary import upload_avatar
from src.database.db import get_db
from src.core.limiter import limiter

router = APIRouter(prefix="/users", tags=["users"])

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/jpg"]

@router.get("/me")
@limiter.limit("5/minute")
async def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "avatar": current_user.avatar,
        "confirmed": current_user.confirmed,
        "created_at": current_user.created_at
    }

@router.patch("/avatar")
async def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    unique_id = str(uuid.uuid4())

    file_path = f"temp_{current_user.id}_{unique_id}.jpg"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file.file.close()

    avatar_url = upload_avatar(
        file_path,
        f"user_{current_user.id}_{unique_id}"
    )

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass

    current_user.avatar = avatar_url

    await db.commit()
    await db.refresh(current_user)

    return {
        "avatar": avatar_url
    }