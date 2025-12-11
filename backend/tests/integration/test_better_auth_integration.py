"""Integration tests for Better Auth Server and FastAPI backend."""

import pytest
import httpx
from datetime import datetime, timedelta, timezone
import asyncio
import secrets
import os
from src.models.database import UserSession
from sqlalchemy import select, text # Added this import
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

AUTH_SERVER_URL = "http://localhost:8080"

# Helper function to get DATABASE_URL from auth-server/.env
def get_auth_server_database_url():
    """Reads DATABASE_URL from auth-server/.env."""
    env_path = os.path.join(os.path.dirname(__file__), '../../../auth-server', '.env')
    try:
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    # Remove " and ' from the URL
                    url = line.split('=', 1)[1].strip().strip('"').strip("'")
                    # Ensure using async driver
                    url = url.replace('postgresql://', 'postgresql+asyncpg://')
                    # Fix sslmode for asyncpg
                    return url.replace('sslmode=require', 'ssl=require')
    except Exception as e:
        pytest.fail(f"Error reading auth-server/.env: {e}")
    return None

async def get_verification_token_from_pg(email: str, pg_db_url: str) -> str | None:
    """Fetches the latest verification token for an email from PostgreSQL."""
    pg_engine = create_async_engine(pg_db_url, echo=False, future=True)
    pg_async_session_maker = async_sessionmaker(
        pg_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with pg_async_session_maker() as pg_session:
        # better-auth v1 uses 'verifications' table, 'identifier' is email, 'value' is token
        result = await pg_session.execute(
            text("SELECT value FROM verifications WHERE identifier = :email ORDER BY \"expiresAt\" DESC"),
            {"email": email}
        )
        row = result.fetchone()
        await pg_engine.dispose()
        if row:
            return row[0]
    return None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_auth_server_signup_and_fastapi_access(test_client, db_session):
    """
    Test the full flow:
    1. Sign up a new user on the Auth Server.
    2. Sign in to get a session token.
    3. Replicate the session in the FastAPI test database (since they are separate in this test env).
    4. Use the token to access a protected FastAPI endpoint.
    """
    pg_db_url = get_auth_server_database_url()
    if not pg_db_url:
        pytest.skip("Could not get PostgreSQL DATABASE_URL from auth-server/.env")

    # 1. Sign up on Auth Server
    # Create a unique email for each test run
    unique_id = secrets.token_hex(4)
    email = f"test.user.{unique_id}@example.com"
    password = "Password123!"
    name = f"Test User {unique_id}"

    async with httpx.AsyncClient() as client:
        # Check if auth server is up
        try:
            health = await client.get(f"{AUTH_SERVER_URL}/health")
            if health.status_code != 200:
                pytest.skip(f"Auth server not healthy: {health.status_code}")
        except httpx.ConnectError:
            pytest.skip("Auth server not reachable")

        # Signup
        signup_response = await client.post(
            f"{AUTH_SERVER_URL}/api/auth/sign-up/email",
            json={
                "email": email,
                "password": password,
                "name": name
            }
        )
        assert signup_response.status_code == 200
        signup_data = signup_response.json()
    
        # Extract user_id from signup response
        user_id = signup_data.get("user", {}).get("id")
    
    assert user_id is not None, "Failed to obtain user ID from signup"

    # 1.1. Verify Email
    # In a real production environment, this would involve clicking a link from an email.
    # In this test, we fetch the token from the test database.
    
    # Wait for the async signup to commit to DB
    await asyncio.sleep(2) # Increased sleep time

    verification_token = await get_verification_token_from_pg(email, pg_db_url)

    assert verification_token is not None, f"No verification record found for {email} in PostgreSQL"

    async with httpx.AsyncClient() as client:
        verify_response = await client.get(
            f"{AUTH_SERVER_URL}/api/auth/verify-email",
            params={"token": verification_token}
        )
        assert verify_response.status_code == 200, f"Email verification failed: {verify_response.text}"

    # Now proceed with sign-in to get a fresh session token after verification
    async with httpx.AsyncClient() as client:
        signin_response = await client.post(
            f"{AUTH_SERVER_URL}/api/auth/sign-in/email",
            json={
                "email": email,
                "password": password
            }
        )
        assert signin_response.status_code == 200
        signin_data = signin_response.json()
        token = signin_data.get("token") or signin_data.get("session", {}).get("token")
        user_id = signin_data.get("user", {}).get("id") or signin_data.get("session", {}).get("userId")

    assert token is not None, "Failed to obtain session token after signin"
    assert user_id is not None, "Failed to obtain user ID after signin"

    # 2. Replicate session in FastAPI test database
    # In a real production environment, both share the same Postgres DB.
    # Here, we manually sync the state to the SQLite test DB.
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    session_record = UserSession(
        id=secrets.token_hex(12), # Generate a cuid-like ID for the session
        token=token,
        user_id=user_id,
        expires_at=expires_at,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        ip_address="127.0.0.1",
        user_agent="TestClient",
        revoked=False
    )
    db_session.add(session_record)
    await db_session.commit()

    # 3. Access protected FastAPI endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get("/tasks/", headers=headers)

    # Should be 200 OK (empty list of tasks)
    assert response.status_code == 200
    assert response.json() == []

    # 4. Create a task with this user
    task_data = {"title": "Integration Task", "description": "Created via auth token"}
    create_response = await test_client.post("/tasks/", json=task_data, headers=headers)
    assert create_response.status_code == 201
    created_task = create_response.json()
    assert created_task["title"] == "Integration Task"

    # 5. Verify data isolation (optional but good)
    # Another test could verify that a different token can't see this task
