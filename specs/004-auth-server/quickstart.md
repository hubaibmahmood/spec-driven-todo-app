# Quick Start Guide: Better Auth Server + FastAPI Integration

**Feature**: 004-auth-server
**Phase**: 1 (Design & Contracts)
**Date**: 2025-12-10

## Overview

This guide walks you through setting up the better-auth authentication server and integrating it with your FastAPI application. Follow these steps sequentially for a working authentication system.

**Total Setup Time**: ~30-45 minutes

---

## Prerequisites

Before starting, ensure you have:

- ✅ **Node.js 20+** ([Download](https://nodejs.org/))
- ✅ **Python 3.12+** with `uv` package manager ([Install UV](https://github.com/astral-sh/uv))
- ✅ **PostgreSQL database** (we'll use Neon Serverless)
- ✅ **Git** for version control
- ✅ **Code editor** (VS Code recommended)

---

## Step 1: Database Setup (Neon PostgreSQL)

### 1.1 Create Neon Account

1. Go to [https://neon.tech](https://neon.tech)
2. Sign up with GitHub or email
3. Create a new project: "todo-app-auth"
4. Select region closest to you

### 1.2 Get Database URL

1. In Neon dashboard, click "Connection String"
2. Copy the connection string (looks like):
   ```
   postgresql://user:password@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
3. Save this for later (you'll need it in `.env` files)

### 1.3 Configure Connection Pooling

Neon automatically provides connection pooling at no extra cost.

**Connection limits**:
- **Free tier**: 100 concurrent connections
- **Shared between**: Auth server + API server

**Expected usage**:
- Auth server: ~20 connections
- API server: ~15 connections
- Headroom: 65 connections for scaling

---

## Step 2: Auth Server Setup (Node.js)

### 2.1 Create Auth Server Directory

```bash
cd /path/to/todo-app
mkdir -p auth-server
cd auth-server
```

### 2.2 Initialize Node.js Project

```bash
npm init -y
```

### 2.3 Edit package.json

Add `"type": "module"` for ESM support:

```json
{
  "name": "auth-server",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "vercel-build": "prisma generate && tsc"
  }
}
```

### 2.4 Install Dependencies

```bash
npm install better-auth express cors dotenv @prisma/client
npm install -D typescript tsx @types/node @types/express @types/cors prisma
```

**Dependency explanations**:
- `better-auth`: Authentication library
- `express`: Web framework
- `@prisma/client`: Database ORM
- `tsx`: TypeScript execution for development

### 2.5 Initialize TypeScript

```bash
npx tsc --init
```

Edit `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "node",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### 2.6 Initialize Prisma

```bash
npx prisma init
```

This creates:
- `prisma/schema.prisma` (database schema)
- `.env` (environment variables)

### 2.7 Configure Environment Variables

Edit `auth-server/.env`:

```bash
# Database (from Step 1.2)
DATABASE_URL="postgresql://user:password@ep-xxx.neon.tech/neondb?sslmode=require"

# Server
NODE_ENV=development
PORT=3000

# Security
JWT_SECRET="your-secret-key-min-32-characters-long-random-string"

# CORS (frontend URLs)
CORS_ORIGINS="http://localhost:3000,http://localhost:5173"

# Email service (Resend)
RESEND_API_KEY="re_your_api_key"  # Sign up at https://resend.com
EMAIL_FROM="noreply@yourdomain.com"

# Frontend
FRONTEND_URL="http://localhost:3000"

# OAuth (Google)
GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
GOOGLE_REDIRECT_URI="http://localhost:3000/api/auth/callback/google"
```

**To generate JWT_SECRET**:
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### 2.8 Define Prisma Schema

Edit `prisma/schema.prisma`:

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id            String    @id @default(cuid())
  email         String    @unique
  emailVerified Boolean   @default(false) @map("email_verified")
  password      String?
  name          String?
  image         String?
  createdAt     DateTime  @default(now()) @map("created_at")
  updatedAt     DateTime  @updatedAt @map("updated_at")

  sessions      Session[]
  accounts      Account[]

  @@map("users")
}

model Session {
  id         String   @id @default(cuid())
  userId     String   @map("user_id")
  token      String   @unique
  expiresAt  DateTime @map("expires_at")
  ipAddress  String?  @map("ip_address")
  userAgent  String?  @map("user_agent")
  createdAt  DateTime @default(now()) @map("created_at")
  updatedAt  DateTime @updatedAt @map("updated_at")

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("user_sessions")
  @@index([userId])
  @@index([token])
  @@index([expiresAt])
}

model Account {
  id                String   @id @default(cuid())
  userId            String   @map("user_id")
  type              String
  provider          String
  providerAccountId String   @map("provider_account_id")
  refreshToken      String?  @map("refresh_token")
  accessToken       String?  @map("access_token")
  expiresAt         Int?     @map("expires_at")
  tokenType         String?  @map("token_type")
  scope             String?
  idToken           String?  @map("id_token")
  sessionState      String?  @map("session_state")
  createdAt         DateTime @default(now()) @map("created_at")
  updatedAt         DateTime @updatedAt @map("updated_at")

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
  @@map("accounts")
}

model VerificationToken {
  id         String   @id @default(cuid())
  identifier String
  token      String   @unique
  type       String
  expiresAt  DateTime @map("expires_at")
  createdAt  DateTime @default(now()) @map("created_at")

  @@unique([identifier, type])
  @@map("verification_tokens")
}
```

### 2.9 Push Schema to Database

```bash
npx prisma db push
```

This creates all tables in your Neon database.

### 2.10 Generate Prisma Client

```bash
npx prisma generate
```

---

## Step 3: Auth Server Code

### 3.1 Create Directory Structure

```bash
mkdir -p src/auth src/config src/database src/middleware src/utils
```

### 3.2 Environment Configuration

Create `src/config/env.ts`:

```typescript
import dotenv from 'dotenv';
dotenv.config();

export const env = {
  nodeEnv: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '3000'),
  databaseUrl: process.env.DATABASE_URL!,
  jwtSecret: process.env.JWT_SECRET!,
  corsOrigins: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'],
  resendApiKey: process.env.RESEND_API_KEY,
  emailFrom: process.env.EMAIL_FROM || 'noreply@example.com',
  frontendUrl: process.env.FRONTEND_URL || 'http://localhost:3000',
  google: {
    clientId: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    redirectUri: process.env.GOOGLE_REDIRECT_URI,
  },
};

// Validate required variables
const required = ['databaseUrl', 'jwtSecret'];
for (const key of required) {
  if (!env[key as keyof typeof env]) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
}
```

### 3.3 Prisma Client

Create `src/database/client.ts`:

```typescript
import { PrismaClient } from '@prisma/client';

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
  });

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma;
}
```

### 3.4 Better-Auth Configuration

Create `src/auth/auth.config.ts`:

```typescript
import { betterAuth } from 'better-auth';
import { prismaAdapter } from 'better-auth/adapters/prisma';
import { Resend } from 'resend';
import { prisma } from '../database/client.js';
import { env } from '../config/env.js';

