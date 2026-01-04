"""Application configuration using Pydantic Settings."""

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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
