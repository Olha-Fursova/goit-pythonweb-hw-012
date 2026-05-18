from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, UTC

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, ForgotPasswordModel, ResetPasswordModel
from src.services.users import UserService
from src.services.auth import (
    verify_password,
    create_access_token,
    create_reset_token,
    get_password_hash,
    is_reset_token_valid
)


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserModel,
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    email_user = await service.get_by_email(body.email)
    if email_user:
        raise HTTPException(status_code=409, detail="Email or username already exists")

    username_user = await service.get_by_username(body.username)
    if username_user:
        raise HTTPException(status_code=409, detail="Email or username already exists")

    user = await service.create_user(body)

    return user

@router.post("/login")
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    user = await service.get_by_username(body.username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Wrong password or username"
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=401,
            detail="Email not confirmed"
        )

    if not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Wrong password or username"
        )

    access_token = create_access_token(
        {"sub": str(user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/verify/{token}")
async def verify_email(
    token: str = Path(...),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    user = await service.confirm_email(token)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )

    return {"message": "Email verified successfully"}

@router.post("/forgot-password")
async def forgot_password(
    body: ForgotPasswordModel,
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    user = await service.get_by_email(body.email)

    if not user:
        return {"message": "If user exists, reset link was sent"}

    reset_token = create_reset_token()
    expires = datetime.now(UTC) + timedelta(minutes=15)

    user.reset_token = reset_token
    user.reset_token_expires = expires

    await db.commit()
    await db.refresh(user)

    return {
        "reset_token": reset_token
    }

@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordModel,
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    user = await service.get_user_by_reset_token(body.token)
    
    if not user or not user.reset_token_expires or not is_reset_token_valid(user.reset_token_expires):
        raise HTTPException(
            status_code=400,
            detail="Reset token expired"
        )

    user.hashed_password = get_password_hash(body.new_password)
    user.reset_token = None
    user.reset_token_expires = None

    await db.commit()

    return {"message": "Password updated successfully"}