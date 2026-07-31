"""
Health check endpoint.

Why this matters in production:
- Azure App Service / load balancers ping this endpoint to know if
  the container is alive and ready to receive traffic.
- It's also our first smoke test today: if this responds, FastAPI,
  config loading, and logging are all working correctly together.
"""

from fastapi import APIRouter
from loguru import logger

from app.core.config import settings

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Returns basic service status. Deliberately lightweight and fast —
    health checks should never do heavy work (like pinging the DB or
    loading the LLM) on every single call.
    """
    logger.debug("Health check pinged")
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "environment": settings.app_env,
    }