# JWT Authentication Deep Dive

## Token Structure

```
header.payload.signature

# Header (Base64)
{
  "alg": "HS256",
  "typ": "JWT"
}

# Payload (Base64)
{
  "sub": "user123",
  "exp": 1735689600,
  "type": "access",
  "roles": ["user"]
}

# Signature
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret_key
)
```

## Complete Auth Flow

```python
# 1. User Registration
@router.post("/register")
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create user
    user = await repository.create({
        "email": user_data.email,
        "username": user_data.username,
        "hashed_password": hashed_password
    })

    return user

# 2. User Login
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Verify user
    user = await authenticate_user(form_data.username, form_data.password)

    # Create tokens
    access_token = create_access_token(data={"sub": user.id, "roles": user.roles})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# 3. Protected Endpoint
@router.get("/protected")
async def protected(current_user = Depends(get_current_user)):
    return {"user": current_user}

# 4. Token Refresh
@router.post("/refresh")
async def refresh(refresh_token: str):
    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid token type")

    new_access_token = create_access_token(data={"sub": payload["sub"]})

    return {"access_token": new_access_token}
```

## Token Blacklisting (Logout)

```python
# Using Redis
async def logout(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    exp = payload.get("exp")

    # Add to blacklist until expiration
    ttl = exp - int(datetime.utcnow().timestamp())
    await redis_client.setex(f"blacklist:{token}", ttl, "1")

    return {"message": "Logged out successfully"}

# Check blacklist in get_current_user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Check if token is blacklisted
    if await redis_client.exists(f"blacklist:{token}"):
        raise HTTPException(401, "Token has been revoked")

    payload = decode_token(token)
    # ... rest of logic
```

## Role-Based Access Control (RBAC)

```python
from enum import Enum

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

def require_role(required_role: Role):
    """Dependency to check user role."""
    async def role_checker(current_user = Depends(get_current_user)):
        if required_role not in current_user.roles:
            raise HTTPException(403, "Insufficient permissions")
        return current_user
    return role_checker

# Usage
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user = Depends(require_role(Role.ADMIN))
):
    ...
```

## Best Practices

1. **Short expiration**: Access tokens 15-30 minutes
2. **Refresh tokens**: 7-30 days with rotation
3. **Strong secret key**: Use cryptographically secure random key
4. **Token validation**: Always check exp, iat, nbf claims
5. **HTTPS only**: Never transmit tokens over HTTP
6. **httpOnly cookies**: For web apps, store tokens in httpOnly cookies
7. **Logout**: Implement token blacklisting for logout
