"""Integration tests for session authentication."""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import UserSession, Task


@pytest.mark.asyncio
class TestSessionAuthentication:
    """Test session-based authentication."""

    async def test_valid_session_token_allows_access(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        sample_user_id
    ):
        """Test that a valid session token allows access to endpoints."""
        # Create a valid session in the database
        import hashlib
        import hmac
        from src.config import settings
        
        token = "valid_test_token_12345"
        token_hash = hmac.new(
            settings.SESSION_HASH_SECRET.encode(),
            token.encode(),
            hashlib.sha256
        ).hexdigest()
        
        user_session = UserSession(
            id=uuid4(),
            user_id=sample_user_id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            revoked=False
        )
        db_session.add(user_session)
        await db_session.commit()
        
        # Create a task for this user
        task = Task(
            user_id=sample_user_id,
            title="Test Task",
            description="Test Description",
            completed=False
        )
        db_session.add(task)
        await db_session.commit()
        
        # Make authenticated request with Bearer token
        headers = {"Authorization": f"Bearer {token}"}
        response = await test_client.get("/tasks/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["title"] == "Test Task"

    async def test_missing_token_returns_401(
        self,
        test_client: AsyncClient
    ):
        """Test that missing authentication token returns 401."""
        # Request without Authorization header
        response = await test_client.get("/tasks/")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_invalid_token_returns_401(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test that invalid token (not in database) returns 401."""
        # Use a token that doesn't exist in database
        invalid_token = "invalid_token_does_not_exist"
        headers = {"Authorization": f"Bearer {invalid_token}"}
        
        response = await test_client.get("/tasks/", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower() or "unauthorized" in data["detail"].lower()

    async def test_expired_token_returns_401(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        sample_user_id
    ):
        """Test that expired session token returns 401."""
        import hashlib
        import hmac
        from src.config import settings

        token = "expired_test_token_12345"
        token_hash = hmac.new(
            settings.SESSION_HASH_SECRET.encode(),
            token.encode(),
            hashlib.sha256
        ).hexdigest()

        # Create session with past expiration date
        expired_session = UserSession(
            id=uuid4(),
            user_id=sample_user_id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
            revoked=False
        )
        db_session.add(expired_session)
        await db_session.commit()

        headers = {"Authorization": f"Bearer {token}"}
        response = await test_client.get("/tasks/", headers=headers)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "expired" in data["detail"].lower() or "invalid" in data["detail"].lower()

    async def test_revoked_token_returns_401(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession,
        sample_user_id
    ):
        """Test that revoked session token returns 401."""
        import hashlib
        import hmac
        from src.config import settings

        token = "revoked_test_token_12345"
        token_hash = hmac.new(
            settings.SESSION_HASH_SECRET.encode(),
            token.encode(),
            hashlib.sha256
        ).hexdigest()

        # Create revoked session
        revoked_session = UserSession(
            id=uuid4(),
            user_id=sample_user_id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(hours=1),  # Valid expiration
            revoked=True  # But revoked
        )
        db_session.add(revoked_session)
        await db_session.commit()

        headers = {"Authorization": f"Bearer {token}"}
        response = await test_client.get("/tasks/", headers=headers)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_user_cannot_access_other_user_tasks_returns_403(
        self,
        test_client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test that user cannot access tasks belonging to another user."""
        import hashlib
        import hmac
        from src.config import settings

        # Create two users
        user1_id = uuid4()
        user2_id = uuid4()

        # Create session for user1
        token = "user1_token_12345"
        token_hash = hmac.new(
            settings.SESSION_HASH_SECRET.encode(),
            token.encode(),
            hashlib.sha256
        ).hexdigest()

        user1_session = UserSession(
            id=uuid4(),
            user_id=user1_id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            revoked=False
        )
        db_session.add(user1_session)

        # Create task for user2
        user2_task = Task(
            user_id=user2_id,
            title="User 2 Task",
            description="Belongs to user 2",
            completed=False
        )
        db_session.add(user2_task)
        await db_session.commit()

        # User1 tries to access user2's task
        headers = {"Authorization": f"Bearer {token}"}
        response = await test_client.get(f"/tasks/{user2_task.id}", headers=headers)

        # Should return 404 (not found) - user doesn't have access to this task
        # Note: We return 404 instead of 403 to avoid leaking existence of tasks
        assert response.status_code == 404

        # User1 should only see their own tasks
        response = await test_client.get("/tasks/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0  # No tasks for user1