const resend = env.resendApiKey ? new Resend(env.resendApiKey) : null;

export const auth = betterAuth({
  database: prismaAdapter(prisma, {
    provider: 'postgresql',
  }),
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
    minPasswordLength: 8,
    maxPasswordLength: 128,
    sendVerificationEmail: async ({ user, token, url }) => {
      if (!resend) {
        console.log(`📧 Verification email (dev mode): ${url}`);
        return;
      }
      await resend.emails.send({
        from: env.emailFrom,
        to: user.email,
        subject: 'Verify your email',
        html: `
          <p>Welcome! Please verify your email by clicking the link below:</p>
          <a href="${url}">Verify Email</a>
          <p>This link expires in 15 minutes.</p>
        `,
      });
    },
  },
  socialProviders: {
    google: {
      clientId: env.google.clientId!,
      clientSecret: env.google.clientSecret!,
      redirectURI: env.google.redirectUri!,
    },
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update session every 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // 5 minutes
    },
  },
  account: {
    accountLinking: {
      enabled: true,
      trustedProviders: ['google'],
    },
  },
  advanced: {
    defaultCookieAttributes: {
      httpOnly: true,
      secure: env.nodeEnv === 'production',
      sameSite: env.nodeEnv === 'production' ? 'none' : 'lax',
      path: '/',
    },
  },
});
```

### 3.5 Express App

Create `src/app.ts`:

```typescript
import express from 'express';
import cors from 'cors';
import { auth } from './auth/auth.config.js';
import { toNodeHandler } from 'better-auth/node';
import { env } from './config/env.js';

