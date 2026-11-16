"""
FastAPI application entrypoint.

This file:
1. Creates the FastAPI app instance
2. Configures logging
3. Registers API routes
4. Will later register the Supervisor Agent's orchestration endpoint (Phase 11)

Run locally with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.core.logging_config import configure_logging
from app.api.routes import health, tickets

# Set up logging before anything else runs
configure_logging()

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 {settings.app_name} starting up in '{settings.app_env}' mode")
    yield
    logger.info("👋 Application shutting down")


app = FastAPI(
    title=settings.app_name,
    description="AI-Powered IT Incident Ticket Classification & Resolution Assistant",
    version="0.1.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules.
app.include_router(health.router, prefix="/api")
app.include_router(tickets.router, prefix="/api")


@app.get("/", tags=["Root"])
async def root():
    """Simple root endpoint so visiting the base URL isn't a 404."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
    }