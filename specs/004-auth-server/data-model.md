# Data Model: Better Auth Server for FastAPI Integration

**Feature**: 004-auth-server
**Phase**: 1 (Design & Contracts)
**Date**: 2025-12-10
**Status**: Complete

## Overview

This document defines the data entities, relationships, validation rules, and state transitions for the authentication system. The model is designed to support both the Node.js auth server (using Prisma) and FastAPI backend (using SQLAlchemy).

---

## Entity Definitions

### 1. User

Represents a registered user account with credentials and profile information.

#### Schema (Prisma)

```prisma
model User {
  id            String    @id @default(cuid())
  email         String    @unique
  emailVerified Boolean   @default(false) @map("email_verified")
  password      String?   // Nullable for OAuth-only users
  name          String?
  image         String?
  createdAt     DateTime  @default(now()) @map("created_at")
  updatedAt     DateTime  @updatedAt @map("updated_at")

  // Relations
  sessions      Session[]
  accounts      Account[]  // OAuth accounts

  @@map("users")
}
```

#### Schema (SQLAlchemy)

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    password: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    image: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relations
    sessions: Mapped[List["Session"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    accounts: Mapped[List["Account"]] = relationship(back_populates="user", cascade="all, delete-orphan")
```

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | String (cuid) | Primary Key | Unique user identifier (collision-resistant) |
| `email` | String | Unique, Not Null, Max 255 | User's email address (lowercase normalized) |
| `emailVerified` | Boolean | Default: false | Whether email has been verified |
| `password` | String (nullable) | Min 8 chars (if present) | Bcrypt-hashed password (null for OAuth-only users) |
| `name` | String (nullable) | Max 100 chars | User's display name |
| `image` | String (nullable) | Valid URL | Profile picture URL |
| `createdAt` | DateTime | Auto-generated | Account creation timestamp |
| `updatedAt` | DateTime | Auto-updated | Last modification timestamp |

#### Validation Rules

**Email** (FR-001, FR-002):
- Must be valid email format (regex: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`)
- Converted to lowercase before storage
- Unique across all users
- Max length: 255 characters

**Password** (FR-002):
- Required for email/password authentication
- Nullable for OAuth-only users
- Min length: 8 characters
- Hashed with bcrypt (cost factor: 10)
- Never returned in API responses

**Name**:
- Optional
- Max length: 100 characters
- Sanitized to prevent XSS

**Image**:
- Optional
- Must be valid HTTPS URL if provided
- Max length: 500 characters

#### State Transitions

```
┌─────────────┐
│   Created   │ (emailVerified: false, password: hashed)
└──────┬──────┘
       │
       │ User clicks verification link (FR-001)
       ▼
┌─────────────┐
│  Verified   │ (emailVerified: true)
└──────┬──────┘
       │
       │ User initiates password reset (FR-003)
       ▼
┌─────────────────┐
│ Reset Requested │ (PasswordReset token created)
└──────┬──────────┘
       │
       │ User submits new password
       ▼
┌─────────────┐
│  Verified   │ (password updated)
└─────────────┘
```

#### Business Rules

1. **Email Uniqueness**: Only one user per email address
2. **Verification Required**: `emailVerified` must be true before accessing protected resources (FR-001)
3. **Password Changes**: Old sessions optionally invalidated on password change (security feature)
4. **OAuth Linking**: Multiple OAuth accounts can link to one user email

---

### 2. Session

Represents an active user session with authentication token and device metadata.

#### Schema (Prisma)

```prisma
model Session {
  id         String   @id @default(cuid())
  userId     String   @map("user_id")
  token      String   @unique  // JWT or opaque session token
  expiresAt  DateTime @map("expires_at")
  ipAddress  String?  @map("ip_address")  // ⚠️ Use String, NOT ip_address type
  userAgent  String?  @map("user_agent")
  createdAt  DateTime @default(now()) @map("created_at")
  updatedAt  DateTime @updatedAt @map("updated_at")

  // Relations
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("user_sessions")
  @@index([userId])
  @@index([token])
  @@index([expiresAt])
}
```

#### Schema (SQLAlchemy)

```python
class Session(Base):
    __tablename__ = "user_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # ⚠️ Use Text, NOT INET
    user_agent: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relations
    user: Mapped["User"] = relationship(back_populates="sessions")

    # Indexes
    __table_args__ = (
        Index("idx_sessions_user_id", "user_id"),
        Index("idx_sessions_token", "token"),
        Index("idx_sessions_expires_at", "expires_at"),
    )
```

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | String (cuid) | Primary Key | Unique session identifier |
| `userId` | String | Foreign Key (User.id), Indexed | Associated user ID |
| `token` | String | Unique, Not Null, Indexed | Session token (JWT or opaque) |
| `expiresAt` | DateTime | Not Null, Indexed | Session expiration timestamp |
| `ipAddress` | String (nullable) | Max 45 chars | Client IP address (IPv4/IPv6) |
| `userAgent` | String (nullable) | Max 500 chars | Browser/device user agent |
| `createdAt` | DateTime | Auto-generated | Session creation timestamp |
| `updatedAt` | DateTime | Auto-updated | Last session update timestamp |

#### Validation Rules

**Token** (FR-004):
- Generated by better-auth (cryptographically secure random)
- Min length: 32 characters
- Unique across all sessions
- Indexed for fast lookup

**ExpiresAt** (FR-006):
- Default: 7 days from creation (configurable)
- Access tokens: 15 minutes
- Refresh tokens: 7 days
- Must be in future when created

**IpAddress**:
- Extracted from request headers (`X-Forwarded-For` or `req.ip`)
- Format: IPv4 (xxx.xxx.xxx.xxx) or IPv6 (xxxx:xxxx:...)
- Max length: 45 characters (IPv6)
- ⚠️ **CRITICAL**: Use `String`/`Text` type, NOT PostgreSQL `INET` type (Prisma incompatibility)

**UserAgent**:
- Extracted from `User-Agent` header
- Max length: 500 characters
- Truncated if longer
- Used for device identification (FR-006a)

#### State Transitions

```
┌─────────────┐
│   Created   │ (expiresAt: now + 7 days)
└──────┬──────┘
       │
       │ Time passes, session still valid
       ▼
┌─────────────┐
│   Active    │ (expiresAt > now)
└──────┬──────┘
       │
       ├─── User logs out (FR-008) ──▶ [Deleted]
       │
       ├─── Expires naturally ──▶ [Expired] (expiresAt < now)
       │
       └─── User revokes session (FR-006b) ──▶ [Deleted]
```

#### Business Rules (FR-006a, FR-006b)

1. **Multiple Sessions**: Users can have unlimited concurrent sessions
2. **Session Revocation**: Individual sessions can be revoked without affecting others
3. **Automatic Cleanup**: Expired sessions deleted after grace period (24 hours)
4. **Device Tracking**: IP + User-Agent used for device fingerprinting
5. **Location Tracking**: IP address can be geocoded for location display (future feature)

---

### 3. Account (OAuth)

Represents an OAuth provider account linked to a user.

#### Schema (Prisma)

```prisma
model Account {
  id                String  @id @default(cuid())
  userId            String  @map("user_id")
  type              String  // "oauth"
  provider          String  // "google", "github", etc.
  providerAccountId String  @map("provider_account_id")
  refreshToken      String? @map("refresh_token")
  accessToken       String? @map("access_token")
  expiresAt         Int?    @map("expires_at")
  tokenType         String? @map("token_type")
  scope             String?
  idToken           String? @map("id_token")
  sessionState      String? @map("session_state")
  createdAt         DateTime @default(now()) @map("created_at")
  updatedAt         DateTime @updatedAt @map("updated_at")

  // Relations
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
  @@map("accounts")
}
```

#### Schema (SQLAlchemy)

```python
class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    provider_account_id: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expires_at: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    token_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    scope: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    id_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    session_state: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relations
    user: Mapped["User"] = relationship(back_populates="accounts")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint("provider", "provider_account_id", name="uq_provider_account"),
    )
```

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | String (cuid) | Primary Key | Unique account identifier |
| `userId` | String | Foreign Key (User.id) | Associated user ID |
| `type` | String | Not Null | Account type (always "oauth") |
| `provider` | String | Not Null | OAuth provider (google, github, apple) |
| `providerAccountId` | String | Not Null, Unique with provider | Provider's user ID |
| `accessToken` | String (nullable) | Encrypted at rest | OAuth access token |
| `refreshToken` | String (nullable) | Encrypted at rest | OAuth refresh token |
| `expiresAt` | Integer (nullable) | Unix timestamp | Access token expiration |
| `tokenType` | String (nullable) | e.g., "Bearer" | Token type |
| `scope` | String (nullable) | e.g., "email profile" | OAuth scopes granted |
| `idToken` | String (nullable) | JWT from provider | OpenID Connect ID token |
| `sessionState` | String (nullable) | OAuth session state | Provider-specific session state |

#### Validation Rules (FR-009)

**Provider**:
- Allowed values: `google`, `github`, `apple` (initial: `google`)
- Case-insensitive, stored lowercase

**ProviderAccountId**:
- Unique per provider (one Google account = one Account record)
- Can link multiple providers to same User (email matching)

**Tokens**:
- Encrypted at rest using AES-256
- Never returned in API responses
- Refresh token used to renew access token

#### Business Rules (FR-009)

1. **Account Linking**: If OAuth email matches existing user email, link to that user
2. **Multi-Provider**: One user can have multiple OAuth accounts (Google + GitHub)
3. **Token Refresh**: Refresh tokens exchanged for new access tokens when expired
4. **Provider Uniqueness**: One provider account can only link to one user

---

### 4. VerificationToken

Represents an email verification or password reset token.

#### Schema (Prisma)

```prisma
model VerificationToken {
  id         String   @id @default(cuid())
  identifier String   // Email address
  token      String   @unique
  type       String   // "email_verification" or "password_reset"
  expiresAt  DateTime @map("expires_at")
  createdAt  DateTime @default(now()) @map("created_at")

  @@unique([identifier, type])
  @@map("verification_tokens")
}
```

#### Schema (SQLAlchemy)

```python
class VerificationToken(Base):
    __tablename__ = "verification_tokens"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    identifier: Mapped[str] = mapped_column(String, nullable=False)  # Email
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("identifier", "type", name="uq_identifier_type"),
    )
```

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | String (cuid) | Primary Key | Unique token record ID |
| `identifier` | String | Not Null, Unique with type | Email address |
| `token` | String | Unique, Not Null | Verification token (random 32-byte hex) |
| `type` | String | Not Null | Token type (email_verification, password_reset) |
| `expiresAt` | DateTime | Not Null | Token expiration timestamp |
| `createdAt` | DateTime | Auto-generated | Token creation timestamp |

#### Validation Rules (FR-001, FR-003)

**Token**:
- Generated with `crypto.randomBytes(32).toString('hex')`
- Length: 64 characters (hex-encoded)
- Unique across all tokens
- Single-use (deleted after verification)

**ExpiresAt**:
- **Email Verification**: 15 minutes from creation
- **Password Reset**: 1 hour from creation
- Must be in future when created

**Type**:
- Allowed values: `email_verification`, `password_reset`
- Determines expiration duration

#### State Transitions

```
┌─────────────┐
│   Created   │ (sent via email)
└──────┬──────┘
       │
       ├─── User clicks link before expiration ──▶ [Used] → [Deleted]
       │
       └─── Token expires ──▶ [Expired] → [Deleted after 24h]
```

#### Business Rules (FR-001, FR-003)

1. **Single Use**: Token deleted immediately after successful verification
2. **One Active Token**: Only one token per (identifier, type) pair
3. **Expiration**: Tokens expire based on type (15 min or 1 hour)
4. **Cleanup**: Expired tokens deleted after 24-hour grace period

---

## Entity Relationships

### ER Diagram

```
┌─────────────┐
│    User     │
│ id (PK)     │
│ email       │
│ password    │
│ ...         │
└──────┬──────┘
       │
       │ 1
       │
       │ N
       ├───────────────────────────┐
       │                           │
       ▼                           ▼
┌─────────────┐            ┌──────────────┐
│   Session   │            │   Account    │
│ id (PK)     │            │ id (PK)      │
│ userId (FK) │            │ userId (FK)  │
│ token       │            │ provider     │
│ expiresAt   │            │ accessToken  │
│ ...         │            │ ...          │
└─────────────┘            └──────────────┘

┌──────────────────────┐
│  VerificationToken   │
│  id (PK)             │
│  identifier (email)  │
│  token               │
│  type                │
│  expiresAt           │
└──────────────────────┘
```

### Relationships

| Parent | Child | Type | Cascade | Description |
|--------|-------|------|---------|-------------|
| User | Session | 1:N | Delete | One user has many sessions |
| User | Account | 1:N | Delete | One user has many OAuth accounts |

**Notes**:
- `VerificationToken` is standalone (no foreign key to User)
- Cascade delete: Deleting user deletes all sessions and accounts
- Orphaned sessions/accounts impossible due to `onDelete: Cascade`

---

## Indexes

### Performance Optimization

| Table | Column(s) | Type | Reason |
|-------|-----------|------|--------|
| users | email | Unique | Fast lookup during login |
| user_sessions | user_id | Index | Fast session queries per user |
| user_sessions | token | Unique | Fast token validation |
| user_sessions | expires_at | Index | Fast expired session cleanup |
| accounts | (provider, provider_account_id) | Unique | Prevent duplicate OAuth links |
| verification_tokens | token | Unique | Fast token lookup |
| verification_tokens | (identifier, type) | Unique | One active token per email/type |

---

## Data Integrity Constraints

### Database-Level Constraints

```sql
-- Users
ALTER TABLE users ADD CONSTRAINT chk_email_format
  CHECK (email ~* '^[^\s@]+@[^\s@]+\.[^\s@]+$');

-- Sessions
ALTER TABLE user_sessions ADD CONSTRAINT chk_expires_future
  CHECK (expires_at > created_at);

-- Accounts
ALTER TABLE accounts ADD CONSTRAINT chk_provider_lowercase
  CHECK (provider = LOWER(provider));

-- Verification Tokens
ALTER TABLE verification_tokens ADD CONSTRAINT chk_token_length
  CHECK (LENGTH(token) = 64);
ALTER TABLE verification_tokens ADD CONSTRAINT chk_type_valid
  CHECK (type IN ('email_verification', 'password_reset'));
```

### Application-Level Validation

```python
# Pydantic models for FastAPI
class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    password: str = Field(min_length=8, max_length=128)
    name: Optional[str] = Field(None, max_length=100)

class SessionCreate(BaseModel):
    token: str = Field(min_length=32)
    expires_at: datetime

    @validator('expires_at')
    def expires_in_future(cls, v):
        if v <= datetime.utcnow():
            raise ValueError('expiresAt must be in future')
        return v
```

---

## Migration Strategy

### Initial Migration (Alembic)

```python
# backend/src/database/migrations/versions/001_create_auth_tables.py
def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('email', sa.String(), unique=True, nullable=False),
        sa.Column('email_verified', sa.Boolean(), default=False),
        sa.Column('password', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('image', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), onupdate=datetime.utcnow),
    )

    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(), unique=True, nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.Text(), nullable=True),  # ⚠️ Use Text, NOT INET
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), onupdate=datetime.utcnow),
    )

    # Create accounts table
    op.create_table(
        'accounts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('provider_account_id', sa.String(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.Integer(), nullable=True),
        sa.Column('token_type', sa.String(), nullable=True),
        sa.Column('scope', sa.String(), nullable=True),
        sa.Column('id_token', sa.Text(), nullable=True),
        sa.Column('session_state', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), onupdate=datetime.utcnow),
    )

    # Create verification_tokens table
    op.create_table(
        'verification_tokens',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('identifier', sa.String(), nullable=False),
        sa.Column('token', sa.String(), unique=True, nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
    )

    # Create indexes
    op.create_index('idx_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('idx_sessions_token', 'user_sessions', ['token'])
    op.create_index('idx_sessions_expires_at', 'user_sessions', ['expires_at'])
    op.create_unique_constraint('uq_provider_account', 'accounts', ['provider', 'provider_account_id'])
    op.create_unique_constraint('uq_identifier_type', 'verification_tokens', ['identifier', 'type'])

def downgrade():
    op.drop_table('verification_tokens')
    op.drop_table('accounts')
    op.drop_table('user_sessions')
    op.drop_table('users')
```

### Prisma Migration

```prisma
// auth-server/prisma/schema.prisma
// Run: npx prisma db push
// This creates tables in Neon PostgreSQL
// Alembic migration must match this schema exactly
```

---

## Next Steps (Phase 1 Continued)

1. **Generate API Contracts**: Define OpenAPI specs in `contracts/` directory
2. **Generate Quickstart Guide**: Setup instructions in `quickstart.md`
3. **Update Agent Context**: Add technologies to `.claude/agents/` context files

---

**Data Model Complete** ✅
**Ready for**: API contract generation
