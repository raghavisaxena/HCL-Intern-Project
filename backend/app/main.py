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
from loguru import logger

from app.core.config import settings
from app.core.logging_config import configure_logging
from app.api.routes import health

# Set up logging before anything else runs
configure_logging()

app = FastAPI(
    title=settings.app_name,
    description="AI-Powered IT Incident Ticket Classification & Resolution Assistant",
    version="0.1.0",
)

# Register route modules.
# As we add more routers (tickets, classification, etc.) in later phases,
# they get included the same way — one line each, right here.
app.include_router(health.router, prefix="/api")


@app.on_event("startup")
async def on_startup():
    logger.info(f"🚀 {settings.app_name} starting up in '{settings.app_env}' mode")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("👋 Application shutting down")


@app.get("/", tags=["Root"])
async def root():
    """Simple root endpoint so visiting the base URL isn't a 404."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
    }