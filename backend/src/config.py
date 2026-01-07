"""Application configuration using Pydantic Settings."""

import hashlib
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from cryptography.fernet import Fernet, InvalidToken


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"

    # Authentication Configuration
    SESSION_HASH_SECRET: str = "dev-secret-key-change-in-production"
    SERVICE_AUTH_TOKEN: str = ""  # Service-to-service authentication token

    # JWT Configuration
    JWT_SECRET: str = "dev-jwt-secret-min-32-chars-change-in-production-please"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_AUTH_ENABLED: bool = True  # Full JWT migration - enabled by default
    JWT_ROLLOUT_PERCENTAGE: int = 100  # 100% JWT usage (full migration)

    # API Key Encryption Configuration
    ENCRYPTION_KEY: str = ""  # Fernet encryption key for API keys (REQUIRED in production)

    # Application Configuration
    ENVIRONMENT: str = "development"

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:3000"

    # SQLAlchemy Pool Configuration
    SQLALCHEMY_POOL_SIZE: int = 10
    SQLALCHEMY_POOL_OVERFLOW: int = 20
    SQLALCHEMY_POOL_TIMEOUT: int = 30
    SQLALCHEMY_POOL_RECYCLE: int = 3600
    SQLALCHEMY_ECHO: bool = False

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"

    def validate_encryption_key(self) -> None:
        """Validate that ENCRYPTION_KEY is a valid Fernet key."""
        if not self.ENCRYPTION_KEY:
            raise ValueError(
                "ENCRYPTION_KEY is required. Generate one with: "
                "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        try:
            Fernet(self.ENCRYPTION_KEY.encode())
        except Exception as e:
            raise ValueError(f"Invalid ENCRYPTION_KEY format: {e}") from e

    def should_use_jwt(self, user_id: str) -> bool:
        """
        Determine if a user should use JWT authentication based on rollout percentage.

        Uses MD5 hash of user_id for stable cohort assignment. The same user_id
        will always get the same result, enabling gradual rollout (0% → 10% → 25% → 50% → 100%).

        Args:
            user_id: The user's unique identifier

        Returns:
            True if user should use JWT auth, False for session auth

        Example rollout progression:
            - JWT_ROLLOUT_PERCENTAGE=0: No users use JWT (all session)
            - JWT_ROLLOUT_PERCENTAGE=10: 10% of users use JWT
            - JWT_ROLLOUT_PERCENTAGE=50: 50% of users use JWT
            - JWT_ROLLOUT_PERCENTAGE=100: All users use JWT (full migration)
        """
        # If JWT is disabled, return False
        if not self.JWT_AUTH_ENABLED:
            return False

        # If rollout is 100%, everyone uses JWT
        if self.JWT_ROLLOUT_PERCENTAGE >= 100:
            return True

        # If rollout is 0%, no one uses JWT
        if self.JWT_ROLLOUT_PERCENTAGE <= 0:
            return False

        # Hash user_id to get stable cohort assignment
        # Use first 8 hex characters of MD5 hash (32 bits)
        hash_hex = hashlib.md5(user_id.encode()).hexdigest()[:8]
        hash_int = int(hash_hex, 16)

        # Map hash to 0-100 range using modulo
        cohort = hash_int % 100

        # User is in JWT cohort if their cohort number < rollout percentage
        return cohort < self.JWT_ROLLOUT_PERCENTAGE

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
