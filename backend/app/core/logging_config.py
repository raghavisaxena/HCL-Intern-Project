"""
Application-wide logging configuration using loguru.

Why loguru instead of the standard `logging` module?
- Sensible defaults out of the box (colored console output, timestamps)
- One-line setup instead of dozens of lines of boilerplate
- Easy to later add file rotation, JSON output, or shipping to
  Azure Monitor / Application Insights without changing call sites.

Usage elsewhere in the app:
    from loguru import logger
    logger.info("Ticket classified as Network/VPN")
    logger.error("Failed to load embedding model")
"""

import sys
from loguru import logger

from app.core.config import settings


def configure_logging() -> None:
    """
    Configures loguru's global logger. Call this once, at application
    startup (we do this in main.py).
    """
    # Remove the default handler so we don't get duplicate log lines
    logger.remove()

    # Console handler: human-readable, colored, level depends on env
    log_level = "DEBUG" if settings.debug else "INFO"

    logger.add(
        sys.stdout,
        level=log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
            "- <level>{message}</level>"
        ),
        colorize=True,
    )

    # File handler: rotates daily, keeps 7 days of history.
    # Useful for debugging issues after the fact, even locally.
    logger.add(
        "logs/app.log",
        level="INFO",
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )

    logger.info(f"Logging configured | env={settings.app_env} | level={log_level}")