"""SQLAlchemy model for user API keys."""

from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.sql import func
from src.models.database import Base


class UserApiKey(Base):
    """
    Stores encrypted API keys for external LLM providers.

    Encryption/decryption happens at service layer (ApiKeyService),
    not at ORM level (no TypeDecorator).
    """

    __tablename__ = "user_api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        String(255),
        nullable=False,
        index=True
    )  # No FK constraint - user table managed by better-auth
    encrypted_key = Column(String(500), nullable=False)  # Ciphertext (Fernet-encrypted)
    provider = Column(String(50), nullable=False, server_default="gemini")
    validation_status = Column(String(50), nullable=True)  # 'success', 'failure', or NULL
    last_validated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'provider', name='uq_user_provider_key'),
    )

    def __repr__(self) -> str:
        """String representation (safe - doesn't expose plaintext key)."""
        return f"<UserApiKey(id={self.id}, user_id={self.user_id}, provider={self.provider})>"
