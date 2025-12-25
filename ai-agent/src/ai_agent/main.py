"""FastAPI application entry point for AI Agent service."""

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

# Set specific loggers to INFO to see our debug logs
logging.getLogger("ai_agent").setLevel(logging.INFO)
logging.getLogger("ai_agent.agent.context_manager").setLevel(logging.INFO)
logging.getLogger("ai_agent.api.chat").setLevel(logging.INFO)

# Create FastAPI app
app = FastAPI(
    title="AI Agent - Chat Persistence Service",
    description="Manages conversation history and message persistence for AI chat",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Timezone"],
    expose_headers=["Content-Type"],
    max_age=600,
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
