# FastAPI Complete Working Examples

## Complete CRUD Example with Clean Architecture

### 1. Database Model

```python
# app/models/post.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
```

### 2. Pydantic Schemas

```python
# app/schemas/post.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    published: bool = False

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    published: Optional[bool] = None

class PostResponse(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "My First Post",
                "content": "This is the content of my first post",
                "published": True,
                "author_id": 1,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-02T00:00:00"
            }
        }

class PostWithAuthor(PostResponse):
    author: dict  # Or UserResponse if you want full type safety

    class Config:
        from_attributes = True
```

### 3. Repository Layer

```python
# app/repositories/post_repository.py
from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate

class PostRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        published_only: bool = False
    ) -> List[Post]:
        """Get all posts with optional filtering."""
        query = select(Post).options(selectinload(Post.author))

        if published_only:
            query = query.where(Post.published == True)

        query = query.offset(skip).limit(limit).order_by(Post.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, post_id: int) -> Optional[Post]:
        """Get post by ID."""
        query = select(Post).options(selectinload(Post.author)).where(Post.id == post_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_author(self, author_id: int) -> List[Post]:
        """Get all posts by a specific author."""
        query = select(Post).where(Post.author_id == author_id).order_by(Post.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, post_data: PostCreate, author_id: int) -> Post:
        """Create a new post."""
        post = Post(**post_data.model_dump(), author_id=author_id)
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def update(self, post_id: int, post_data: PostUpdate) -> Optional[Post]:
        """Update an existing post."""
        # Only update fields that are provided
        update_data = post_data.model_dump(exclude_unset=True)

        if not update_data:
            return await self.get_by_id(post_id)

        stmt = (
            update(Post)
            .where(Post.id == post_id)
            .values(**update_data)
            .returning(Post)
        )

        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def delete(self, post_id: int) -> bool:
        """Delete a post."""
        stmt = delete(Post).where(Post.id == post_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def count(self, published_only: bool = False) -> int:
        """Count total posts."""
        from sqlalchemy import func, select

        query = select(func.count(Post.id))

        if published_only:
            query = query.where(Post.published == True)

        result = await self.db.execute(query)
        return result.scalar_one()
```

### 4. Service Layer

```python
# app/services/post_service.py
from typing import List
from fastapi import HTTPException, status
from app.repositories.post_repository import PostRepository
from app.schemas.post import PostCreate, PostUpdate, PostResponse, PostWithAuthor

class PostService:
    def __init__(self, repository: PostRepository):
        self.repository = repository

    async def list_posts(
        self,
        skip: int = 0,
        limit: int = 100,
        published_only: bool = False
    ) -> List[PostWithAuthor]:
        """List all posts."""
        posts = await self.repository.get_all(skip, limit, published_only)
        return [PostWithAuthor.model_validate(post) for post in posts]

    async def get_post(self, post_id: int) -> PostWithAuthor:
        """Get post by ID."""
        post = await self.repository.get_by_id(post_id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id {post_id} not found"
            )

        return PostWithAuthor.model_validate(post)

    async def get_user_posts(self, author_id: int) -> List[PostResponse]:
        """Get all posts by a specific author."""
        posts = await self.repository.get_by_author(author_id)
        return [PostResponse.model_validate(post) for post in posts]

    async def create_post(
        self,
        post_data: PostCreate,
        author_id: int
    ) -> PostResponse:
        """Create a new post."""
        post = await self.repository.create(post_data, author_id)
        return PostResponse.model_validate(post)

    async def update_post(
        self,
        post_id: int,
        post_data: PostUpdate,
        current_user_id: int
    ) -> PostResponse:
        """Update a post."""
        # Check if post exists
        existing_post = await self.repository.get_by_id(post_id)

        if not existing_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id {post_id} not found"
            )

        # Check authorization
        if existing_post.author_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this post"
            )

        updated_post = await self.repository.update(post_id, post_data)

        if not updated_post:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update post"
            )

        return PostResponse.model_validate(updated_post)

    async def delete_post(self, post_id: int, current_user_id: int) -> None:
        """Delete a post."""
        # Check if post exists
        existing_post = await self.repository.get_by_id(post_id)

        if not existing_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id {post_id} not found"
            )

        # Check authorization
        if existing_post.author_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this post"
            )

        success = await self.repository.delete(post_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete post"
            )

    async def publish_post(self, post_id: int, current_user_id: int) -> PostResponse:
        """Publish a post."""
        post_data = PostUpdate(published=True)
        return await self.update_post(post_id, post_data, current_user_id)
```

### 5. Dependencies

