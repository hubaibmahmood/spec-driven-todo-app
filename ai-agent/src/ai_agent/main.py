"""FastAPI application entry point for AI Agent service."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AI Agent - Chat Persistence Service",
    description="Manages conversation history and message persistence for AI chat",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "AI Agent - Chat Persistence Service", "version": "0.1.0"}


# Register routers
from ai_agent.api import chat, health, history

app.include_router(health.router)
app.include_router(chat.router, prefix="/api")
app.include_router(history.router, prefix="/api")