const app = express();

// Middleware
app.use(express.json());
app.use(cors({
  origin: env.corsOrigins,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));

// Trust proxy (required for Vercel, Render, etc.)
app.set('trust proxy', 1);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Custom auth routes (BEFORE better-auth catch-all)
app.get('/api/auth/me', async (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) {
    return res.status(401).json({ error: 'Missing token' });
  }
  // Validate token and return user
  // Implementation depends on better-auth API
  res.json({ user: { id: 'demo', email: 'demo@example.com' } });
});

// Better-auth catch-all (MUST be last)
app.all('/api/auth/*', toNodeHandler(auth));

export default app;
```

### 3.6 Entry Point

Create `src/index.ts`:

```typescript
import app from './app.js';
import { env } from './config/env.js';

const PORT = env.port;

app.listen(PORT, () => {
  console.log(`🚀 Auth server running on http://localhost:${PORT}`);
  console.log(`📝 Environment: ${env.nodeEnv}`);
});
```

### 3.7 Run Auth Server

```bash
npm run dev
```

**Expected output**:
```
🚀 Auth server running on http://localhost:3000
📝 Environment: development
```

**Test health check**:
```bash
curl http://localhost:3000/health
# Expected: {"status":"healthy","timestamp":"2025-01-10T12:00:00.000Z"}
```

---

## Step 4: FastAPI Backend Setup

### 4.1 Create Backend Directory

```bash
cd /path/to/todo-app
mkdir -p backend
cd backend
```

### 4.2 Initialize Python Project with UV

```bash
uv init --package .
```

### 4.3 Install Dependencies

```bash
uv add fastapi uvicorn sqlalchemy asyncpg alembic pydantic-settings python-jose
uv add --dev pytest pytest-asyncio httpx
```

**Dependency explanations**:
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `sqlalchemy`: ORM for database
- `asyncpg`: Async PostgreSQL driver
- `alembic`: Database migrations
- `python-jose`: JWT validation (optional)

### 4.4 Configure Environment Variables

Create `backend/.env`:

```bash
# Database (same as auth server)
DATABASE_URL="postgresql+asyncpg://user:password@ep-xxx.neon.tech/neondb?ssl=require"

# Server
ENVIRONMENT=development

# Auth
AUTH_SERVER_URL="http://localhost:3000"

# CORS
CORS_ORIGINS="http://localhost:3000,http://localhost:5173"

# Frontend
FRONTEND_ORIGIN="http://localhost:3000"
```

**Note**: Database URL uses `postgresql+asyncpg://` for SQLAlchemy async.

### 4.5 Initialize Alembic

```bash
uv run alembic init src/database/migrations
```

Edit `alembic.ini`:

```ini
# Line 63: Change sqlalchemy.url to use env variable
sqlalchemy.url = postgresql+asyncpg://localhost/dbname  # Will be overridden by env.py
```

Edit `src/database/migrations/env.py`:

```python
import os
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Import your models here
from src.auth.models import Base

config = context.config

# Override sqlalchemy.url with environment variable
config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL', ''))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
```

### 4.6 Create SQLAlchemy Models

Create `backend/src/auth/models.py`:

```python
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Index, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    password: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    image: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sessions: Mapped[List["Session"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "user_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="sessions")

    __table_args__ = (
        Index("idx_sessions_user_id", "user_id"),
        Index("idx_sessions_token", "token"),
        Index("idx_sessions_expires_at", "expires_at"),
    )
```

**Note**: Tables already exist (created by Prisma in Step 2.9), so Alembic migration is for reference only.

### 4.7 Create Authentication Dependency

Create `backend/src/auth/dependencies.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional

from src.database.connection import get_db
from src.auth.models import User, Session as UserSession

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials

    stmt = (
        select(UserSession, User)
        .join(User, UserSession.user_id == User.id)
        .where(UserSession.token == token)
        .where(UserSession.expires_at > datetime.utcnow())
    )

    result = await db.execute(stmt)
    row = result.one_or_none()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    session, user = row

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required",
        )

    return user
```