```python
# app/api/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.post_repository import PostRepository
from app.services.post_service import PostService

def get_post_repository(db: AsyncSession = Depends(get_db)) -> PostRepository:
    return PostRepository(db)

def get_post_service(
    repository: PostRepository = Depends(get_post_repository)
) -> PostService:
    return PostService(repository)
```

### 6. Router/Endpoints

```python
# app/api/v1/endpoints/posts.py
from fastapi import APIRouter, Depends, status, Query
from typing import List
from app.api.dependencies import get_post_service
from app.schemas.post import PostCreate, PostUpdate, PostResponse, PostWithAuthor
from app.services.post_service import PostService
from app.core.security import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=List[PostWithAuthor])
async def list_posts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    published_only: bool = Query(False, description="Show only published posts"),
    service: PostService = Depends(get_post_service)
):
    """
    List all posts with pagination.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 100)
    - **published_only**: Filter to show only published posts (default: false)
    """
    return await service.list_posts(skip, limit, published_only)

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: dict = Depends(get_current_user),
    service: PostService = Depends(get_post_service)
):
    """
    Create a new post.

    - **title**: Post title (required, max 200 characters)
    - **content**: Post content (required)
    - **published**: Publication status (default: false)
    """
    return await service.create_post(post_data, current_user["id"])

@router.get("/{post_id}", response_model=PostWithAuthor)
async def get_post(
    post_id: int,
    service: PostService = Depends(get_post_service)
):
    """
    Get a specific post by ID.

    Returns the post with author information.
    """
    return await service.get_post(post_id)

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: dict = Depends(get_current_user),
    service: PostService = Depends(get_post_service)
):
    """
    Update a post.

    Only the post author can update their posts.
    Only provided fields will be updated.
    """
    return await service.update_post(post_id, post_data, current_user["id"])

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: dict = Depends(get_current_user),
    service: PostService = Depends(get_post_service)
):
    """
    Delete a post.

    Only the post author can delete their posts.
    """
    await service.delete_post(post_id, current_user["id"])
    return None

@router.patch("/{post_id}/publish", response_model=PostResponse)
async def publish_post(
    post_id: int,
    current_user: dict = Depends(get_current_user),
    service: PostService = Depends(get_post_service)
):
    """
    Publish a post.

    Sets the post's published status to true.
    Only the post author can publish their posts.
    """
    return await service.publish_post(post_id, current_user["id"])

@router.get("/users/{user_id}", response_model=List[PostResponse])
async def get_user_posts(
    user_id: int,
    service: PostService = Depends(get_post_service)
):
    """
    Get all posts by a specific user.

    Returns all posts authored by the specified user, ordered by creation date.
    """
    return await service.get_user_posts(user_id)
```

### 7. Main Application

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-ready FastAPI backend",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import posts, users, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
```

### 8. Database Session

```python
# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    future=True,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW
)

# Create session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncSession:
    """Dependency for getting async database session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 9. Configuration

```python
# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "FastAPI Backend"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 10. Testing

```python
# tests/test_posts.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_post(async_client: AsyncClient, auth_headers):
    """Test creating a post."""
    post_data = {
        "title": "Test Post",
        "content": "This is a test post",
        "published": False
    }

    response = await async_client.post(
        "/api/v1/posts/",
        json=post_data,
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == post_data["title"]
    assert data["content"] == post_data["content"]
    assert "id" in data

@pytest.mark.asyncio
async def test_get_post(async_client: AsyncClient, sample_post):
    """Test getting a post by ID."""
    response = await async_client.get(f"/api/v1/posts/{sample_post.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_post.id
    assert data["title"] == sample_post.title

@pytest.mark.asyncio
async def test_update_post(async_client: AsyncClient, sample_post, auth_headers):
    """Test updating a post."""
    update_data = {"title": "Updated Title"}

    response = await async_client.put(
        f"/api/v1/posts/{sample_post.id}",
        json=update_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]

@pytest.mark.asyncio
async def test_delete_post(async_client: AsyncClient, sample_post, auth_headers):
    """Test deleting a post."""
    response = await async_client.delete(
        f"/api/v1/posts/{sample_post.id}",
        headers=auth_headers
    )

    assert response.status_code == 204

    # Verify post is deleted
    get_response = await async_client.get(f"/api/v1/posts/{sample_post.id}")
    assert get_response.status_code == 404
```

## Summary

This complete example demonstrates:

- ✅ Clean architecture (routers → services → repositories → models)
- ✅ Proper async/await usage
- ✅ Type hints everywhere
- ✅ Pydantic validation
- ✅ Dependency injection
- ✅ Error handling
- ✅ Authorization checks
- ✅ OpenAPI documentation
- ✅ Comprehensive testing

Use this as a template for building your own FastAPI endpoints!
