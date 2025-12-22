"""FastAPI application initialization and configuration."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError

from src.config import settings
from src.api.routers import health, tasks
from src.database.connection import engine
from src.api.schemas.error import ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events.
    """
    # Startup: Test database connection
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("Database connection successful!")
    except Exception as e:
        print(f"WARNING: Database connection failed: {e}")
        print("API will start but database operations will fail")
    
    yield
    
    # Shutdown: Close database connections
    await engine.dispose()
    print("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="RESTful API for todo application with session-based authentication",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Accept", "Content-Type", "Authorization", "X-Timezone"],
    expose_headers=["Content-Type", "Retry-After"],
    max_age=600,
)


# Error Handlers

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors (422)."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"] if loc != "body"),
            "message": error["msg"],
            "code": error["type"],
            "value": error.get("input")
        })
    
    error_response = ErrorResponse(
        type="validation_error",
        title="Request validation failed",
        status=422,
        detail="One or more validation errors occurred",
        instance=str(request.url.path),
        errors=errors
    )

    return JSONResponse(
        status_code=422,
        content=error_response.model_dump()
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_error_handler(
    request: Request,
    exc: ValidationError
) -> JSONResponse:
    """Handle Pydantic ValidationError."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "code": error["type"]
        })
    
    error_response = ErrorResponse(
        type="validation_error",
        title="Validation failed",
        status=status.HTTP_400_BAD_REQUEST,
        detail="Input validation failed",
        instance=str(request.url.path),
        errors=errors
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response.model_dump()
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(
    request: Request,
    exc: IntegrityError
) -> JSONResponse:
    """Handle database integrity constraint violations."""
    error_response = ErrorResponse(
        type="integrity_error",
        title="Data integrity violation",
        status=status.HTTP_409_CONFLICT,
        detail="The operation violates a database constraint",
        instance=str(request.url.path)
    )
    
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error_response.model_dump()
    )


@app.exception_handler(OperationalError)
async def operational_error_handler(
    request: Request,
    exc: OperationalError
) -> JSONResponse:
    """Handle database operational errors."""
    error_response = ErrorResponse(
        type="database_error",
        title="Database operation failed",
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="A database error occurred. Please try again later.",
        instance=str(request.url.path)
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """Handle general SQLAlchemy errors."""
    import traceback
    # Log the full exception in development
    print(f"SQLAlchemy Error: {exc}")
    print(f"Traceback: {traceback.format_exc()}")

    error_response = ErrorResponse(
        type="database_error",
        title="Database error",
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"An unexpected database error occurred: {str(exc)}" if settings.is_development else "An unexpected database error occurred",
        instance=str(request.url.path)
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )


@app.exception_handler(500)
async def internal_server_error_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle internal server errors."""
    import traceback
    # Log the full exception in development
    print(f"Internal Server Error: {exc}")
    print(f"Traceback: {traceback.format_exc()}")

    error_response = ErrorResponse(
        type="internal_error",
        title="Internal server error",
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"An unexpected error occurred: {str(exc)}" if settings.is_development else "An unexpected error occurred",
        instance=str(request.url.path)
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )


# Register routers
app.include_router(health.router)
app.include_router(tasks.router)


def main():
    """Entry point for running the application."""
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development
    )


if __name__ == "__main__":
    main()