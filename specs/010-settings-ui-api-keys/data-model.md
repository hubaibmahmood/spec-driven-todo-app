# Data Model: Settings UI for API Key Management

**Feature**: 010-settings-ui-api-keys
**Date**: 2025-12-24
**Context**: Database schema and entities for secure user API key storage

---

## Overview

This feature introduces one new database table (`user_api_keys`) to store encrypted Gemini API keys per user. The encryption happens at the service layer (not ORM level) using the cryptography library with Fernet.

---

## Entity Diagram

```
┌─────────────────┐
│     users       │
│  (existing)     │
├─────────────────┤
│ id (UUID/TEXT)  │←────┐
│ email           │     │
│ ...             │     │
└─────────────────┘     │
                        │ Foreign Key
                        │
┌─────────────────────┐ │
│   user_api_keys     │ │
│     (NEW)           │ │
├─────────────────────┤ │
│ id (INTEGER PK)     │ │
│ user_id (TEXT FK)───┘
│ encrypted_key (TEXT)│ ← Service-layer encrypted using Fernet
│ provider (TEXT)     │ ← 'gemini' (extensible for future providers)
│ validation_status   │ ← 'success' | 'failure' | NULL
│ last_validated_at   │ ← Timestamp of last Test Connection
│ created_at          │
│ updated_at          │
└─────────────────────┘
   Unique: (user_id, provider)
```

---

## Table: `user_api_keys`

### Purpose
Stores encrypted API keys for external LLM providers (initially Gemini only). Each user can have one API key per provider.

### Schema

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO_INCREMENT | Primary key |
| `user_id` | TEXT/VARCHAR(255) | NO | - | Foreign key to `users.id` |
| `encrypted_key` | TEXT/VARCHAR(500) | NO | - | **Ciphertext** (encrypted using Fernet) |
| `provider` | VARCHAR(50) | NO | `'gemini'` | Provider name (e.g., 'gemini', 'openai') |
| `validation_status` | VARCHAR(50) | YES | NULL | Last validation result: `'success'`, `'failure'`, or NULL |
| `last_validated_at` | TIMESTAMP | YES | NULL | UTC timestamp of last Test Connection attempt |
| `created_at` | TIMESTAMP | NO | `NOW()` | UTC timestamp of key creation |
| `updated_at` | TIMESTAMP | NO | `NOW()` | UTC timestamp of last key update (auto-updated) |

### Indexes

```sql
CREATE INDEX idx_user_api_keys_user_id ON user_api_keys(user_id);
CREATE UNIQUE INDEX uq_user_provider_key ON user_api_keys(user_id, provider);
```

### Constraints

- **Primary Key**: `id`
- **Foreign Key**: `user_id` REFERENCES `users(id)` ON DELETE CASCADE
- **Unique Constraint**: `(user_id, provider)` - Each user can have only one key per provider

### Example Rows

| id | user_id | encrypted_key | provider | validation_status | last_validated_at | created_at | updated_at |
|----|---------|---------------|----------|-------------------|-------------------|------------|------------|
| 1 | user-123 | `gAAAABl...xyz=` | gemini | success | 2025-12-24 10:30:00 | 2025-12-24 10:25:00 | 2025-12-24 10:30:00 |
| 2 | user-456 | `gAAAABm...abc=` | gemini | NULL | NULL | 2025-12-24 11:00:00 | 2025-12-24 11:00:00 |
| 3 | user-789 | `gAAAABn...def=` | gemini | failure | 2025-12-24 11:15:00 | 2025-12-24 11:10:00 | 2025-12-24 11:15:00 |

---

## SQLAlchemy Model

```python
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserApiKey(Base):
    """
    Stores encrypted API keys for external LLM providers.

    Encryption/decryption happens at service layer (ApiKeyService),
    not at ORM level (no TypeDecorator).
    """

    __tablename__ = "user_api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    encrypted_key = Column(String(500), nullable=False)  # Ciphertext (Fernet-encrypted)
    provider = Column(String(50), nullable=False, default="gemini")
    validation_status = Column(String(50), nullable=True)  # 'success', 'failure', or NULL
    last_validated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'provider', name='uq_user_provider_key'),
    )

    def __repr__(self) -> str:
        return f"<UserApiKey(id={self.id}, user_id={self.user_id}, provider={self.provider})>"
```

---

## Alembic Migration

**File**: `backend/alembic/versions/XXXX_create_user_api_keys_table.py`

```python
"""Create user_api_keys table for encrypted API key storage

Revision ID: XXXX
Revises: <previous_revision>
Create Date: 2025-12-24
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'XXXX'
down_revision = '<previous_revision>'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user_api_keys',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('encrypted_key', sa.String(length=500), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False, server_default='gemini'),
        sa.Column('validation_status', sa.String(length=50), nullable=True),
        sa.Column('last_validated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'provider', name='uq_user_provider_key')
    )
    op.create_index('idx_user_api_keys_user_id', 'user_api_keys', ['user_id'])


def downgrade() -> None:
    op.drop_index('idx_user_api_keys_user_id', table_name='user_api_keys')
    op.drop_table('user_api_keys')
```

---

## Encryption Flow

### Save API Key Flow

```
User Input (Plaintext Key)
        ↓
[EncryptionService.encrypt(plaintext)]
        ↓
Ciphertext (Fernet-encrypted)
        ↓
[ApiKeyService.save_api_key()]
        ↓
user_api_keys.encrypted_key ← Store in database
```

### Retrieve API Key Flow

```
Database Query
        ↓
user_api_keys.encrypted_key (Ciphertext)
        ↓
[EncryptionService.decrypt(ciphertext)]
        ↓
Plaintext Key
        ↓
Return to caller (AI agent, validation service)
```

