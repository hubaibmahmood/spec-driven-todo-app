---
allowed-tools: Read, Write, Edit, Glob, Grep
description: Scaffold a new FastAPI CRUD endpoint with clean architecture
---

# Create New FastAPI Endpoint

## Your Task

Guide the user through creating a new CRUD endpoint following clean architecture.

### Step 1: Gather Requirements

Ask the user:
1. **Resource name** (singular, e.g., "Product", "Category")
2. **Fields** (name, type, constraints)
3. **Relationships** (if any)

### Step 2: Generate Files

Based on requirements, create:

1. **Model** (`app/models/{resource}.py`):
   - SQLAlchemy model with fields
   - Relationships
   - Constraints

2. **Schemas** (`app/schemas/{resource}.py`):
   - Base schema
   - Create schema (input)
   - Update schema (partial)
   - Response schema (output)

3. **Repository** (`app/repositories/{resource}_repository.py`):
   - CRUD methods
   - Custom queries if needed

4. **Service** (`app/services/{resource}_service.py`):
   - Business logic
   - Error handling
   - Validation

5. **Router** (`app/api/v1/endpoints/{resources}.py`):
   - List endpoint (GET)
   - Create endpoint (POST)
   - Get by ID (GET)
   - Update (PUT)
   - Delete (DELETE)

6. **Tests** (`tests/test_{resources}.py`):
   - Test all CRUD operations
   - Test validation
   - Test error cases

### Step 3: Integration

1. Add dependencies to `app/api/dependencies.py`
2. Register router in `app/api/v1/router.py`
3. Create migration: `alembic revision --autogenerate -m "Add {resources} table"`

### Step 4: Verification

1. Run migration: `alembic upgrade head`
2. Run tests: `pytest tests/test_{resources}.py`
3. Check types: `mypy app/`
4. Format code: `ruff format app/`

### Template Reference

Use the endpoint template at:
`.claude/skills/fastapi-patterns/templates/endpoint-template.py`

Follow clean architecture:
- API layer (routers) → Service layer (business logic) → Repository layer (database)

Ready to create your endpoint? Tell me the resource name and fields!
