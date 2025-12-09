"""
FastAPI Endpoint Template

This is a complete template for creating a new resource endpoint with CRUD operations.
Replace {Resource}, {resource}, and {resources} with your actual resource name.

Example: If creating a "Product" endpoint:
  - {Resource} -> Product
  - {resource} -> product
  - {resources} -> products
"""

# ============================================================================
# 1. DATABASE MODEL (app/models/{resource}.py)
# ============================================================================

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class {Resource}(Base):
    __tablename__ = "{resources}"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============================================================================
# 2. PYDANTIC SCHEMAS (app/schemas/{resource}.py)
# ============================================================================

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class {Resource}Base(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = True

class {Resource}Create({Resource}Base):
    pass

class {Resource}Update(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class {Resource}Response({Resource}Base):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# 3. REPOSITORY LAYER (app/repositories/{resource}_repository.py)
# ============================================================================

from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.{resource} import {Resource}
from app.schemas.{resource} import {Resource}Create, {Resource}Update

class {Resource}Repository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[{Resource}]:
        """Get all {resources}."""
        query = select({Resource}).offset(skip).limit(limit).order_by({Resource}.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, {resource}_id: int) -> Optional[{Resource}]:
        """Get {resource} by ID."""
        query = select({Resource}).where({Resource}.id == {resource}_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, {resource}_data: {Resource}Create) -> {Resource}:
        """Create a new {resource}."""
        {resource} = {Resource}(**{resource}_data.model_dump())
        self.db.add({resource})
        await self.db.commit()
        await self.db.refresh({resource})
        return {resource}

    async def update(
        self,
        {resource}_id: int,
        {resource}_data: {Resource}Update
    ) -> Optional[{Resource}]:
        """Update an existing {resource}."""
        update_data = {resource}_data.model_dump(exclude_unset=True)

        if not update_data:
            return await self.get_by_id({resource}_id)

        stmt = (
            update({Resource})
            .where({Resource}.id == {resource}_id)
            .values(**update_data)
            .returning({Resource})
        )

        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def delete(self, {resource}_id: int) -> bool:
        """Delete a {resource}."""
        stmt = delete({Resource}).where({Resource}.id == {resource}_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0


# ============================================================================
# 4. SERVICE LAYER (app/services/{resource}_service.py)
# ============================================================================

from typing import List
from fastapi import HTTPException, status
from app.repositories.{resource}_repository import {Resource}Repository
from app.schemas.{resource} import {Resource}Create, {Resource}Update, {Resource}Response

class {Resource}Service:
    def __init__(self, repository: {Resource}Repository):
        self.repository = repository

    async def list_{resources}(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[{Resource}Response]:
        """List all {resources}."""
        {resources} = await self.repository.get_all(skip, limit)
        return [{Resource}Response.model_validate({resource}) for {resource} in {resources}]

    async def get_{resource}(self, {resource}_id: int) -> {Resource}Response:
        """Get {resource} by ID."""
        {resource} = await self.repository.get_by_id({resource}_id)

        if not {resource}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{Resource} with id {{resource}_id} not found"
            )

        return {Resource}Response.model_validate({resource})

    async def create_{resource}(
        self,
        {resource}_data: {Resource}Create
    ) -> {Resource}Response:
        """Create a new {resource}."""
        {resource} = await self.repository.create({resource}_data)
        return {Resource}Response.model_validate({resource})

    async def update_{resource}(
        self,
        {resource}_id: int,
        {resource}_data: {Resource}Update
    ) -> {Resource}Response:
        """Update a {resource}."""
        existing_{resource} = await self.repository.get_by_id({resource}_id)

        if not existing_{resource}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{Resource} with id {{resource}_id} not found"
            )

        updated_{resource} = await self.repository.update({resource}_id, {resource}_data)

        if not updated_{resource}:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update {resource}"
            )

        return {Resource}Response.model_validate(updated_{resource})

    async def delete_{resource}(self, {resource}_id: int) -> None:
        """Delete a {resource}."""
        existing_{resource} = await self.repository.get_by_id({resource}_id)

        if not existing_{resource}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{Resource} with id {{resource}_id} not found"
            )

        success = await self.repository.delete({resource}_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete {resource}"
            )


# ============================================================================
# 5. DEPENDENCIES (app/api/dependencies.py)
# ============================================================================

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.{resource}_repository import {Resource}Repository
from app.services.{resource}_service import {Resource}Service

def get_{resource}_repository(db: AsyncSession = Depends(get_db)) -> {Resource}Repository:
    return {Resource}Repository(db)

def get_{resource}_service(
    repository: {Resource}Repository = Depends(get_{resource}_repository)
) -> {Resource}Service:
    return {Resource}Service(repository)


# ============================================================================
# 6. ROUTER/ENDPOINTS (app/api/v1/endpoints/{resources}.py)
# ============================================================================

