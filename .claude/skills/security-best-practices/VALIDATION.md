# Input Validation Patterns

## Pydantic Validators

### Field Validators
```python
from pydantic import BaseModel, Field, validator

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    age: int = Field(..., ge=0, le=150)
    email: str

    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v.lower()

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v.lower()
```

### Multiple Field Validation
```python
from pydantic import root_validator

class PasswordReset(BaseModel):
    password: str
    password_confirm: str

    @root_validator
    def verify_password_match(cls, values):
        pw1 = values.get('password')
        pw2 = values.get('password_confirm')
        if pw1 != pw2:
            raise ValueError('Passwords do not match')
        return values
```

### Custom Types
```python
from pydantic import constr, conint

# Constrained string
Username = constr(min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_]+$')

# Constrained int
Age = conint(ge=0, le=150)

class User(BaseModel):
    username: Username
    age: Age
```

## Request Validation

### Path Parameters
```python
from fastapi import Path

@router.get("/users/{user_id}")
async def get_user(
    user_id: int = Path(..., gt=0, description="User ID must be positive")
):
    ...
```

### Query Parameters
```python
from fastapi import Query

@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str | None = Query(None, max_length=100)
):
    ...
```

### Body Validation
```python
from fastapi import Body

@router.post("/users")
async def create_user(
    user: UserCreate = Body(..., example={
        "username": "johndoe",
        "email": "john@example.com"
    })
):
    ...
```

## Sanitization

### SQL Injection Prevention
```python
# ✅ Use ORM (automatically parameterized)
stmt = select(User).where(User.email == email)

# ❌ Never string interpolation
query = f"SELECT * FROM users WHERE email = '{email}'"
```

### XSS Prevention
```python
import html

def sanitize_html(text: str) -> str:
    """Escape HTML to prevent XSS."""
    return html.escape(text)

# Or use bleach
import bleach
def sanitize_html(text: str) -> str:
    return bleach.clean(text, tags=[], strip=True)
```

### File Upload Validation
```python
from fastapi import UploadFile, HTTPException

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

async def validate_upload(file: UploadFile):
    # Check extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Invalid file type")

    # Check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")

    # Reset file pointer
    await file.seek(0)
    return file
```

## Error Handling

### Custom Validation Errors
```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "details": exc.errors()
        }
    )
```
