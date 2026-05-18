"""
Authentication routes: signup, login, email verification, password reset.
"""
 
from fastapi import APIRouter, Depends, HTTPException, status, Path, BackgroundTasks
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
    is_reset_token_valid,
)
from src.services.email import send_reset_password_email, send_verification_email
 
 
router = APIRouter(prefix="/auth", tags=["auth"])
 
 
@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.
 
    After successful registration, a verification email is sent
    to the provided address. The account cannot be used until
    the email is confirmed.
 
    :param body: Registration data (username, email, password).
    :param background_tasks: FastAPI background task runner.
    :param db: Async database session.
    :return: Created user data.
    :raises HTTPException: 409 if email or username already exists.
    """
    service = UserService(db)
 
    if await service.get_by_email(body.email):
        raise HTTPException(status_code=409, detail="Email or username already exists")
 
    if await service.get_by_username(body.username):
        raise HTTPException(status_code=409, detail="Email or username already exists")
 
    user = await service.create_user(body)
 
    background_tasks.add_task(
        send_verification_email,
        email=user.email,
        token=user.verification_token,
    )
 
    return user
 
 
@router.post("/login")
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate a user and return a JWT access token.
 
    :param body: OAuth2 form with username and password.
    :param db: Async database session.
    :return: Dict with access_token and token_type.
    :raises HTTPException: 401 if credentials are invalid or email not confirmed.
    """
    service = UserService(db)
 
    user = await service.get_by_username(body.username)
 
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Wrong password or username",
        )
 
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not confirmed",
        )
 
    if not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Wrong password or username",
        )
 
    access_token = create_access_token({"sub": str(user.id)})
 
    return {"access_token": access_token, "token_type": "bearer"}
 
 
@router.get("/verify/{token}")
async def verify_email(
    token: str = Path(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Confirm a user's email address using the verification token.
 
    The token is sent to the user's email after registration.
 
    :param token: The UUID verification token from the email link.
    :param db: Async database session.
    :return: Success message.
    :raises HTTPException: 400 if the token is invalid or already used.
    """
    service = UserService(db)
    user = await service.confirm_email(token)
 
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )
 
    return {"message": "Email verified successfully"}
 
 
@router.post("/forgot-password")
async def forgot_password(
    body: ForgotPasswordModel,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Initiate a password reset by sending a reset link to the user's email.
 
    For security, always returns the same message regardless of whether
    the email exists in the database (prevents user enumeration).
 
    :param body: Request body containing the user's email.
    :param background_tasks: FastAPI background task runner.
    :param db: Async database session.
    :return: Generic success message.
    """
    service = UserService(db)
    user = await service.get_by_email(body.email)

    if not user:
        return {"message": "If this email exists, a reset link has been sent"}
 
    reset_token = create_reset_token()
    expires = datetime.now(UTC) + timedelta(minutes=15)
 
    user.reset_token = reset_token
    user.reset_token_expires = expires
    await db.commit()
    await db.refresh(user)
 
    background_tasks.add_task(
        send_reset_password_email,
        email=user.email,
        token=reset_token,
    )
 
    return {"message": "If this email exists, a reset link has been sent"}
 
 
@router.get("/reset-password-confirm/{token}")
async def reset_password_confirm(
    token: str = Path(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Validate a password reset token (simulates clicking the email link).
 
    This endpoint is hit when the user clicks the link in their email.
    It confirms the token is valid and not expired.
 
    :param token: The UUID reset token from the email link.
    :param db: Async database session.
    :return: Message instructing the user to submit their new password.
    :raises HTTPException: 400 if the token is invalid or expired.
    """
    service = UserService(db)
    user = await service.get_user_by_reset_token(token)
 
    if not user or not is_reset_token_valid(user.reset_token_expires):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token is invalid or has expired",
        )
 
    return {
        "message": "Token is valid. Submit your new password to /api/auth/reset-password",
        "token": token,
    }
 
 
@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordModel,
    db: AsyncSession = Depends(get_db),
):
    """
    Set a new password using a valid reset token.
 
    The token must have been obtained from the email link and
    must not be expired (15-minute window).
 
    :param body: Reset data containing the token and new password.
    :param db: Async database session.
    :return: Success message.
    :raises HTTPException: 400 if the token is invalid or expired.
    """
    service = UserService(db)
    user = await service.get_user_by_reset_token(body.token)
 
    if not user or not is_reset_token_valid(user.reset_token_expires):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token expired",
        )
 
    user.hashed_password = get_password_hash(body.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    await db.commit()
 
    return {"message": "Password updated successfully"}