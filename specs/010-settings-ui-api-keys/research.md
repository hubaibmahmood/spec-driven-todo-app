# Research Document: Settings UI for API Key Management

**Feature**: 010-settings-ui-api-keys
**Date**: 2025-12-24
**Context**: Secure storage and management of user Gemini API keys in a FastAPI + Next.js full-stack application

---

## Executive Summary

This research resolves 5 critical technical unknowns identified in the implementation plan:

1. **Encryption Library** → **cryptography (Fernet)** - Industry standard, battle-tested, perfect for this use case
2. **Gemini API Validation** → **generateContent with 1-word prompt** - Minimal cost (~$0.0000017/test), full validation
3. **Better-Auth Integration** → **Database query pattern** - Already implemented in project, production-ready
4. **Password Input Component** → **React with lucide-react Eye/EyeOff** - Accessible, secure, follows best practices
5. **SQLAlchemy Encryption** → **Service-layer encryption** - Explicit, testable, async-compatible

All recommendations align with the project's constitution principles: test-first development, clean code, simplicity over magic.

---

## 1. Encryption Library Selection

### Decision: Use `cryptography` Library with Fernet

**Rationale**:
- **Industry standard**: PyCA cryptography is the gold standard in Python with extensive security audits
- **Simplicity**: Fernet is a pre-packaged symmetric encryption format with secure defaults
- **Spec compliance**: Spec explicitly mentions "AES-256 or Fernet"
- **No async issues**: Pure Python, can be used safely in async context via thread pool
- **Battle-tested**: Used by Django, major Python frameworks, thousands of production systems

### Comparison Matrix

| Library | Security Audit | Async Support | Ease of Use | Recommendation |
|---------|----------------|---------------|-------------|----------------|
| **cryptography (Fernet)** | ✅ Extensive (PyCA) | ✅ Sync (safe with thread pool) | ✅ 3-line API | **RECOMMENDED** |
| PyCryptodome | ⚠️ Community-driven | ⚠️ Sync only | ⚠️ Low-level (manual IV, padding) | Not recommended |
| PyNaCl | ✅ libsodium (excellent) | ⚠️ Sync only | ✅ Clean API | Good, but not AES |

### Implementation Example

```python
from cryptography.fernet import Fernet
import hashlib
import base64

class EncryptionService:
    """Symmetric encryption using Fernet (AES-128-CBC + HMAC)."""

    def __init__(self, master_key: str):
        # Derive proper 32-byte key from master key
        key_bytes = hashlib.sha256(master_key.encode()).digest()
        self.cipher = Fernet(base64.urlsafe_b64encode(key_bytes))

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext API key."""
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext API key."""
        return self.cipher.decrypt(ciphertext.encode()).decode()

# Usage
from src.config import settings
encryption_service = EncryptionService(settings.ENCRYPTION_KEY)
```

### Key Generation

```bash
# Generate a secure Fernet key (one-time setup)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Output example: Hs5LhMvlQhR-N8jz5N6B5J6L9K2M3N4O5P6Q7R8S=
# Store in .env as ENCRYPTION_KEY=<output>
```

**Decision**: ✅ **Use cryptography library with Fernet**

---

## 2. Gemini API Key Validation

### Decision: Use `google-generativeai` SDK with Minimal generateContent Request

**Validation Strategy**:
- **Endpoint**: `generateContent` with 1-word prompt (e.g., "hi")
- **Model**: `gemini-1.5-flash` (cheapest, fastest)
- **Max tokens**: 5 (minimize cost)
- **Timeout**: 10 seconds (as per requirement)
- **Cost per validation**: ~$0.0000017 (negligible)

### Error Classification

| Error Type | HTTP Code | Detection | User Message |
|------------|-----------|-----------|--------------|
| Invalid API Key | 401 | `"UNAUTHENTICATED"` in error | "Invalid or expired API key" |
| Rate Limited | 429 | `"429"` or `"quota"` in error | "Rate limit exceeded" |
| Network Timeout | N/A | `asyncio.TimeoutError` | "Request timeout after 10s" |
| Connection Error | N/A | `ConnectionError`, `502/503` | "Network error. Check connection." |

