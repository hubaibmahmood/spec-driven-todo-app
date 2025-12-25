"""Encryption service using Fernet (AES-256) for API key encryption at rest."""

from cryptography.fernet import Fernet, InvalidToken


class EncryptionService:
    """
    Symmetric encryption using Fernet (AES-128-CBC + HMAC).

    Used for encrypting user API keys before storing them in the database.
    """

    def __init__(self, encryption_key: str):
        """
        Initialize encryption service with a Fernet key.

        Args:
            encryption_key: Base64-encoded Fernet key (from ENCRYPTION_KEY env var)

        Raises:
            ValueError: If encryption_key is invalid
        """
        if not encryption_key:
            raise ValueError("encryption_key cannot be empty")

        try:
            if isinstance(encryption_key, str):
                encryption_key = encryption_key.encode()
            self.cipher = Fernet(encryption_key)
        except Exception as e:
            raise ValueError(f"Invalid encryption key format: {e}") from e

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string.

        Args:
            plaintext: The string to encrypt (e.g., API key)

        Returns:
            Base64-encoded ciphertext

        Raises:
            ValueError: If plaintext is empty or encryption fails
        """
        if not plaintext:
            raise ValueError("plaintext cannot be empty")

        try:
            ciphertext = self.cipher.encrypt(plaintext.encode())
            return ciphertext.decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {e}") from e

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext string.

        Args:
            ciphertext: Base64-encoded ciphertext (from database)

        Returns:
            Decrypted plaintext string

        Raises:
            ValueError: If ciphertext is empty or decryption fails
                       (wrong key, corrupted data, etc.)
        """
        if not ciphertext:
            raise ValueError("ciphertext cannot be empty")

        try:
            plaintext = self.cipher.decrypt(ciphertext.encode())
            return plaintext.decode()
        except InvalidToken as e:
            raise ValueError(
                "Decryption failed - invalid key or corrupted data"
            ) from e
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}") from e
