"""Service for managing encrypted API keys."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.models.user_api_key import UserApiKey
from src.services.encryption_service import EncryptionService


class ApiKeyService:
    """
    Service for CRUD operations on user API keys with encryption.

    Handles encryption/decryption using EncryptionService.
    """

    def __init__(self, session: AsyncSession, encryption: EncryptionService):
        """
        Initialize API key service.

        Args:
            session: SQLAlchemy async session
            encryption: EncryptionService instance for encrypt/decrypt
        """
        self.session = session
        self.encryption = encryption

    async def save_api_key(
        self,
        user_id: str,
        plaintext_key: str,
        provider: str = "gemini"
    ) -> UserApiKey:
        """
        Encrypt and save API key (create or update).

        Args:
            user_id: User's ID (from authentication)
            plaintext_key: Unencrypted API key
            provider: Provider name (default: "gemini")

        Returns:
            UserApiKey model instance

        Raises:
            ValueError: If encryption fails
        """
        # Encrypt the plaintext key
        encrypted_key = self.encryption.encrypt(plaintext_key.strip())

        # Check for existing key
        stmt = select(UserApiKey).where(
            UserApiKey.user_id == user_id,
            UserApiKey.provider == provider
        )
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing key
            existing.encrypted_key = encrypted_key
            existing.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
            # Reset validation status when key changes
            existing.validation_status = None
            existing.last_validated_at = None
            await self.session.flush()
            return existing

        # Create new key
        user_api_key = UserApiKey(
            user_id=user_id,
            encrypted_key=encrypted_key,
            provider=provider
        )
        self.session.add(user_api_key)
        await self.session.flush()
        return user_api_key

    async def get_api_key(
        self,
        user_id: str,
        provider: str = "gemini"
    ) -> Optional[str]:
        """
        Retrieve and decrypt API key.

        Args:
            user_id: User's ID
            provider: Provider name (default: "gemini")

        Returns:
            Decrypted plaintext API key or None if not found

        Raises:
            ValueError: If decryption fails
        """
        stmt = select(UserApiKey).where(
            UserApiKey.user_id == user_id,
            UserApiKey.provider == provider
        )
        result = await self.session.execute(stmt)
        user_api_key = result.scalar_one_or_none()

        if not user_api_key:
            return None

        # Decrypt and return plaintext key
        return self.encryption.decrypt(user_api_key.encrypted_key)

    async def get_api_key_record(
        self,
        user_id: str,
        provider: str = "gemini"
    ) -> Optional[UserApiKey]:
        """
        Retrieve API key record (without decryption).

        Useful for checking status and metadata without decrypting.

        Args:
            user_id: User's ID
            provider: Provider name (default: "gemini")

        Returns:
            UserApiKey model instance or None if not found
        """
        stmt = select(UserApiKey).where(
            UserApiKey.user_id == user_id,
            UserApiKey.provider == provider
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_api_key(
        self,
        user_id: str,
        provider: str = "gemini"
    ) -> bool:
        """
        Delete API key.

        Args:
            user_id: User's ID
            provider: Provider name (default: "gemini")

        Returns:
            True if key was deleted, False if not found
        """
        stmt = delete(UserApiKey).where(
            UserApiKey.user_id == user_id,
            UserApiKey.provider == provider
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def update_validation_status(
        self,
        user_id: str,
        status: str,
        provider: str = "gemini"
    ) -> Optional[UserApiKey]:
        """
        Update validation status after testing API key.

        Args:
            user_id: User's ID
            status: Validation status ('success' or 'failure')
            provider: Provider name (default: "gemini")

        Returns:
            Updated UserApiKey model instance or None if not found
        """
        record = await self.get_api_key_record(user_id, provider)
        if not record:
            return None

        record.validation_status = status
        record.last_validated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        await self.session.flush()
        return record
