import pytest
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_reset_token
)

def test_password_hashing_and_verification():
    """
    Verifies that hash_password successfully encrypts plaintext passwords,
    and verify_password correctly matches passwords against their bcrypt hashes.
    """
    password = "SecurePassword@123"
    hashed = hash_password(password)
    
    assert hashed != password
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    
    # Verification checks
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword@123", hashed) is False
    assert verify_password(password, "invalid_hash_format") is False

def test_jwt_token_flow():
    """
    Verifies that create_access_token generates valid signed JWT tokens,
    and decode_access_token correctly parses user_id and email claims or returns None if invalid.
    """
    user_id = "507f1f77bcf86cd799439011"
    email = "testuser@recruitsafe.com"
    
    token = create_access_token(user_id=user_id, email=email)
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Decrypt and assert claims
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["user_id"] == user_id
    assert payload["email"] == email
    assert "exp" in payload
    assert "iat" in payload

def test_jwt_invalid_token():
    """
    Verifies that decode_access_token returns None when parsing invalid, tampered, or malformed tokens.
    """
    assert decode_access_token("invalid.token.here") is None
    assert decode_access_token("") is None

def test_password_reset_token_generation():
    """
    Verifies that generate_reset_token returns a cryptographically secure URL-safe string.
    """
    token1 = generate_reset_token()
    token2 = generate_reset_token()
    
    assert isinstance(token1, str)
    assert len(token1) >= 32
    assert token1 != token2  # Unique