### Implementation Example

```python
import asyncio
import google.generativeai as genai
from google.api_core.exceptions import Unauthenticated, ResourceExhausted

class GeminiValidator:
    """Validates Gemini API keys via format and connectivity tests."""

    @staticmethod
    def validate_format(api_key: str) -> tuple[bool, str | None]:
        """Check if key starts with 'AIza' and has reasonable length."""
        if not api_key or len(api_key) < 20:
            return False, "API key is too short"

        if not api_key.startswith('AIza'):
            return False, "Invalid format. Gemini keys typically start with 'AIza'"

        return True, None

    @staticmethod
    async def validate_key(api_key: str) -> tuple[bool, str | None]:
        """Test API key by making minimal request to Gemini API."""
        # Format check first
        valid, error = GeminiValidator.validate_format(api_key)
        if not valid:
            return False, error

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Run in thread pool to avoid blocking
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: model.generate_content(
                        "hi",
                        generation_config={"max_output_tokens": 5}
                    )
                ),
                timeout=10  # 10-second timeout requirement
            )

            if response and hasattr(response, 'text'):
                return True, None

            return False, "Invalid response from Gemini API"

        except asyncio.TimeoutError:
            return False, "Request timeout after 10 seconds"
        except Unauthenticated:
            return False, "API key is invalid or expired"
        except ResourceExhausted:
            return False, "API key quota exceeded"
        except Exception as e:
            if "network" in str(e).lower():
                return False, "Network error. Check your connection."
            return False, f"Validation failed: {str(e)[:100]}"
```

### Cost Analysis

- **Input tokens**: ~2 (1-word prompt)
- **Output tokens**: ~5 (max_output_tokens=5)
- **Cost per validation**: ~$0.0000017 (using gemini-1.5-flash)
- **10,000 validations**: ~$0.017 (less than 2 cents)

**Decision**: ✅ **Use generateContent with 1-word prompt "hi"**

---

## 3. Better-Auth Session Integration

### Decision: Database Query Pattern (Already Implemented)

**Finding**: The project already has a **production-ready better-auth + FastAPI integration** in `backend/src/services/auth_service.py` and `backend/src/api/dependencies.py`.

### How It Works

better-auth uses **stateful session IDs** (not JWTs) stored in the `user_sessions` table:

```
Session Token Format: {tokenId}.{signature}
Database Stores: tokenId only
Validation: Query user_sessions table for tokenId + expiration check
```

### Existing Implementation

**File**: `backend/src/services/auth_service.py`

```python
async def validate_session(token: str, db: AsyncSession) -> Optional[str]:
    """
    Validate a session token and return the user ID.

    Queries user_sessions table for:
    - token matches the provided token (better-auth stores plain tokens)
    - expires_at > now (not expired)
    - revoked == False (supports revocation)
    """
    # Extract token ID from the full token (before the first dot)
    token_id = token.split('.')[0] if '.' in token else token

    # Query for valid session
    current_time_utc = datetime.now(timezone.utc).replace(tzinfo=None)

    stmt = select(UserSession).where(
        UserSession.token == token_id,
        UserSession.expires_at > current_time_utc,
        UserSession.revoked == False
    )

    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if session is None:
        return None

    return session.user_id
```