### 4.8 Create Database Connection

Create `backend/src/database/connection.py`:

```python
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=3600,
)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with async_session_maker() as session:
        yield session
```

### 4.9 Create FastAPI App

Create `backend/src/main.py`:

```python
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.auth.dependencies import get_current_user
from src.auth.models import User

app = FastAPI(title="Todo API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-01-10T12:00:00Z"}

# Protected endpoint example
@app.get("/api/todos")
async def list_todos(current_user: User = Depends(get_current_user)):
    return {
        "todos": [],
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
        }
    }
```

### 4.10 Run FastAPI Server

```bash
uv run uvicorn src.main:app --reload --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Test health check**:
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","timestamp":"2025-01-10T12:00:00Z"}
```

---

## Step 5: Test End-to-End Authentication

### 5.1 Sign Up a User

```bash
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123",
    "name": "Test User"
  }'
```

**Expected response** (200 OK):
```json
{
  "user": {
    "id": "clh1234567890",
    "email": "test@example.com",
    "emailVerified": false,
    "name": "Test User"
  },
  "session": {
    "token": "eyJhbGc...",
    "expiresAt": "2025-01-17T12:00:00Z"
  }
}
```

### 5.2 Verify Email (Development Mode)

Check auth server console for verification link:
```
📧 Verification email (dev mode): http://localhost:3000/api/auth/verify-email?token=abc123...
```

Click the link or curl it:
```bash
curl http://localhost:3000/api/auth/verify-email?token=abc123...
```

### 5.3 Sign In

```bash
curl -X POST http://localhost:3000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

**Copy the `session.token` from response.**

### 5.4 Access Protected Endpoint

```bash
curl http://localhost:8000/api/todos \
  -H "Authorization: Bearer <paste-token-here>"
```

**Expected response** (200 OK):
```json
{
  "todos": [],
  "user": {
    "id": "clh1234567890",
    "email": "test@example.com",
    "name": "Test User"
  }
}
```

---

## Step 6: Production Deployment

### 6.1 Auth Server Deployment (Vercel)

#### Pre-Deployment Checklist

Verify these files exist:
- ✅ `auth-server/vercel.json` (catch-all routing)
- ✅ `auth-server/api/index.ts` (serverless entry point)
- ✅ `auth-server/package.json` has `vercel-build` script

#### Vercel Configuration Files

**File: `auth-server/vercel.json`** (already created in Phase 7):

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/api/index.js"
    }
  ]
}
```

**File: `auth-server/api/index.ts`** (already created in Phase 7):

```typescript
import app from '../src/app';

// Export the Express app for Vercel serverless functions
export default app;
```

**File: `auth-server/package.json`** (verify scripts exist):

```json
{
  "scripts": {
    "dev": "tsx --env-file=.env src/index.ts",
    "start": "node dist/index.js",
    "build": "tsc",
    "vercel-build": "prisma generate && tsc"
  }
}
```

#### Deploy to Vercel

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from auth-server directory**:
   ```bash
   cd auth-server
   vercel
   ```

4. **Follow prompts**:
   - Set up and deploy? → Yes
   - Scope? → Your account/team
   - Link to existing project? → No
   - Project name? → `todo-auth-server`
   - Directory? → `./` (current directory)
   - Override settings? → No

#### Configure Environment Variables in Vercel

Go to Vercel Dashboard → Project Settings → Environment Variables:

**Required Variables**:
```bash
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech/neondb?sslmode=require
JWT_SECRET=your-32-char-random-string
NODE_ENV=production
```

**Email Service (Resend)**:
```bash
RESEND_API_KEY=re_your_api_key
EMAIL_FROM=noreply@yourdomain.com
```

**CORS Configuration**:
```bash
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
FRONTEND_URL=https://yourdomain.com
```

**OAuth (Optional - Phase 9)**:
```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=https://auth.yourdomain.com/api/auth/callback/google
```

#### Redeploy After Environment Variables

```bash
vercel --prod
```

#### Verify Deployment

1. **Check health endpoint**:
   ```bash
   curl https://your-auth-server.vercel.app/health
   ```

