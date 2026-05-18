"""
Authentication helper functions.
 
Provides password hashing, JWT token creation/decoding,
and password reset token utilities.
"""
 
from datetime import datetime, timedelta, UTC
import uuid
 
from jose import jwt, JWTError
from passlib.context import CryptContext
 
from src.conf.config import settings
 
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
 
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
 
 
def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain-text password against its hashed version.
 
    :param plain: The plain-text password provided by the user.
    :param hashed: The hashed password stored in the database.
    :return: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain, hashed)
 
 
def get_password_hash(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
 
    :param password: The plain-text password to hash.
    :return: The hashed password string.
    """
    return pwd_context.hash(password)
 
 
def create_access_token(data: dict) -> str:
    """
    Create a signed JWT access token with a 30-minute expiry.
 
    :param data: Payload data to encode into the token (e.g. ``{"sub": user_id}``).
    :return: Encoded JWT token string.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
 
 
def decode_access_token(token: str) -> str | None:
    """
    Decode a JWT access token and return the subject claim.
 
    :param token: The JWT token string to decode.
    :return: The ``sub`` value (user ID as string) if valid, or None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
 
 
def create_reset_token() -> str:
    """
    Generate a unique UUID-based password reset token.
 
    :return: A UUID4 string to be used as a one-time reset token.
    """
    return str(uuid.uuid4())
 
 
def is_reset_token_valid(expires_at: datetime) -> bool:
    """
    Check whether a password reset token has not yet expired.
 
    :param expires_at: The expiry datetime of the token (timezone-aware).
    :return: True if the token is still valid, False if expired or None.
    """
    return expires_at is not None and expires_at > datetime.now(UTC)
 