### Key Points

- **Plaintext never touches the ORM**: Service layer handles encryption/decryption
- **Safe to log model objects**: `encrypted_key` contains ciphertext, not plaintext
- **Master key**: `ENCRYPTION_KEY` environment variable (Fernet key)
- **Key derivation**: Optional (currently using direct Fernet key)

---

## Validation Status State Machine

```
NULL (Initial State)
  │
  ├─ Test Connection (successful) ──→ 'success'
  ├─ Test Connection (failed)     ──→ 'failure'
  └─ No test performed            ──→ NULL

'success'
  │
  ├─ Test Connection (successful) ──→ 'success' (refresh last_validated_at)
  ├─ Test Connection (failed)     ──→ 'failure'
  └─ Key updated                  ──→ NULL (reset status until tested)

'failure'
  │
  ├─ Test Connection (successful) ──→ 'success'
  ├─ Test Connection (failed)     ──→ 'failure' (update last_validated_at)
  └─ Key updated                  ──→ NULL (reset status)
```

**Transitions**:
- **Key saved without test**: `validation_status = NULL`
- **Test Connection succeeds**: `validation_status = 'success'`, `last_validated_at = NOW()`
- **Test Connection fails**: `validation_status = 'failure'`, `last_validated_at = NOW()`
- **Key updated**: Reset `validation_status = NULL` (force re-validation)

---

## Data Access Patterns

### Pattern 1: Save API Key (Create/Update)

```python
# Service layer
encryption = EncryptionService(settings.ENCRYPTION_KEY)
api_key_service = ApiKeyService(session, encryption)

user_api_key = await api_key_service.save_api_key(
    user_id="user-123",
    plaintext_key="AIzaSyDPjJjPjVq_yqBN6OdqY5Hk3gV4ZfmULeo",
    provider="gemini"
)
# Sets encrypted_key = <ciphertext>, validation_status = NULL
```

### Pattern 2: Retrieve and Decrypt API Key

```python
# Service layer
plaintext_key = await api_key_service.get_api_key(
    user_id="user-123",
    provider="gemini"
)
# Returns: "AIzaSyDPjJjPjVq_yqBN6OdqY5Hk3gV4ZfmULeo" or None
```

### Pattern 3: Delete API Key

```python
# Service layer
deleted = await api_key_service.delete_api_key(
    user_id="user-123",
    provider="gemini"
)
# Returns: True if deleted, False if not found
```

### Pattern 4: Update Validation Status

```python
# After Test Connection
user_api_key.validation_status = "success"
user_api_key.last_validated_at = datetime.utcnow()
await session.flush()
```

---

## Security Considerations

### What's Protected

✅ **At-rest encryption**: Keys encrypted in PostgreSQL using Fernet
✅ **Service-layer control**: Plaintext never enters ORM layer
✅ **Safe logging**: Models contain ciphertext only
✅ **User isolation**: Each user has separate encrypted key (unique constraint)

### What's NOT Protected

⚠️ **In-transit encryption**: Use HTTPS (handled by production deployment)
⚠️ **Plaintext in memory**: Necessary for decryption (controlled scope in service)
⚠️ **Database access**: If attacker has DB + ENCRYPTION_KEY, can decrypt
⚠️ **ENCRYPTION_KEY exposure**: Master key must be protected (secrets manager)

### Best Practices

1. Store `ENCRYPTION_KEY` in secrets manager (not `.env` in production)
2. Rotate `ENCRYPTION_KEY` quarterly or after suspected compromise
3. Never log plaintext keys (service layer makes this safe by default)
4. Use HTTPS for all API requests
5. Monitor unusual access patterns

---

## Testing Strategy

### Unit Tests (No Database)

```python
def test_encryption_round_trip():
    encryption = EncryptionService(Fernet.generate_key())
    plaintext = "AIzaSyDPjJjPjVq_yqBN6OdqY5Hk3gV4ZfmULeo"

    encrypted = encryption.encrypt(plaintext)
    decrypted = encryption.decrypt(encrypted)

    assert decrypted == plaintext
    assert encrypted != plaintext
```

### Contract Tests (Database Required)

```python
@pytest.mark.asyncio
async def test_user_api_key_crud():
    # Create
    user_api_key = UserApiKey(
        user_id="user-123",
        encrypted_key="<ciphertext>",
        provider="gemini"
    )
    session.add(user_api_key)
    await session.commit()

    # Read
    result = await session.get(UserApiKey, user_api_key.id)
    assert result.user_id == "user-123"

    # Update
    result.validation_status = "success"
    await session.commit()

    # Delete
    await session.delete(result)
    await session.commit()
```

### Integration Tests (Full Flow)

```python
@pytest.mark.asyncio
async def test_save_and_retrieve_encrypted_key():
    encryption = EncryptionService(TEST_KEY)
    service = ApiKeyService(session, encryption)

    # Save
    saved = await service.save_api_key("user-123", "AIzaTestKey")
    assert saved.encrypted_key != "AIzaTestKey"  # Verify encrypted

    # Retrieve
    decrypted = await service.get_api_key("user-123")
    assert decrypted == "AIzaTestKey"  # Verify decryption
```

---

## Summary

- **New Table**: `user_api_keys` (8 columns, 2 indexes, 1 unique constraint)
- **Encryption**: Service-layer using Fernet (not TypeDecorator)
- **Access Pattern**: Create/Read/Update/Delete via `ApiKeyService`
- **Security**: At-rest encryption with master ENCRYPTION_KEY
- **Validation Tracking**: Status + timestamp for Test Connection feature
- **Extensibility**: Provider column supports future multi-provider scenarios
