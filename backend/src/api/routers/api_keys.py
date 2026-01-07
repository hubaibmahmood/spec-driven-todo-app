"""API routes for user API key management."""

import logging
from datetime import datetime, UTC
from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.schemas.api_key import (
    SaveApiKeyRequest,
    SaveApiKeyResponse,
    ApiKeyStatusResponse,
    DeleteApiKeyResponse,
    mask_api_key,
)
from src.services.api_key_service import ApiKeyService
from src.services.encryption_service import EncryptionService
from src.services.gemini_validator import GeminiValidator
from src.services.rate_limiter import api_key_test_limiter
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
    1. Regular user auth: Uses JWT Bearer token
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
        # Regular user authentication via JWT Bearer token
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Validate JWT access token
        from src.services.jwt_service import jwt_service, TokenExpiredError, InvalidTokenError
        try:
            target_user_id = jwt_service.validate_access_token(credentials.credentials)
        except TokenExpiredError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": "token_expired", "message": "Access token has expired"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": "invalid_token", "message": str(e)},
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
    description="Validate with Gemini API, then encrypt and store the user's API key"
)
async def save_api_key(
    request: SaveApiKeyRequest,
    user_id: str = Depends(get_current_user),
    service: ApiKeyService = Depends(get_api_key_service),
    session: AsyncSession = Depends(get_db),
):
    """
    Save or update user's API key with automatic validation.

    Flow:
    1. Check rate limit (5 validation tests per hour)
    2. Validates format
    3. Tests connectivity with Gemini API
    4. Only saves if test succeeds
    5. Updates validation status in database

    Returns:
        - success: bool
        - message: str
        - masked_key: str - Masked version of the saved key

    Raises:
        - 400: Invalid format or API key test failed
        - 429: Rate limit exceeded (5 tests per hour)
        - 500: Encryption or database error
    """
    # Step 1: Check rate limit (5 validation tests per hour)
    is_allowed, remaining, window_end = api_key_test_limiter.check_rate_limit(user_id)

    if not is_allowed:
        # Calculate minutes until reset
        now = datetime.now(UTC)
        minutes_remaining = int((window_end - now).total_seconds() / 60)
        hours = minutes_remaining // 60
        minutes = minutes_remaining % 60

        # Format time remaining message
        if hours > 0:
            time_msg = f"{hours} hour{'s' if hours > 1 else ''} and {minutes} minute{'s' if minutes != 1 else ''}"
        else:
            time_msg = f"{minutes} minute{'s' if minutes != 1 else ''}"

        error_message = (
            f"You've reached the limit of 5 API key validation tests per hour. "
            f"Please try again in {time_msg}."
        )

        logger.warning(
            f"Rate limit exceeded - user_id={user_id[:8]}... "
            f"reset_in={minutes_remaining}min operation=save_api_key"
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_message,
            headers={
                "X-RateLimit-Limit": "5",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": window_end.isoformat(),
                "Retry-After": str(minutes_remaining * 60)  # In seconds
            }
        )

    # Log remaining attempts for monitoring
    logger.info(
        f"Rate limit check passed - user_id={user_id[:8]}... "
        f"remaining_tests={remaining}/5 operation=save_api_key"
    )

    # Step 2: Validate format
    valid, error = GeminiValidator.validate_format(request.api_key)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    # Step 3: Test API key with Gemini API before saving
    logger.info(
        f"Testing API key before save - user_id={user_id[:8]}... "
        f"provider={request.provider} operation=save_api_key"
    )

    valid, error = await GeminiValidator.validate_key(request.api_key)
    if not valid:
        logger.warning(
            f"API key validation failed - user_id={user_id[:8]}... "
            f"provider={request.provider} operation=save_api_key reason={error}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API key validation failed: {error}"
        )

    # Step 4: Save encrypted key (validation succeeded)
    try:
        await service.save_api_key(user_id, request.api_key, request.provider)

        # Step 5: Update validation status to 'success'
        await service.update_validation_status(user_id, "success", request.provider)

        await session.commit()

        # Audit log (no sensitive data)
        logger.info(
            f"API key saved successfully - user_id={user_id[:8]}... "
            f"provider={request.provider} validation_status=success operation=save_api_key"
        )

        return SaveApiKeyResponse(
            success=True,
            message="API key validated and saved successfully",
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
