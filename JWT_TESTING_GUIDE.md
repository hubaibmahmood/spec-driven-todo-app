# JWT Authentication Testing Guide

This guide shows you how to test the JWT authentication implementation.

## 🧪 Testing Options

### Option 1: Automated Python Tests (Unit Tests)

Test JWT generation and validation directly:

```bash
cd backend
uv run python test_jwt_manual.py
```

**What it tests:**
- ✅ JWT access token generation
- ✅ Token payload structure (sub, iat, exp, type)
- ✅ Token validation and user_id extraction
- ✅ Invalid token rejection
- ✅ Refresh token generation and hashing
- ✅ Token type validation

**Expected output:**
```
============================================================
  JWT AUTHENTICATION TEST SUITE
============================================================

============================================================
  TEST 1: JWT Token Generation
============================================================

✅ Generated JWT token for user: test-user-123

Token (first 50 chars): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOi...
Token length: 234 characters

📋 Token Payload:
   - Subject (user_id): test-user-123
   - Type: access
   - Issued At: 2026-01-03 12:34:56+00:00
   - Expires At: 2026-01-03 13:04:56+00:00
   - Time until expiration: 30.0 minutes

============================================================
  TEST SUMMARY
============================================================
✅ PASS   Token Generation
✅ PASS   Token Validation
✅ PASS   Invalid Token Handling
✅ PASS   Refresh Token Generation
✅ PASS   Token Type Validation

============================================================
  🎉 ALL TESTS PASSED!
============================================================
```

---

### Option 2: API Integration Tests (Full Flow)

Test the complete authentication flow with HTTP requests:

**Prerequisites:**
1. Backend running: `cd backend && uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload`
2. Auth-server running: `cd auth-server && npm run dev`
3. jq installed: `brew install jq` (if not already installed)

**Run the tests:**
```bash
./test_jwt_api.sh
```

**What it tests:**
- ✅ POST /api/auth/jwt/sign-up (create user + get JWT)
- ✅ POST /api/auth/jwt/sign-in (login + get JWT)
- ✅ JWT token in Authorization header
- ✅ Backend validates JWT and extracts user_id
- ✅ Refresh token cookie is set (httpOnly)
- ✅ Invalid tokens are rejected with 401
- ✅ Complete authenticated API flow

**Expected output:**
```
============================================
  TEST 1: Sign Up (JWT)
============================================

✅ Sign up successful
ℹ️  User ID: clm8x9y8z0000...
ℹ️  Email: test-jwt-1735912345@example.com
ℹ️  Access Token (first 50 chars): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOi...
ℹ️  JWT Payload:
{
  "sub": "clm8x9y8z0000...",
  "iat": 1735912345,
  "exp": 1735914145,
  "type": "access"
}

============================================
  TEST 2: Authenticated API Request (with JWT)
============================================

✅ Task created successfully with JWT
ℹ️  Task ID: 123
ℹ️  Task Title: Test JWT Authentication
ℹ️  This confirms JWT validation works in the backend!

...

============================================
  TEST SUMMARY
============================================

✅ All tests passed! 🎉

ℹ️  What was verified:
  ✅ JWT signup endpoint works
  ✅ JWT signin endpoint works
  ✅ Access tokens are generated correctly
  ✅ Refresh tokens are set in httpOnly cookies
  ✅ Backend validates JWT signatures
  ✅ Backend extracts user_id from JWT correctly
  ✅ Invalid tokens are rejected with 401
  ✅ Authenticated API requests work with JWT
```

---

### Option 3: Manual Testing with curl

#### 1. Sign up and get JWT token:

```bash
curl -X POST http://localhost:8080/api/auth/jwt/sign-up \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "name": "Test User"
  }' \
  -c cookies.txt | jq
```

**Expected response:**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "clm8x9y8z0000...",
    "email": "test@example.com",
    "name": "Test User",
    "image": null,
    "emailVerified": false
  },
  "message": "Registration successful. Please check your email to verify your account."
}
```

#### 2. Extract the access token:

```bash
ACCESS_TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/jwt/sign-up \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test2@example.com",
    "password": "SecurePassword123!",
    "name": "Test User 2"
  }' | jq -r '.accessToken')

echo "Access Token: $ACCESS_TOKEN"
```

#### 3. Make an authenticated request:

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "title": "My JWT Task",
    "description": "Created with JWT authentication",
    "priority": "High"
  }' | jq
```

**Expected response:**
```json
{
  "id": 1,
  "user_id": "clm8x9y8z0000...",
  "title": "My JWT Task",
  "description": "Created with JWT authentication",
  "completed": false,
  "priority": "High",
  "due_date": null,
  "created_at": "2026-01-03T12:34:56.789Z",
  "updated_at": "2026-01-03T12:34:56.789Z"
}
```

#### 4. Decode JWT to see user_id:

```bash
# Extract the payload part (between the two dots)
PAYLOAD=$(echo $ACCESS_TOKEN | cut -d. -f2)

# Decode from base64 (add padding if needed)
echo $PAYLOAD | base64 -d 2>/dev/null | jq
```

**Expected output:**
```json
{
  "sub": "clm8x9y8z0000...",  ← This is the user_id
  "iat": 1735912345,
  "exp": 1735914145,
  "type": "access"
}
```

#### 5. Test with invalid token:

```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer invalid-token-here" \
  -v
```

**Expected response:**
```
< HTTP/1.1 401 Unauthorized
{
  "detail": {
    "error_code": "invalid_token",
    "message": "Invalid access token: ..."
  }
}
```

---

### Option 4: Decode JWT at jwt.io

1. Copy your access token
2. Go to https://jwt.io
3. Paste the token in the "Encoded" field
4. See the decoded payload with user_id in the `sub` field

**What to verify:**
- ✅ Algorithm: HS256
- ✅ Payload contains: `sub` (user_id), `iat`, `exp`, `type: "access"`
- ✅ Expiration is ~30 minutes from issued time

---

## 🔍 What to Look For

### ✅ Successful JWT Generation
- Token is a 3-part string separated by dots (header.payload.signature)
- Length is ~200-300 characters
- Payload contains user_id in `sub` field
- Expiration is 30 minutes from now
- Type is "access"

### ✅ Successful JWT Validation
- Backend accepts the token without error
- API requests return 200 OK
- Backend correctly extracts user_id from token
- Tasks are associated with the correct user

### ✅ Proper Security
- Refresh token set in httpOnly cookie (not visible in response body)
- Invalid tokens rejected with 401
- Expired tokens rejected with error_code: "token_expired"
- Wrong token type rejected

---

## 🐛 Troubleshooting

### Backend import error
```
ImportError: cannot import name 'get_db' from 'src.database'
```
**Fix:** Already fixed in commit c128c11 - update your code!

### "jq: command not found"
```bash
brew install jq
```

### Backend not running
```bash
cd backend
uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Auth-server not running
```bash
cd auth-server
npm run dev
```

### Token validation fails
- Check `JWT_SECRET` matches in both backend and auth-server
- Verify backend has `JWT_AUTH_ENABLED=true` in .env (if you want to test JWT)
- Check token hasn't expired (30-minute lifetime)

---

## 📊 Performance Verification

To verify JWT is faster than session validation:

```bash
# With JWT (should be <1ms)
time curl -s -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null

# The authentication part should be nearly instant (signature verification only)
```

---

## 🎯 Next Steps

After verifying JWT works:
1. Enable JWT in production: `JWT_AUTH_ENABLED=true`
2. Implement Phase 4: Auto token refresh
3. Implement Phase 5: Logout endpoint
4. Add monitoring (Phase 6)
5. Write comprehensive tests (Phase 7)