**File**: `backend/src/api/dependencies.py`

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> str:
    """
    FastAPI dependency to extract and validate authenticated user.

    Usage:
        @router.get("/api/user-api-keys/current")
        async def get_key(user_id: str = Depends(get_current_user)):
            # user_id is automatically injected and validated
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    user_id = await validate_session(token, db)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id
```

### Why This Approach is Optimal

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Database Query (Current)** | Direct truth source; supports revocation; <5ms latency; async-compatible | Requires DB connection | ✅ **RECOMMENDED** |
| JWT Validation | Stateless; no DB queries | Can't revoke; better-auth doesn't use JWTs | ❌ Not applicable |
| Auth-Server API Call | Centralized validation | Network latency; bottleneck; complex errors | ❌ Over-engineering |

### Database Schema

```sql
CREATE TABLE user_sessions (
    id TEXT PRIMARY KEY,           -- CUID
    token TEXT NOT NULL UNIQUE,    -- Session token ID (before the dot)
    user_id TEXT NOT NULL,         -- Foreign key to users
    expires_at TIMESTAMP NOT NULL, -- UTC expiration
    revoked BOOLEAN DEFAULT FALSE, -- Supports immediate revocation
    ip_address TEXT,               -- Optional: client IP
    user_agent TEXT,               -- Optional: browser info
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_user_sessions_token ON user_sessions(token);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
```

**Decision**: ✅ **Use existing database query pattern (already implemented)**

---

## 4. Frontend Password Input Best Practices

### Decision: React Component with Lucide-React Icons

**Requirements**:
- Input masked by default (`type="password"`)
- Show/hide toggle with Eye/EyeOff icons
- No clipboard restrictions (password managers need paste)
- Accessibility (WCAG 2.1 AA)
- Security attributes (autocomplete, spellcheck)

### Implementation

```tsx
'use client';

import { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

interface PasswordInputProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  helperText?: string;
}

export function PasswordInput({
  id,
  label,
  value,
  onChange,
  error,
  helperText,
}: PasswordInputProps) {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="w-full">
      <label
        htmlFor={id}
        className="block text-sm font-medium text-gray-700 mb-2"
      >
        {label}
      </label>

      <div className="relative">
        <input
          id={id}
          type={showPassword ? 'text' : 'password'}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          required
          // Security attributes
          autoComplete="current-password"
          spellCheck="false"
          data-lpignore="true"  // LastPass ignore
          data-1p-ignore         // 1Password ignore
          // Accessibility
          aria-label={label}
          aria-describedby={error ? `${id}-error` : helperText ? `${id}-hint` : undefined}
          aria-invalid={!!error}
          className={`
            w-full px-4 py-2 pr-12 border rounded-lg
            font-medium tracking-widest
            ${
              error
                ? 'border-red-500 focus:ring-2 focus:ring-red-500'
                : 'border-gray-300 focus:ring-2 focus:ring-blue-500'
            }
          `}
        />

        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          aria-label={showPassword ? 'Hide password' : 'Show password'}
          aria-pressed={showPassword}
          className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded text-gray-500 hover:text-gray-700"
        >
          {showPassword ? (
            <EyeOff size={20} aria-hidden="true" />
          ) : (
            <Eye size={20} aria-hidden="true" />
          )}
        </button>
      </div>

      {error && (
        <p id={`${id}-error`} className="mt-1 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}

      {helperText && !error && (
        <p id={`${id}-hint`} className="mt-1 text-sm text-gray-500">
          {helperText}
        </p>
      )}
    </div>
  );
}
```

### Security Attributes Explained

| Attribute | Value | Purpose |
|-----------|-------|---------|
| `autocomplete` | `current-password` | Helps password managers identify field type |
| `spellCheck` | `false` | Prevents keyboard suggestions that could expose partial passwords |
| `data-lpignore` | `true` | Tells LastPass to ignore (if needed for sensitive keys) |
| `data-1p-ignore` | (present) | Tells 1Password to ignore (optional) |
| `type` | `password` or `text` | Dynamically switch to show/hide |

### Accessibility Features

| Feature | Implementation | WCAG Criterion |
|---------|----------------|----------------|
| **Associated Label** | `<label htmlFor={id}>` | 1.3.1 Info and Relationships |
| **ARIA Labels** | `aria-label`, `aria-describedby` | 4.1.2 Name, Role, Value |
| **Error Announcements** | `role="alert"` on error text | 3.3.1 Error Identification |
| **Button States** | `aria-pressed={showPassword}` | 4.1.2 Name, Role, Value |
| **Icon Hiding** | `aria-hidden="true"` on icons | Best practice (no duplicate labels) |
| **Keyboard Navigation** | Native button behavior | 2.1.1 Keyboard Accessible |

### Clipboard Security: DO NOT Restrict Copy/Paste

**Modern best practice**: Allow copy/paste for password manager compatibility. Security is achieved through:
- ✅ HTTPS (protects in transit)
- ✅ Server-side hashing
- ✅ Masked input by default
- ❌ **NOT** through preventing clipboard access

**Decision**: ✅ **Use password-type input with Eye/EyeOff toggle (allow copy/paste)**

---

## 5. SQLAlchemy Encryption Pattern

### Decision: Service-Layer Encryption (NOT TypeDecorator)

**Comparison**:

| Criteria | TypeDecorator | Service Layer | Winner |
|----------|---------------|---------------|--------|
| **Async compatibility** | ⚠️ Problematic (sync hooks) | ✅ Perfect (pure Python) | Service Layer |
| **Accidental logging risk** | ⚠️ High (plaintext in ORM) | ✅ Low (controlled scope) | Service Layer |
| **Testing complexity** | ⚠️ Requires ORM mocking | ✅ Simple unit tests | Service Layer |
| **Code clarity** | ⚠️ "Magic" behavior | ✅ Explicit | Service Layer |
| **Project alignment** | ⚠️ Implicit | ✅ TDD, clean code | Service Layer |
| **Lines of code** | ~20 | ~100 | TypeDecorator |
| **Maintainability** | ⚠️ Harder to debug | ✅ Clear errors | Service Layer |

### Why Service Layer Wins

1. **Async compatibility**: TypeDecorator's synchronous `process_bind_param`/`process_result_value` hooks don't play well with SQLAlchemy 2.0+ async sessions
2. **No accidental logging**: Plaintext only exists in service scope, never in ORM objects
3. **Testable**: Encryption service can be tested without database
4. **Explicit > Implicit**: Follows Python Zen and project constitution
5. **Marginal complexity**: Extra ~80 lines of code is worth the security and maintainability

### Implementation Pattern

**1. EncryptionService (Pure Python, No ORM)**

```python
from cryptography.fernet import Fernet

class EncryptionService:
    """Symmetric encryption using Fernet."""

    def __init__(self, key: str):
        if isinstance(key, str):
            key = key.encode()
        self.cipher = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext and return ciphertext."""
        if not plaintext:
            return ""
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext and return plaintext."""
        if not ciphertext:
            return ""
        try:
            return self.cipher.decrypt(ciphertext.encode()).decode()
        except Exception as exc:
            raise ValueError("Decryption failed - invalid key or corrupted data") from exc
```

**2. Simple Model (No TypeDecorator Magic)**

```python
from sqlalchemy import Column, String, Integer, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class UserApiKey(Base):
    """User's encrypted API key for LLM provider."""

    __tablename__ = "user_api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    encrypted_key = Column(String(500), nullable=False)  # Plain String column
    provider = Column(String(50), default="gemini", nullable=False)
    validation_status = Column(String(50), nullable=True)  # 'success', 'failure', None
    last_validated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'provider', name='uq_user_provider_key'),
    )
