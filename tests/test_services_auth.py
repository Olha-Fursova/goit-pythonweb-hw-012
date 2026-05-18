"""
Unit tests for src/services/auth.py.
"""

from datetime import datetime, timedelta, UTC

from src.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    create_reset_token,
    is_reset_token_valid,
)

def test_password_hash_and_verify():
    plain = "mysecret"
    hashed = get_password_hash(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)

def test_verify_wrong_password():
    hashed = get_password_hash("correct")
    assert not verify_password("wrong", hashed)

def test_create_and_decode_access_token():
    token = create_access_token({"sub": "42"})
    result = decode_access_token(token)
    assert result == "42"

def test_decode_invalid_token():
    result = decode_access_token("not.a.valid.token")
    assert result is None

def test_decode_expired_token():
    from jose import jwt
    from src.conf.config import settings
 
    payload = {"sub": "1", "exp": datetime.now(UTC) - timedelta(seconds=1)}
    expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
 
    result = decode_access_token(expired_token)
    assert result is None

def test_create_reset_token_is_uuid():
    import re
    token = create_reset_token()
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    assert re.match(uuid_pattern, token)

def test_is_reset_token_valid_future():
    future = datetime.now(UTC) + timedelta(minutes=10)
    assert is_reset_token_valid(future) is True

def test_is_reset_token_valid_past():
    past = datetime.now(UTC) - timedelta(minutes=1)
    assert is_reset_token_valid(past) is False

def test_is_reset_token_valid_none():
    assert is_reset_token_valid(None) is False