2. **Expected response**:
   ```json
   {
     "status": "ok",
     "timestamp": "2025-01-10T12:00:00.000Z",
     "database": "connected"
   }
   ```

### 6.2 CORS Configuration for Production

#### Auth Server CORS

Update production `CORS_ORIGINS` to include all frontend domains:

```bash
# Vercel environment variable
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://app.yourdomain.com
```

The auth server reads this in `src/config/env.ts`:

```typescript
corsOrigins: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'],
```

#### FastAPI Backend CORS

Similarly, update backend's `CORS_ORIGINS`:

```bash
# Render/production environment
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### Cookie Configuration

For cross-domain authentication, cookies require:

```typescript
// In auth.config.ts - already configured
advanced: {
  defaultCookieAttributes: {
    httpOnly: true,
    secure: env.nodeEnv === 'production',  // HTTPS only in production
    sameSite: env.nodeEnv === 'production' ? 'none' : 'lax',  // Cross-site in prod
    path: '/',
  },
}
```

### 6.3 FastAPI Backend Deployment (Render)

#### Create Render Configuration

**File: `backend/render.yaml`**:

```yaml
services:
  - type: web
    name: todo-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn src.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.0
      - key: DATABASE_URL
        sync: false
      - key: AUTH_SERVER_URL
        value: https://your-auth-server.vercel.app
      - key: CORS_ORIGINS
        value: https://yourdomain.com
      - key: FRONTEND_ORIGIN
        value: https://yourdomain.com
```

#### Deploy to Render

1. **Connect GitHub repository** to Render
2. **Create new Web Service** from dashboard
3. **Select repository** and branch
4. **Configure service**:
   - Name: `todo-api`
   - Environment: Python 3.12
   - Build command: (use render.yaml)
   - Start command: (use render.yaml)
5. **Add environment variables** (if not in render.yaml)
6. **Deploy**

#### Verify Backend Deployment

```bash
curl https://your-api.onrender.com/health
```

### 6.4 Production Architecture

```
┌─────────────┐
│   Frontend  │ (Vercel/Netlify)
│   Next.js   │
└──────┬──────┘
       │
       ├──────────────┐
       │              │
       v              v
┌─────────────┐  ┌──────────────┐
│ Auth Server │  │ API Server   │
│  (Vercel)   │  │  (Render)    │
│ better-auth │  │   FastAPI    │
└──────┬──────┘  └──────┬───────┘
       │                │
       └────────┬───────┘
                v
       ┌────────────────┐
       │   PostgreSQL   │
       │     (Neon)     │
       └────────────────┘
```

**Flow**:
1. User signs up → Frontend → Auth Server → Neon
2. Auth server returns session token
3. Frontend stores token
4. API requests → Frontend → API Server (with token)
5. API Server validates token against Neon sessions table

---

## Troubleshooting

### Issue: `ERR_REQUIRE_ESM`

**Cause**: Missing `"type": "module"` in `package.json`

**Solution**:
```json
{
  "type": "module"
}
```

### Issue: 401 Unauthorized on Protected Endpoint

**Cause**: Token not sent or invalid

**Solution**:
1. Check `Authorization: Bearer <token>` header format
2. Verify token is from `/signin` or `/signup` response
3. Check token hasn't expired (7 days)

### Issue: CORS Error

**Cause**: Frontend origin not in `CORS_ORIGINS`

**Solution**:
Add frontend URL to both `.env` files:
```bash
CORS_ORIGINS="http://localhost:3000,https://yourdomain.com"
```

---

## Next Steps

1. ✅ **Authentication working**: Users can sign up, sign in, and access protected endpoints
2. ⏭️ **Add password reset**: Implement forgot password flow
3. ⏭️ **Add Google OAuth**: Enable Google sign-in
4. ⏭️ **Add session management**: List and revoke sessions
5. ⏭️ **Write integration tests**: Test auth flows end-to-end

---

**Quick Start Complete!** 🎉

You now have a working authentication system with:
- ✅ Email/password authentication
- ✅ Email verification
- ✅ Session management
- ✅ Protected FastAPI endpoints
- ✅ Shared PostgreSQL database

**Time to implement**: Use `/sp.tasks` to generate implementation tasks!