```

**3. Service Layer (Explicit Encryption/Decryption)**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

class ApiKeyService:
    """Service for managing encrypted API keys."""

    def __init__(self, session: AsyncSession, encryption: EncryptionService):
        self.session = session
        self.encryption = encryption

    async def save_api_key(
        self,
        user_id: str,
        plaintext_key: str,
        provider: str = "gemini"
    ) -> UserApiKey:
        """Encrypt and save API key."""
        # Explicit encryption
        encrypted_key = self.encryption.encrypt(plaintext_key)

        # Check for existing key
        stmt = select(UserApiKey).where(
            UserApiKey.user_id == user_id,
            UserApiKey.provider == provider
        )
        existing = await self.session.scalar(stmt)

        if existing:
            existing.encrypted_key = encrypted_key
            existing.updated_at = datetime.utcnow()
            await self.session.flush()
            return existing

        # Create new
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
    ) -> str | None:
        """Retrieve and decrypt API key."""
        stmt = select(UserApiKey).where(
            UserApiKey.user_id == user_id,
            UserApiKey.provider == provider
        )
        user_api_key = await self.session.scalar(stmt)

        if not user_api_key:
            return None

        # Explicit decryption
        return self.encryption.decrypt(user_api_key.encrypted_key)

    async def delete_api_key(
        self,
        user_id: str,
        provider: str = "gemini"
    ) -> bool:
        """Delete API key."""
        stmt = delete(UserApiKey).where(
            UserApiKey.user_id == user_id,
            UserApiKey.provider == provider
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
```

