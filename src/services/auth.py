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


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(minutes=30)

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload.get("sub")

    except JWTError:
        return None
    
def create_reset_token():
    return str(uuid.uuid4())

def is_reset_token_valid(expires_at: datetime) -> bool:
    return expires_at is not None and expires_at > datetime.now(UTC)