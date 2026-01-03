#!/usr/bin/env python3
"""
Manual JWT testing script.
Run this to verify JWT token generation and validation works correctly.

Usage:
    cd backend
    uv run python test_jwt_manual.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.jwt_service import jwt_service, TokenExpiredError, InvalidTokenError
from src.services.refresh_token_service import refresh_token_service
import jwt as pyjwt
from datetime import datetime, UTC


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def test_jwt_generation():
    """Test JWT access token generation."""
    print_section("TEST 1: JWT Token Generation")

    # Generate token for a test user
    test_user_id = "test-user-123"
    token = jwt_service.generate_access_token(test_user_id)

    print(f"✅ Generated JWT token for user: {test_user_id}")
    print(f"\nToken (first 50 chars): {token[:50]}...")
    print(f"Token length: {len(token)} characters")

    # Decode the token to see its contents (without verification for display)
    decoded = pyjwt.decode(token, options={"verify_signature": False})

    print(f"\n📋 Token Payload:")
    print(f"   - Subject (user_id): {decoded.get('sub')}")
    print(f"   - Type: {decoded.get('type')}")
    print(f"   - Issued At: {datetime.fromtimestamp(decoded.get('iat'), tz=UTC)}")
    print(f"   - Expires At: {datetime.fromtimestamp(decoded.get('exp'), tz=UTC)}")

    # Calculate time until expiration
    exp_time = datetime.fromtimestamp(decoded.get('exp'), tz=UTC)
    time_until_exp = exp_time - datetime.now(UTC)
    minutes = time_until_exp.total_seconds() / 60
    print(f"   - Time until expiration: {minutes:.1f} minutes")

    return token, test_user_id


def test_jwt_validation(token: str, expected_user_id: str):
    """Test JWT access token validation."""
    print_section("TEST 2: JWT Token Validation")

    try:
        # Validate the token and extract user_id
        user_id = jwt_service.validate_access_token(token)

        print(f"✅ Token validation successful!")
        print(f"   - Extracted user_id: {user_id}")
        print(f"   - Expected user_id: {expected_user_id}")
        print(f"   - Match: {'✅ YES' if user_id == expected_user_id else '❌ NO'}")

        return True
    except TokenExpiredError as e:
        print(f"❌ Token expired: {e}")
        return False
    except InvalidTokenError as e:
        print(f"❌ Token invalid: {e}")
        return False


def test_invalid_token():
    """Test validation with invalid token."""
    print_section("TEST 3: Invalid Token Handling")

    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

    try:
        user_id = jwt_service.validate_access_token(invalid_token)
        print(f"❌ Should have failed but got user_id: {user_id}")
        return False
    except InvalidTokenError as e:
        print(f"✅ Correctly rejected invalid token")
        print(f"   - Error: {e}")
        return True


def test_refresh_token_generation():
    """Test refresh token generation and hashing."""
    print_section("TEST 4: Refresh Token Generation & Hashing")

    # Generate refresh token
    refresh_token = refresh_token_service.generate_refresh_token()
    print(f"✅ Generated refresh token (first 20 chars): {refresh_token[:20]}...")
    print(f"   - Length: {len(refresh_token)} characters")
    print(f"   - Type: URL-safe base64")

    # Hash the refresh token
    hashed = refresh_token_service.hash_refresh_token(refresh_token)
    print(f"\n✅ Hashed refresh token (SHA-256):")
    print(f"   - Hash: {hashed}")
    print(f"   - Length: {len(hashed)} characters")

    # Verify hashing is deterministic
    hashed2 = refresh_token_service.hash_refresh_token(refresh_token)
    print(f"\n✅ Hash is deterministic:")
    print(f"   - Hash 1: {hashed}")
    print(f"   - Hash 2: {hashed2}")
    print(f"   - Match: {'✅ YES' if hashed == hashed2 else '❌ NO'}")

    return refresh_token, hashed


def test_token_type_validation():
    """Test that only 'access' type tokens are accepted."""
    print_section("TEST 5: Token Type Validation")

    # Create a token with wrong type
    from datetime import timedelta

    payload = {
        "sub": "test-user",
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(minutes=30),
        "type": "refresh"  # Wrong type!
    }

    from src.config import settings
    wrong_type_token = pyjwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    try:
        user_id = jwt_service.validate_access_token(wrong_type_token)
        print(f"❌ Should have failed but got user_id: {user_id}")
        return False
    except InvalidTokenError as e:
        print(f"✅ Correctly rejected token with wrong type")
        print(f"   - Error: {e}")
        return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  JWT AUTHENTICATION TEST SUITE")
    print("=" * 60)

    results = []

    # Test 1 & 2: Generation and validation
    try:
        token, user_id = test_jwt_generation()
        results.append(("Token Generation", True))

        success = test_jwt_validation(token, user_id)
        results.append(("Token Validation", success))
    except Exception as e:
        print(f"\n❌ Error in token generation/validation: {e}")
        results.append(("Token Generation", False))
        results.append(("Token Validation", False))

    # Test 3: Invalid token
    try:
        success = test_invalid_token()
        results.append(("Invalid Token Handling", success))
    except Exception as e:
        print(f"\n❌ Error in invalid token test: {e}")
        results.append(("Invalid Token Handling", False))

    # Test 4: Refresh token
    try:
        test_refresh_token_generation()
        results.append(("Refresh Token Generation", True))
    except Exception as e:
        print(f"\n❌ Error in refresh token test: {e}")
        results.append(("Refresh Token Generation", False))

    # Test 5: Token type validation
    try:
        success = test_token_type_validation()
        results.append(("Token Type Validation", success))
    except Exception as e:
        print(f"\n❌ Error in token type validation: {e}")
        results.append(("Token Type Validation", False))

    # Print summary
    print_section("TEST SUMMARY")
    all_passed = all(result[1] for result in results)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10} {test_name}")

    print(f"\n{'=' * 60}")
    if all_passed:
        print("  🎉 ALL TESTS PASSED!")
    else:
        print("  ⚠️  SOME TESTS FAILED")
    print(f"{'=' * 60}\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
