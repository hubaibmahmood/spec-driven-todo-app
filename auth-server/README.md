# Auth Server - Authentication Microservice

A Node.js/TypeScript authentication service built with better-auth, providing secure user authentication, email verification, password recovery, and session management for the todo application.

## Features

### 🔐 Authentication
- ✅ **Email/Password**: Secure registration and login with bcrypt hashing
- ✅ **Email Verification**: Mandatory verification using Resend email service
- ✅ **Password Recovery**: Secure password reset flow via email
- ✅ **Session Management**: Multiple concurrent sessions with device tracking

### 🛡️ Security
- ✅ **Bcrypt Hashing**: Secure password storage with salt rounds
- ✅ **JWT Tokens**: 15-minute access tokens, 7-day refresh tokens
- ✅ **Database-Driven**: Session validation against PostgreSQL
- ✅ **CORS Support**: Configured for cross-origin requests
- ✅ **Rate Limiting**: Protection against brute-force attacks

### 📧 Email Integration
- ✅ **Resend Service**: Production-ready email delivery
- ✅ **Email Templates**: Customizable verification and reset emails
- ✅ **Link Expiration**: Time-limited verification and reset links
- ✅ **Email Validation**: Format and deliverability checks

## Technology Stack

- **Framework**: Express.js
- **Language**: TypeScript 5.x
- **Runtime**: Node.js 20+
- **Auth Library**: better-auth 1.4+
- **Database**: PostgreSQL (Neon Serverless) via Prisma
- **Email Service**: Resend
- **Password Hashing**: bcrypt
- **Deployment**: Vercel serverless functions + local development

## Architecture

```
Client (Frontend/Mobile)
        ↓
better-auth Client SDK
        ↓
Auth Server (Port 3002)
        ↓
better-auth Library
        ↓
PostgreSQL (via Prisma)
        ↓
Email Service (Resend)
```

### Directory Structure

```
auth-server/
├── src/
│   ├── auth/                  # better-auth configuration
│   │   ├── auth.config.ts     # Auth instance setup
│   │   └── routes.ts          # Auth routes
│   ├── config/                # Server configuration
│   │   └── env.ts             # Environment variables
│   ├── database/              # Database configuration
│   │   └── client.ts          # Prisma client
│   ├── middleware/            # Express middleware
│   │   └── errorHandler.ts   # Error handling
│   ├── utils/                 # Utility functions
│   │   └── resend.ts          # Email service setup
│   ├── app.ts                 # Express app configuration
│   └── index.ts               # Server entry point
├── api/                       # Vercel serverless functions
│   └── index.ts               # Serverless entry point
├── prisma/
│   ├── schema.prisma          # Database schema
│   └── migrations/            # Database migrations
├── dist/                      # Compiled TypeScript output
├── tests/                     # Test suite
├── package.json               # Dependencies
├── tsconfig.json              # TypeScript config
├── vercel.json                # Vercel deployment config
└── README.md                  # This file
```

## Prerequisites

- Node.js 20 or higher
- PostgreSQL database (Neon recommended)
- Resend API key (for email verification)

## Quick Start

### 1. Installation

```bash
# Navigate to auth-server directory
cd auth-server

# Install dependencies
npm install

# Generate Prisma client
npx prisma generate
```

### 2. Environment Configuration

Create a `.env` file in the `auth-server/` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require

# better-auth Configuration
BETTER_AUTH_SECRET=your_secure_random_string_here

#CORS
CORS_ORIGINS="http://localhost:3000,http://localhost:8000"

# Email Service (Resend)
RESEND_API_KEY=re_your_resend_api_key_here
EMAIL_FROM="email_to_send_emails"

FRONTEND_URL="http://localhost:3000"

# Application Settings
NODE_ENV=development
PORT=3002
```

**Important Notes**:
- Generate `BETTER_AUTH_SECRET` with: `openssl rand -base64 32`
- Get Resend API key from [resend.com](https://resend.com)

### 3. Database Setup

Push the schema to your PostgreSQL database:

```bash
# Push schema to database
npx prisma db push