from fastapi import APIRouter, Depends, status, Query
from typing import List
from app.api.dependencies import get_{resource}_service
from app.schemas.{resource} import {Resource}Create, {Resource}Update, {Resource}Response
from app.services.{resource}_service import {Resource}Service

router = APIRouter(
    prefix="/{resources}",
    tags=["{resources}"],
    responses={{404: {{"description": "Not found"}}}}
)

@router.get("/", response_model=List[{Resource}Response])
async def list_{resources}(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    service: {Resource}Service = Depends(get_{resource}_service)
):
    """
    List all {resources} with pagination.
    """
    return await service.list_{resources}(skip, limit)

@router.post("/", response_model={Resource}Response, status_code=status.HTTP_201_CREATED)
async def create_{resource}(
    {resource}_data: {Resource}Create,
    service: {Resource}Service = Depends(get_{resource}_service)
):
    """
    Create a new {resource}.
    """
    return await service.create_{resource}({resource}_data)

@router.get("/{{resource}_id}}", response_model={Resource}Response)
async def get_{resource}(
    {resource}_id: int,
    service: {Resource}Service = Depends(get_{resource}_service)
):
    """
    Get a specific {resource} by ID.
    """
    return await service.get_{resource}({resource}_id)

@router.put("/{{resource}_id}}", response_model={Resource}Response)
async def update_{resource}(
    {resource}_id: int,
    {resource}_data: {Resource}Update,
    service: {Resource}Service = Depends(get_{resource}_service)
):
    """
    Update a {resource}.
    """
    return await service.update_{resource}({resource}_id, {resource}_data)

@router.delete("/{{resource}_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{resource}(
    {resource}_id: int,
    service: {Resource}Service = Depends(get_{resource}_service)
):
    """
    Delete a {resource}.
    """
    await service.delete_{resource}({resource}_id)
    return None


# ============================================================================
# 7. REGISTER ROUTER (app/api/v1/router.py)
# ============================================================================

# Add this line to app/api/v1/router.py:
# from app.api.v1.endpoints import {resources}
# api_router.include_router({resources}.router)


# ============================================================================
# 8. TESTS (tests/test_{resources}.py)
# ============================================================================

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_{resource}(async_client: AsyncClient):
    ""Test creating a {resource}.""
    {resource}_data = {{
        "name": "Test {Resource}",
        "description": "This is a test {resource}",
        "is_active": True
    }}

    response = await async_client.post(
        "/api/v1/{resources}/",
        json={resource}_data
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == {resource}_data["name"]
    assert "id" in data

@pytest.mark.asyncio
async def test_list_{resources}(async_client: AsyncClient):
    ""Test listing {resources}.""
    response = await async_client.get("/api/v1/{resources}/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_{resource}(async_client: AsyncClient, sample_{resource}):
    ""Test getting a {resource} by ID.""
    response = await async_client.get(f"/api/v1/{resources}/{{sample_{resource}.id}}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_{resource}.id

@pytest.mark.asyncio
async def test_update_{resource}(async_client: AsyncClient, sample_{resource}):
    ""Test updating a {resource}.""
    update_data = {{"name": "Updated Name"}}

    response = await async_client.put(
        f"/api/v1/{resources}/{{sample_{resource}.id}}",
        json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]

@pytest.mark.asyncio
async def test_delete_{resource}(async_client: AsyncClient, sample_{resource}):
    ""Test deleting a {resource}.""
    response = await async_client.delete(
        f"/api/v1/{resources}/{{sample_{resource}.id}}"
    )

    assert response.status_code == 204


# ============================================================================
# USAGE INSTRUCTIONS
# ============================================================================

"""
To use this template:

1. Replace all instances of:
   - {Resource} with your capitalized singular name (e.g., Product)
   - {resource} with your lowercase singular name (e.g., product)
   - {resources} with your lowercase plural name (e.g., products)

2. Create the files in the appropriate directories:
   - app/models/{resource}.py
   - app/schemas/{resource}.py
   - app/repositories/{resource}_repository.py
   - app/services/{resource}_service.py
   - app/api/v1/endpoints/{resources}.py
   - tests/test_{resources}.py

3. Add dependencies to app/api/dependencies.py

4. Register the router in app/api/v1/router.py

5. Create database migration:
   alembic revision --autogenerate -m "Add {resources} table"
   alembic upgrade head

6. Run tests:
   pytest tests/test_{resources}.py

7. Access your API at:
   - POST   /api/v1/{resources}/       - Create
   - GET    /api/v1/{resources}/       - List
   - GET    /api/v1/{resources}/{{id}}   - Get
   - PUT    /api/v1/{resources}/{{id}}   - Update
   - DELETE /api/v1/{resources}/{{id}}   - Delete
"""
