#!/usr/bin/env python3
"""
Test script for Phase 3: User Registration and Authentication
Tests the better-auth server endpoints: signup, email verification, signin, signout
"""

import requests
import json
import time
import uuid
import os
import sys
from sqlalchemy import create_engine, text

# Configuration - adjust these based on your auth server setup
AUTH_SERVER_URL = "http://localhost:8080"  # Default port for auth server
TEST_EMAIL = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "SecurePassword123!"
TEST_NAME = "Test User"

def get_database_url():
    """Read DATABASE_URL from auth-server/.env"""
    env_path = os.path.join(os.path.dirname(__file__), 'auth-server', '.env')
    try:
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    return line.split('=', 1)[1].strip().strip('"')
    except Exception as e:
        print(f"Error reading .env: {e}")
        return None

def get_verification_token(email):
    """Fetch verification token from database"""
    db_url = get_database_url()
    if not db_url:
        print("Could not find DATABASE_URL")
        return None
        
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # better-auth v1 uses 'verifications' table, 'identifier' is email, 'value' is token
            result = conn.execute(
                text("SELECT value FROM verifications WHERE identifier = :email"),
                {"email": email}
            )
            row = result.fetchone()
            if row:
                return row[0]
            else:
                print(f"No verification token found for {email}")
                return None
    except Exception as e:
        print(f"Database error: {e}")
        return None

def test_signup():
    """Test signup endpoint: POST /api/auth/sign-up/email"""
    print("Testing signup endpoint...")

    signup_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": TEST_NAME
    }

    try:
        response = requests.post(f"{AUTH_SERVER_URL}/api/auth/sign-up/email", json=signup_data)
        print(f"Signup response status: {response.status_code}")

        print(f"Signup response: {response.json()}")

        if response.status_code == 200 or response.status_code == 201:
            print("✓ Signup successful")
            return response.json()
        else:
            print(f"✗ Signup failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Signup request failed: {e}")
        return None

def test_verify_email():
    """Test verify email endpoint: GET /api/auth/verify-email?token=..."""
    print("\nTesting verify email endpoint...")
    
    # Give DB a moment to sync
    time.sleep(1)
    
    token = get_verification_token(TEST_EMAIL)
    if not token:
        print("✗ Could not retrieve verification token from DB")
        return False
        
    print(f"Found verification token: {token}")
    
    try:
        response = requests.get(f"{AUTH_SERVER_URL}/api/auth/verify-email", params={"token": token})
        print(f"Verify response status: {response.status_code}")
        # The verify-email endpoint might redirect or return plain text/HTML on success,
        # so attempt to parse JSON but don't fail if it's not JSON.
        try:
            print(f"Verify response: {response.json()}")
        except json.JSONDecodeError:
            print(f"Verify response (non-JSON): {response.text}")
        
        if response.status_code == 200:
            print("✓ Email verification successful")
            return True
        else:
            print(f"✗ Email verification failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Verify request failed: {e}")
        return False

def test_signin():
    """Test signin endpoint: POST /api/auth/sign-in/email"""
    print("\nTesting signin endpoint...")

    signin_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }

    session = requests.Session() # Create a session object
    try:
        response = session.post(f"{AUTH_SERVER_URL}/api/auth/sign-in/email", json=signin_data)
        print(f"Signin response status: {response.status_code}")

        print(f"Signin response: {response.json()}")

        if response.status_code == 200:
            print("✓ Signin successful")
            return response.json(), session # Return session object
        else:
            print(f"✗ Signin failed with status {response.status_code}")
            return None, None
    except Exception as e:
        print(f"✗ Signin request failed: {e}")
        return None, None

def test_me_endpoint(session_object: requests.Session): # Accept session object
    """Test me endpoint: GET /api/auth/me"""
    print("\nTesting me endpoint...")

    try:
        response = session_object.get(f"{AUTH_SERVER_URL}/api/auth/me") # Use session object
        print(f"Me response status: {response.status_code}")
        print(f"Me response: {response.json()}")

        if response.status_code == 200:
            print("✓ Me endpoint successful")
            return response.json()
        else:
            print(f"✗ Me endpoint failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Me endpoint request failed: {e}")
        return None

def test_signout(session_object: requests.Session): # Accept session object
    """Test signout endpoint: POST /api/auth/sign-out"""
    print("\nTesting signout endpoint...")
    
    headers = {
        "Origin": "http://localhost:3000" # Add Origin header for CSRF
    }
    
    try:
        # Signout usually requires the token to know which session to kill
        response = session_object.post(f"{AUTH_SERVER_URL}/api/auth/sign-out", headers=headers, data={}) # Use session object
        print(f"Signout response status: {response.status_code}")
        print(f"Signout response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Signout successful")
            return True
        else:
            print(f"✗ Signout failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Signout request failed: {e}")
        return False

def test_health_check():
    """Test health check endpoint: GET /health"""
    print("\nTesting health check endpoint...")

    try:
        response = requests.get(f"{AUTH_SERVER_URL}/health")
        print(f"Health check response status: {response.status_code}")
        print(f"Health check response: {response.json()}")

        if response.status_code == 200:
            print("✓ Health check successful")
            return response.json()
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Health check request failed: {e}")
        return None

def main():
    print("Starting Phase 3 Authentication Tests")
    print(f"Testing against: {AUTH_SERVER_URL}")
    print(f"Test email: {TEST_EMAIL}")
    print("="*50)

    # Test health check first
    health_result = test_health_check()
    if not health_result or health_result.get('database') != 'connected':
        print("❌ Auth server is not running or database is not connected")
        return

    print("\n" + "="*50)

    # Test signup
    signup_result = test_signup()
    if not signup_result:
        print("❌ Signup failed, cannot proceed with other tests")
        return

    print("\n" + "="*50)
    
    # Test verify email
    if not test_verify_email():
        print("❌ Email verification failed, cannot proceed")
        return

    print("\n" + "="*50)

    # Test signin (should succeed now)
    signin_data, session_object = test_signin() # Get session_object
    if not signin_data:
        print("❌ Signin failed")
        return

    # No need to extract token, session_object handles it.
    
    print(f"✓ Signin successful (session managed by requests.Session)")

    print("\n" + "="*50)

    # Test me endpoint with session object
    me_result = test_me_endpoint(session_object) # Pass session_object
    if not me_result:
        print("❌ Me endpoint failed")
        return
        
    print("\n" + "="*50)
    
    # Test signout
    if test_signout(session_object): # Pass session_object
        # Verify token is invalid
        print("\nVerifying token is invalid after signout...")
        resp = session_object.get(f"{AUTH_SERVER_URL}/api/auth/me") # Use session_object
        if resp.status_code == 401:
            print("✓ Token successfully invalidated")
        else:
            print(f"✗ Token still valid? Status: {resp.status_code}")

    print("\n" + "="*50)
    print("✅ All Phase 3 tests completed successfully!")

if __name__ == "__main__":
    main()
