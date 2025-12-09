---
name: security-best-practices
description: Security implementation for FastAPI including JWT authentication, OAuth2, CORS, input validation, password hashing, rate limiting, and middleware. Use for authentication setup, authorization, security middleware, API protection, and better-auth integration.
allowed-tools: Read, Edit, Bash, Glob, Grep
---

# FastAPI Security Best Practices

## Overview

This skill provides comprehensive security guidance for FastAPI applications, including authentication, authorization, CORS, input validation, rate limiting, and integration with external auth services like better-auth.

## When to Use

- Implementing JWT authentication
- Setting up OAuth2 flows
- Configuring CORS
- Adding security middleware
- Input validation and sanitization
- Password hashing and verification
- Rate limiting
- Integrating with better-auth (Node.js)
- API key management
- Protecting endpoints

## JWT Authentication

### JWT Setup

```python
# app/core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)

# JWT token creation
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")
```

### OAuth2 Password Flow

```python
# app/core/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import decode_token
from app.db.session import get_db
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user from token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    repository = UserRepository(db)
    user = await repository.get_by_id(user_id)

    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_superuser(current_user = Depends(get_current_user)):
    """Require superuser access."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
```

### Login Endpoint

```python
# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.db.session import get_db
from app.schemas.auth import Token
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login with username and password."""
    repository = UserRepository(db)

    # Get user by username or email
    user = await repository.get_by_email(form_data.username)
    if not user:
        user = await repository.get_by_username(form_data.username)

    # Verify user and password
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token."""
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(401, "Invalid token type")

        user_id = payload.get("sub")
        repository = UserRepository(db)
        user = await repository.get_by_id(user_id)

        if not user or not user.is_active:
            raise HTTPException(401, "User not found or inactive")

        # Create new access token
        new_access_token = create_access_token(data={"sub": user.id})

        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except ValueError:
        raise HTTPException(401, "Invalid refresh token")
```

### Protected Endpoints

```python
from fastapi import Depends
from app.core.auth import get_current_active_user

@router.get("/profile")
async def get_profile(current_user = Depends(get_current_active_user)):
    """Get current user profile (requires authentication)."""
    return current_user

@router.get("/admin")
async def admin_only(current_user = Depends(get_current_superuser)):
    """Admin-only endpoint."""
    return {"message": "Admin access granted"}
```

## Better-Auth Integration

### Verify External Tokens

```python
# app/core/better_auth.py
import httpx
from fastapi import HTTPException, status

BETTER_AUTH_URL = "https://your-auth-server.com"

async def verify_better_auth_token(token: str) -> dict:
    """Verify token with better-auth server."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BETTER_AUTH_URL}/api/auth/verify",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )

            return response.json()
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Auth service unavailable"
            )

# Dependency
async def get_better_auth_user(token: str = Depends(oauth2_scheme)):
    """Get user from better-auth token."""
    user_data = await verify_better_auth_token(token)
    return user_data
```

## CORS Configuration

### Basic CORS

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Or specific methods: ["GET", "POST"]
    allow_headers=["*"],  # Or specific headers: ["Authorization", "Content-Type"]
    expose_headers=["X-Total-Count"],  # Headers exposed to frontend
    max_age=3600,  # Cache preflight requests for 1 hour
)
```

### Environment-based CORS

```python
# app/core/config.py
from typing import List

class Settings(BaseSettings):
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from environment."""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS

# app/main.py
from app.core.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Input Validation

### Pydantic Validation

```python
from pydantic import BaseModel, Field, EmailStr, validator
import re

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric')
        return v

    @validator('password')
    def password_strength(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v
```

### SQL Injection Prevention

```python
# ✅ Good: Use ORM (SQLAlchemy prevents SQL injection)
stmt = select(User).where(User.email == email)
user = await db.execute(stmt)

# ❌ Bad: Raw SQL with string interpolation
query = f"SELECT * FROM users WHERE email = '{email}'"  # VULNERABLE!

# ✅ If raw SQL needed, use parameters
from sqlalchemy import text
stmt = text("SELECT * FROM users WHERE email = :email")
result = await db.execute(stmt, {"email": email})
```

## Security Middleware

### Security Headers

```python
# app/middleware/security.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response

# app/main.py
app.add_middleware(SecurityHeadersMiddleware)
```

### HTTPS Redirect

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Only in production
if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

## Rate Limiting

### Redis-based Rate Limiting

```python
# app/core/rate_limit.py
import redis.asyncio as redis
from fastapi import HTTPException, Request, status
from datetime import timedelta

redis_client = redis.from_url("redis://localhost:6379")

async def rate_limit(
    request: Request,
    max_requests: int = 100,
    window: int = 3600  # 1 hour
):
    """Rate limit middleware."""
    # Use IP address or user ID as key
    client_id = request.client.host
    key = f"rate_limit:{client_id}"

    # Get current count
    count = await redis_client.get(key)

    if count is None:
        # First request in window
        await redis_client.setex(key, window, 1)
        remaining = max_requests - 1
    else:
        count = int(count)
        if count >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(window)}
            )
        await redis_client.incr(key)
        remaining = max_requests - count - 1

    # Add rate limit headers
    request.state.rate_limit_remaining = remaining
    return True

# Usage as dependency
from fastapi import Depends

@router.get("/limited")
async def limited_endpoint(
    rate_limit_check = Depends(rate_limit)
):
    return {"message": "Success"}
```

## Environment Variables & Secrets

### Secure Configuration

```python
# .env
SECRET_KEY=your-secret-key-here-change-this-in-production
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
REDIS_URL=redis://localhost:6379

# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: Optional[str] = None

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### .env.example

```bash
# Create .env.example (committed to repo)
SECRET_KEY=change-this-to-a-random-secret-key
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

## Security Checklist

- [ ] JWT tokens with proper expiration
- [ ] Password hashing with bcrypt
- [ ] HTTPS in production
- [ ] CORS properly configured
- [ ] Input validation with Pydantic
- [ ] SQL injection prevention (use ORM)
- [ ] Rate limiting on sensitive endpoints
- [ ] Security headers middleware
- [ ] Secrets in environment variables
- [ ] Error messages don't expose internals
- [ ] Authentication on protected routes
- [ ] Authorization checks where needed
- [ ] Session management
- [ ] CSRF protection if needed
- [ ] XSS prevention
- [ ] File upload validation

## Reference

For detailed patterns, see:
- [JWT-AUTH.md](JWT-AUTH.md) - JWT implementation details
- [CORS-MIDDLEWARE.md](CORS-MIDDLEWARE.md) - CORS configuration
- [VALIDATION.md](VALIDATION.md) - Input validation patterns

## Common Vulnerabilities to Avoid

1. **Hardcoded secrets**: Always use environment variables
2. **Weak password requirements**: Enforce strong passwords
3. **No rate limiting**: Prevent brute force attacks
4. **Missing authentication**: Protect all sensitive endpoints
5. **Exposing stack traces**: Sanitize error messages
6. **SQL injection**: Use ORM, never raw string interpolation
7. **XSS**: Validate and sanitize all inputs
8. **Insecure CORS**: Only allow trusted origins
9. **Expired tokens not checked**: Always verify exp claim
10. **No HTTPS**: Always use HTTPS in production