**4. Unit Test (No Database Needed)**

```python
import pytest
from cryptography.fernet import Fernet

def test_encryption_round_trip():
    """Test that encryption and decryption are inverses."""
    key = Fernet.generate_key()
    service = EncryptionService(key)
    plaintext = "AIzaSyDPjJjPjVq_yqBN6OdqY5Hk3gV4ZfmULeo"

    encrypted = service.encrypt(plaintext)
    decrypted = service.decrypt(encrypted)

    assert decrypted == plaintext
    assert encrypted != plaintext  # Verify it's actually encrypted


def test_decrypt_with_wrong_key_fails():
    """Test that decryption fails with wrong key."""
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()

    service1 = EncryptionService(key1)
    service2 = EncryptionService(key2)

    plaintext = "TestKey123"
    encrypted = service1.encrypt(plaintext)

    with pytest.raises(ValueError, match="Decryption failed"):
        service2.decrypt(encrypted)
```

### Key Management

**Generate Key (One-Time)**:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Store Securely**:
```bash
# .env (development)
ENCRYPTION_KEY=<generated-key>

# Production: Use secrets manager (GitHub Secrets, AWS Secrets Manager, etc.)
```

**Load in Config**:
```python
from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet

class Settings(BaseSettings):
    ENCRYPTION_KEY: str

    def validate_encryption_key(self):
        try:
            Fernet(self.ENCRYPTION_KEY.encode())
        except Exception:
            raise ValueError("Invalid ENCRYPTION_KEY format")

settings = Settings()
settings.validate_encryption_key()
```

**Decision**: ✅ **Use service-layer encryption (not TypeDecorator)**

---

## Summary: All Decisions

| Research Area | Decision | Rationale |
|---------------|----------|-----------|
| **Encryption Library** | cryptography (Fernet) | Industry standard, secure defaults, simple API |
| **Gemini Validation** | generateContent with 1-word prompt | Minimal cost, full validation, 10s timeout |
| **Auth Integration** | Database query (existing pattern) | Already implemented, production-ready |
| **Password Input** | React with Eye/EyeOff toggle | Accessible, secure, allows copy/paste |
| **SQLAlchemy Encryption** | Service-layer encryption | Async-compatible, testable, explicit |

All decisions align with:
- ✅ **Test-First Development**: Easy to write tests before implementation
- ✅ **Clean Code & Simplicity**: Explicit, no magic behavior
- ✅ **Proper Structure**: Clear separation of concerns
- ✅ **Project Principles**: YAGNI, clean code, testability

---

## Next Steps

With all research complete, proceed to:

1. **Phase 1: Design**
   - Generate `data-model.md` with `user_api_keys` table schema
   - Generate API contracts (OpenAPI spec for /api/user-api-keys endpoints)
   - Generate `quickstart.md` with setup instructions

2. **Phase 2: Tasks**
   - Break down implementation into 20-30 minute atomic tasks
   - Follow TDD cycle (Red-Green-Refactor)

3. **Implementation**
   - Write tests first
   - Implement encryption service, API key service, routes, frontend components
   - Integrate with AI agent for per-user API key retrieval
