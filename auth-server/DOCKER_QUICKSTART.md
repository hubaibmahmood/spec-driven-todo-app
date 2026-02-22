# Quick Start - Auth Server Docker

Get the Momentum auth server running in 2 minutes.

## 1. Create `.env` File

```bash
cd auth-server
cat > .env << 'EOF'
NODE_ENV=production
PORT=3002
DATABASE_URL=postgresql://postgres:postgres@db:5432/momentum
BETTER_AUTH_SECRET=change-this-to-32-character-secret-key-minimum
BETTER_AUTH_URL=http://localhost:3002
FRONTEND_URL=http://localhost:3000
RESEND_API_KEY=re_your_resend_api_key_here
EMAIL_FROM=noreply@momentum.intevia.cc
JWT_SECRET=change-this-jwt-secret-key
JWT_EXPIRES_IN=7d
EOF
```

**⚠️ Important**: Replace secrets with actual values:
- `BETTER_AUTH_SECRET`: Generate with `openssl rand -base64 32`
- `JWT_SECRET`: Generate with `openssl rand -base64 32`
- `RESEND_API_KEY`: Get from [resend.com](https://resend.com/api-keys)

## 2. Start Services

```bash
# Build and run
docker-compose up --build

# Or run in background
docker-compose up -d
```

## 3. Verify Running

```bash
# Check containers
docker-compose ps

# Test health endpoint
curl http://localhost:3002/health

# View logs
docker-compose logs -f auth-server
```

Expected output:
```
auth-server_1  | 🚀 Auth server running on port 3002
auth-server_1  |    Environment: production
auth-server_1  |    Health check: http://localhost:3002/health
auth-server_1  |    Auth endpoints: http://localhost:3002/api/auth
```

## 4. Test Authentication

**Sign up:**
```bash
curl -X POST http://localhost:3002/api/auth/sign-up \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "name": "Test User"
  }'
```

**Check database:**
```bash
docker exec -it momentum-postgres psql -U postgres -d momentum -c "SELECT email, name FROM \"user\";"
```

## Troubleshooting

**Container exits immediately:**
```bash
docker-compose logs auth-server
```
→ Check for missing environment variables

**Database connection error:**
```bash
docker-compose restart db
docker-compose restart auth-server
```

**Port already in use:**
```bash
# Change PORT in .env
PORT=4001
docker-compose up
```

## Next Steps

- **Frontend Integration**: Configure your Next.js frontend to connect to auth-server
  - Frontend runs on: `http://localhost:3000`
  - Auth-server runs on: `http://localhost:3002`
  - Set `NEXT_PUBLIC_AUTH_URL=http://localhost:3002/api/auth` in frontend `.env.local`
- Read [DOCKER_README.md](./DOCKER_README.md) for full documentation
- Set up production environment variables
- Enable SSL/TLS in production