# Open Prisma Studio to view data (optional)
npx prisma studio
```

This creates the following tables:
- `user` - User accounts with email and password
- `session` - Active user sessions with tokens
- `verification` - Email verification tokens

### 4. Start the Service

```bash
# Development mode (with auto-reload)
npm run dev

# Production mode
npm start

# Build for production
npm run build
```

The auth server will start at `http://localhost:3002`

## API Endpoints

All endpoints are managed by better-auth. The server exposes a catch-all route at `/api/auth/*`.

### Authentication Endpoints

#### Register

```bash
POST /api/auth/sign-up
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "John Doe"
}
```

**Response** (200 OK):
```json
{
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "name": "John Doe",
    "emailVerified": false
  },
  "session": {
    "token": "session-token-here",
    "expiresAt": "2025-12-27T10:30:00Z"
  }
}
```

**Note**: An email verification link is sent to the user's email address.

#### Login

```bash
POST /api/auth/sign-in
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response** (200 OK):
```json
{
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "name": "John Doe",
    "emailVerified": true
  },
  "session": {
    "token": "session-token-here",
    "expiresAt": "2025-12-27T10:30:00Z"
  }
}
```

#### Logout

```bash
POST /api/auth/sign-out
```

**Headers**:
```
Authorization: Bearer <session_token>
```

**Response** (200 OK):
```json
{
  "success": true
}
```

#### Email Verification

```bash
GET /api/auth/verify-email?token=<verification_token>
```

Verifies user's email address. Redirects to frontend success page.

#### Password Reset Request

```bash
POST /api/auth/forgot-password
```

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

Sends password reset email with secure token.

#### Password Reset

```bash
POST /api/auth/reset-password
```

**Request Body**:
```json
{
  "token": "reset-token-here",
  "password": "NewSecurePassword123!"
}
```

### Session Management

#### Get Session

```bash
GET /api/auth/session
```

**Headers**:
```
Authorization: Bearer <session_token>
```

**Response** (200 OK):
```json
{
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "name": "John Doe",
    "emailVerified": true
  },
  "session": {
    "token": "session-token-here",
    "expiresAt": "2025-12-27T10:30:00Z"
  }
}
```

## Database Schema

### User Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | String | Primary key (cuid) |
| `email` | String | User email (unique) |
| `emailVerified` | Boolean | Email verification status |
| `name` | String | User's display name |
| `image` | String | Profile image URL (optional) |
| `createdAt` | DateTime | Account creation timestamp |
| `updatedAt` | DateTime | Last update timestamp |

### Session Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | String | Primary key (cuid) |
| `token` | String | Session token (unique) |
| `userId` | String | Foreign key to user |
| `expiresAt` | DateTime | Session expiration timestamp |
| `ipAddress` | String | IP address of session |
| `userAgent` | String | Device/browser info |
| `createdAt` | DateTime | Session creation timestamp |

### Verification Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | String | Primary key (cuid) |
| `identifier` | String | Email address |
| `value` | String | Verification token |
| `expiresAt` | DateTime | Token expiration |
| `createdAt` | DateTime | Creation timestamp |

## Email Configuration

### Resend Setup

1. Sign up at [resend.com](https://resend.com)
2. Create an API key
3. Add to `.env` as `RESEND_API_KEY`
4. Verify your sending domain (for production)

### Email Templates

Verification email:
- Subject: "Verify your email address"
- Link format: `{BETTER_AUTH_URL}/api/auth/verify-email?token={token}`
- Expiration: 24 hours

Password reset email:
- Subject: "Reset your password"
- Link format: `{FRONTEND_URL}/reset-password?token={token}`
- Expiration: 1 hour

## Error Handling

The service returns standard HTTP error codes:

| Code | Description | Example |
|------|-------------|---------|
| 200 | Success | Authentication successful |
| 400 | Bad Request | Invalid email format |
| 401 | Unauthorized | Invalid credentials |
| 403 | Forbidden | Email not verified |
| 404 | Not Found | User not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Database error |

**Example Error Response**:
```json
{
  "error": "Invalid credentials",
  "code": "INVALID_CREDENTIALS"
}
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Yes | - | Secret for signing tokens (32+ characters) |
| `CORS_ORIGINS` | Yes | `"http://localhost:3000,http://localhost:8000"` | Comma-separated list of allowed origins |
| `RESEND_API_KEY` | Yes | - | Resend API key for emails |
| `EMAIL_FROM` | Yes | - | Email address to send emails from |
| `FRONTEND_URL` | Yes | `"http://localhost:3000"` | Frontend application URL |
| `NODE_ENV` | No | `development` | Environment (development/production) |
| `PORT` | No | `3002` | Server port |

