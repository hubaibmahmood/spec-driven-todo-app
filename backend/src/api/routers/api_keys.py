"""API routes for user API key management."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.schemas.api_key import (
    SaveApiKeyRequest,
    SaveApiKeyResponse,
    TestApiKeyRequest,
    TestApiKeyResponse,
    ApiKeyStatusResponse,
    DeleteApiKeyResponse,
    mask_api_key,
)
from src.services.api_key_service import ApiKeyService
from src.services.encryption_service import EncryptionService
from src.services.gemini_validator import GeminiValidator
from src.database.connection import get_db
from src.config import settings
from src.api.dependencies import get_current_user


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/user-api-keys", tags=["API Keys"])


def get_encryption_service() -> EncryptionService:
    """Dependency to get encryption service."""
    return EncryptionService(settings.ENCRYPTION_KEY)


def get_api_key_service(
    session: AsyncSession = Depends(get_db),
    encryption: EncryptionService = Depends(get_encryption_service),
) -> ApiKeyService:
    """Dependency to get API key service."""
    return ApiKeyService(session, encryption)


@router.get(
    "/current",
    response_model=ApiKeyStatusResponse,
    summary="Get current user's API key status",
    description="Retrieve masked API key and validation status for the authenticated user"
)
async def get_current_api_key(
    service: ApiKeyService = Depends(get_api_key_service),
    x_user_id: str | None = Header(None, alias="X-User-ID"),
    x_service_auth: str | None = Header(None, alias="X-Service-Auth"),
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's API key status.

    Supports two authentication modes:
    1. Regular user auth: Uses Bearer token
    2. Service-to-service auth: Uses X-User-ID + X-Service-Auth headers

    For service-to-service requests (e.g., from ai-agent), returns plaintext_key.
    For regular user requests, returns masked_key only.

    Returns:
        - configured: bool - Whether user has an API key configured
        - masked_key: str - Masked version of the API key (for user requests)
        - plaintext_key: str - Decrypted API key (for service requests only)
        - validation_status: str - Last validation result ('success', 'failure', or null)
        - last_validated_at: datetime - Timestamp of last Test Connection
    """
    # Determine if this is a service-to-service request
    is_service_request = x_user_id is not None and x_service_auth is not None

    if is_service_request:
        # Validate service auth token
        if x_service_auth != settings.SERVICE_AUTH_TOKEN:
            logger.warning(
                f"Service auth failed - X-User-ID={x_user_id[:8] if x_user_id else 'none'}... "
                f"token_match={x_service_auth == settings.SERVICE_AUTH_TOKEN}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid service authentication token"
            )
        # Use X-User-ID header for service requests
        target_user_id = x_user_id
        logger.info(f"Service-to-service request for user {target_user_id[:8]}...")
    else:
        # Regular user authentication via Bearer token
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Validate session token
        from src.services.auth_service import validate_session
        target_user_id = await validate_session(credentials.credentials, db)

        if target_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    record = await service.get_api_key_record(target_user_id)

    if not record:
        return ApiKeyStatusResponse(
            configured=False,
            provider=None,
            masked_key=None,
            plaintext_key=None,
            validation_status=None,
            last_validated_at=None,
            created_at=None,
            updated_at=None,
        )

    # Decrypt key
    try:
        plaintext_key = await service.get_api_key(target_user_id)
    except ValueError:
        # Decryption failed (wrong ENCRYPTION_KEY or corrupted data)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve API key. Contact support."
        )

    # Return plaintext key for service requests, masked key for user requests
    if is_service_request:
        return ApiKeyStatusResponse(
            configured=True,
            provider=record.provider,
            masked_key=None,
            plaintext_key=plaintext_key,
            validation_status=record.validation_status,
            last_validated_at=record.last_validated_at,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
    else:
        masked = mask_api_key(plaintext_key) if plaintext_key else None
        return ApiKeyStatusResponse(
            configured=True,
            provider=record.provider,
            masked_key=masked,
            plaintext_key=None,
            validation_status=record.validation_status,
            last_validated_at=record.last_validated_at,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )


@router.post(
    "",
    response_model=SaveApiKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save or update API key",
    description="Encrypt and store the user's Gemini API key"
)
async def save_api_key(
    request: SaveApiKeyRequest,
    user_id: str = Depends(get_current_user),
    service: ApiKeyService = Depends(get_api_key_service),
    session: AsyncSession = Depends(get_db),
):
    """
    Save or update user's API key.

    Validates format, encrypts, and stores the API key.

    Returns:
        - success: bool
        - message: str
        - masked_key: str - Masked version of the saved key
    """
    # Validate format before saving
    valid, error = GeminiValidator.validate_format(request.api_key)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    try:
        # Save encrypted key
        await service.save_api_key(user_id, request.api_key, request.provider)
        await session.commit()

        # Audit log (no sensitive data)
        logger.info(
            f"API key saved - user_id={user_id[:8]}... provider={request.provider} "
            f"operation=save_api_key"
        )

        return SaveApiKeyResponse(
            success=True,
            message="API key saved successfully",
            masked_key=mask_api_key(request.api_key),
        )
    except ValueError as e:
        await session.rollback()
        logger.error(
            f"API key save failed - user_id={user_id[:8]}... provider={request.provider} "
            f"operation=save_api_key error={str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save API key: {str(e)}"
        )


@router.post(
    "/test",
    response_model=TestApiKeyResponse,
    summary="Test API key connectivity",
    description="Validate API key by making a test request to Gemini API"
)
async def test_api_key(
    request: TestApiKeyRequest,
    user_id: str = Depends(get_current_user),
    service: ApiKeyService = Depends(get_api_key_service),
    session: AsyncSession = Depends(get_db),
):
    """
    Test API key connectivity.

    Makes a minimal request to Gemini API to verify the key is valid.
    Updates validation_status and last_validated_at in the database.

    Returns:
        - success: bool
        - message: str - Human-readable test result
        - validation_status: str - 'success' or 'failure'
    """
    # Validate API key with Gemini API
    valid, error = await GeminiValidator.validate_key(request.api_key)

    validation_status = "success" if valid else "failure"

    # Update validation status in database if key exists
    await service.update_validation_status(user_id, validation_status)
    await session.commit()

    # Audit log (no sensitive data)
    logger.info(
        f"API key tested - user_id={user_id[:8]}... validation_status={validation_status} "
        f"operation=test_api_key"
    )

    if not valid:
        return TestApiKeyResponse(
            success=False,
            message=error or "API key validation failed",
            validation_status=validation_status,
        )

    return TestApiKeyResponse(
        success=True,
        message="API key is valid and working",
        validation_status=validation_status,
    )


@router.delete(
    "/current",
    response_model=DeleteApiKeyResponse,
    summary="Delete current user's API key",
    description="Remove the user's stored API key"
)
async def delete_current_api_key(
    user_id: str = Depends(get_current_user),
    service: ApiKeyService = Depends(get_api_key_service),
    session: AsyncSession = Depends(get_db),
):
    """
    Delete current user's API key.

    Returns:
        - success: bool
        - message: str
    """
    deleted = await service.delete_api_key(user_id)
    await session.commit()

    if not deleted:
        logger.warning(
            f"API key delete failed - user_id={user_id[:8]}... operation=delete_api_key "
            f"reason=not_found"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No API key found to delete"
        )

    # Audit log (no sensitive data)
    logger.info(
        f"API key deleted - user_id={user_id[:8]}... operation=delete_api_key"
    )

    return DeleteApiKeyResponse(
        success=True,
        message="API key removed successfully"
    )