### CORS Configuration

CORS is configured via the `CORS_ORIGINS` environment variable. Default allowed origins:
- `http://localhost:3000` (Frontend)
- `http://localhost:8000` (Backend API)

Update `CORS_ORIGINS` in `.env` for production with your actual domains (comma-separated).

## Testing

### Run Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### Type Checking

```bash
# Run TypeScript compiler
npx tsc --noEmit
```

### Linting

```bash
# Run ESLint
npm run lint

# Fix linting issues
npm run lint:fix
```

## Deployment

### Vercel Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy to Vercel
vercel

# Deploy to production
vercel --prod
```

**Environment Variables** (Vercel Dashboard):
- Add all variables from `.env`
- Set `BETTER_AUTH_URL` to your Vercel domain
- Update `DATABASE_URL` with production credentials

### Production Checklist

- [ ] Set `NODE_ENV=production`
- [ ] Use strong `BETTER_AUTH_SECRET` (32+ characters)
- [ ] Configure production `DATABASE_URL`
- [ ] Add production domain to CORS origins
- [ ] Verify sending domain in Resend
- [ ] Enable HTTPS/TLS
- [ ] Set up monitoring (Sentry, LogRocket, etc.)
- [ ] Configure database backups
- [ ] Set up rate limiting

## Troubleshooting

### Database Connection Issues

**Error**: `Prisma connection errors`

**Solution**:
- Verify `DATABASE_URL` format and credentials
- Check database is accessible from your network
- Ensure SSL mode is correct (`sslmode=require` for Neon)
- Run `npx prisma db push` to sync schema

### Email Delivery Issues

**Error**: `Resend API errors`

**Solution**:
- Verify `RESEND_API_KEY` is correct
- Check Resend dashboard for quota limits
- Verify sending domain (production)
- Check spam folder for test emails

### Session Issues

**Error**: `Session not found or expired`

**Solution**:
- Check session token is valid and not expired
- Verify `expiresAt` column in database
- Ensure correct `Authorization: Bearer <token>` format
- Clear old sessions from database

## Contributing

This service is part of the todo-app project following Spec-Driven Development (SDD) methodology.

**Development workflow**:
1. Review specifications in `specs/004-auth-server/`
2. Follow task breakdown in `tasks.md`
3. Write tests first (TDD approach)
4. Implement changes with proper error handling
5. Update documentation
6. Run test suite: `npm test`
7. Create PR for review

## License

[Your License Here]

## Support

For issues or questions:
- Review [better-auth documentation](https://www.better-auth.com/)
- Check [Resend documentation](https://resend.com/docs)
- Review deployment guide in `DEPLOYMENT.md`

## Acknowledgments

- Authentication: [better-auth](https://www.better-auth.com/)
- Email Service: [Resend](https://resend.com)
- Database ORM: [Prisma](https://www.prisma.io/)
- Database: [Neon Serverless PostgreSQL](https://neon.tech/)
- Deployment: [Vercel](https://vercel.com/)
